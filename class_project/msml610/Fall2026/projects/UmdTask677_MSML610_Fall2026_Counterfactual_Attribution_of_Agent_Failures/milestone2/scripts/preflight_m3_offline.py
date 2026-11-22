"""Check every prepared transfer using temporary stores and mocked inference."""
from m3_offline_common import ROOT, OUT, agent
import hashlib
import json
from pathlib import Path
import tempfile
import threading

from litellm import ModelResponse
from m2_runtime.compact_store import CompactStore, seed_pilot_store
from m3_runtime.budget import Budget
from m3_runtime.policies import H4, H5, NANO, registry_document
from m3_runtime.transfer import fork_transfer, visible_hash, LiveExecutionDisabled
from m3_runtime.transport import make_guarded_query


def mock_reply(model, content):
    return ModelResponse(model=model.removeprefix("anthropic/"),
        choices=[{"index":0,"message":{"role":"assistant","content":content},"finish_reason":"stop"}],
        usage={"prompt_tokens":1000,"completion_tokens":100,"total_tokens":1100})


def preflight():
    OUT.mkdir(parents=True, exist_ok=True)
    taxonomy = json.loads((OUT/"taxonomy.json").read_text())
    evidence = taxonomy["summary"]["source_files_sha256"]
    for name, digest in evidence.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest
    manifest = json.loads((ROOT/"experiments/m2_direct_v2/experiment_manifest.json").read_text())
    cases = manifest["decisions"]
    config = agent.load_config("chess_haiku_think.yaml")
    checks, executions = [], []
    with tempfile.TemporaryDirectory(prefix="chess-m3-offline-") as temp:
        temp = Path(temp)
        seed_pilot_store(ROOT/"inputs/m1_original/runs/m1_think", temp/"store", sorted({d["branch_id"] for d in cases}))
        store = CompactStore(temp/"store")
        for d in cases:
            for p in (H5,H4):
                for arm in ("keep_original_reply", "redecide_reply"):
                    b = fork_transfer(store,d["before_checkpoint"],config=config,target_model=p.model,
                        job_id=d["decision_id"]+":"+p.model+":"+arm,arm=arm,source_branch_id=d["branch_id"])
                    assert b.agent.model.config.model_name == p.model
                    parent=store.snapshot(d["before_checkpoint"])
                    original_ctx=json.loads(store.get_blob("context",parent["context_hash"]))
                    assert visible_hash(b.agent.messages) == visible_hash(original_ctx["messages"])
                    assert b.agent.n_calls == int(d["step"])-1
                    try:
                        b.agent.model.query(b.agent.messages)
                    except LiveExecutionDisabled:
                        pass
                    else:
                        raise AssertionError("Unconfigured query must fail closed")
                    checks.append({"decision_id":d["decision_id"],"model":p.model,"arm":arm,
                                   "prefix_board_and_nonmodel_context_verified":True,"live_transport_absent":True})
                    b.agent.tape.close()
        # Full recorded continuations are replayed through an injected mock.
        # The forced first reply must bypass that mock once; all later calls use H4.
        for bid in sorted({d["branch_id"] for d in cases}):
            ds = [d for d in cases if d["branch_id"] == bid]
            d = ds[0]
            original_tape = store.read_tape(bid)
            calls = {e["step"]:e["response"]["content"] for e in original_tape if e["kind"] == "model_call"}
            for arm in ("keep_original_reply", "redecide_reply"):
                b=fork_transfer(store,d["before_checkpoint"],config=config,target_model=H4.model,
                    job_id=bid+arm,arm=arm,source_branch_id=bid)
                ledger=Budget(temp/(bid+arm+".sqlite"),NANO)
                dispatched=[]

                def completion(**kw):
                    assert kw["model"] == H4.model
                    assert kw["thinking"] == {"type":"enabled","budget_tokens":4096}
                    assert kw["drop_params"] is False and kw["num_retries"] == kw["max_retries"] == 0
                    assert ledger.summary()["accounted_plus_reserved_usd"] >= .33
                    dispatched.append(b.agent.n_calls)
                    return mock_reply(H4.model,calls[b.agent.n_calls])

                b.agent.model.guarded_query=make_guarded_query(ledger,H4.model,bid+arm,threading.Event(),completion=completion)
                outcome=agent.run_to_end(b)
                expected=store.snapshot(ds[-1]["after_checkpoint"])
                actual=store.snapshot(b.agent.last_snapshot_id)
                assert actual["env_hash"] == expected["env_hash"]
                actual_ctx=json.loads(store.get_blob("context",actual["context_hash"]))
                expected_ctx=json.loads(store.get_blob("context",expected["context_hash"]))
                assert visible_hash(actual_ctx["messages"]) == visible_hash(expected_ctx["messages"])
                expected_calls=list(range(2 if arm == "keep_original_reply" else 1,len(ds)+1))
                assert dispatched == expected_calls
                assert ledger.summary()["accounted_plus_reserved_usd"] == round(len(dispatched)*.0015, 9)
                tape=store.read_tape(b.branch_id)
                model_calls=[e for e in tape if e["kind"] == "model_call"]
                assert sum(e["response"]["source"] == "forced" for e in model_calls) == (arm == "keep_original_reply")
                assert all(e["request"]["model"] == H4.model for e in model_calls)
                executions.append({"branch_id":bid,"arm":arm,"mock_dispatches":len(dispatched),
                    "exact_final_board_and_visible_history":True,"forced_reply_exactly_once":arm == "keep_original_reply",
                    "target_request_and_response_identity_verified":True,"simulated_accounted_usd":ledger.summary()["accounted_plus_reserved_usd"],
                    "outcome":outcome["status"]})
                b.agent.tape.close()
        store.db.close()
    for name, digest in evidence.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    report={"schema":"caaf.m3.offline_preflight/1","network_blocked":True,"credential_loader_used":False,
        "api_calls":0,"api_cost_usd":0,"paid_execution_authorized":False,"source_files_unchanged":True,
        "restore_checks":len(checks),"mock_full_continuations":len(executions),
        "mock_dispatches":sum(e["mock_dispatches"] for e in executions),
        "simulated_costs_are_not_actual_spend":True,"restorations":checks,"mock_executions":executions}
    (OUT/"preflight.json").write_text(json.dumps(report,indent=2)+"\n")
    (OUT/"model_policies.json").write_text(json.dumps(registry_document(),indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in {"restorations","mock_executions"}}))
    return report


if __name__ == "__main__":
    preflight()
