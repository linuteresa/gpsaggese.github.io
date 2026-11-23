"""Network-disabled transfer and accounting regressions; no API credentials."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from m3_offline_common import agent, deny_network

from concurrent.futures import ProcessPoolExecutor
import json
import sqlite3
import threading
import pytest
from minisweagent.exceptions import FormatError
from m3_runtime.budget import Budget, BudgetBusy, BudgetExhausted
from m3_runtime.policies import H4, H5, AccountingError, NANO, normalize_usage, price_usage
from m3_runtime.transfer import TransferModel, fork_transfer
from m3_runtime.transport import make_guarded_query
from m3_runtime.source import RecordedStore
from build_m3_taxonomy import build
from preflight_m3_offline import preflight, mock_reply


def _compete(args):
    path, model=args
    b=Budget(path,NANO)
    try:
        return b.reserve("shared",model,"a"*64)
    except (BudgetBusy,BudgetExhausted):
        return None


def test_mixed_models_share_atomic_process_cap(tmp_path):
    path=tmp_path/"budget.sqlite"
    b=Budget(path,NANO)
    with ProcessPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(_compete,[(path,p.model) for p in (H4,H5)*8]))
    summary=b.summary()
    assert summary["within_cap"] and summary["accounted_plus_reserved_usd"] <= 1
    assert sum(r is not None for r in results) in (2,3)
    assert summary["accounted_plus_reserved_usd"] in (.99,.995)


@pytest.mark.parametrize("policy",[H4,H5])
def test_maximum_cache_and_reasoning_accounting(policy):
    assert policy.maximum == (330_000_000 if policy == H4 else 665_000_000)
    assert price_usage(policy.model,{"input_tokens":0,"cache_creation_input_tokens":policy.max_input,
        "output_tokens":policy.max_output}) == policy.maximum
    raw={"input_tokens":100,"cache_read_input_tokens":600,"cache_creation_input_tokens":300,"output_tokens":200}
    inclusive={"prompt_tokens":1000,"completion_tokens":200,
        "prompt_tokens_details":{"cached_tokens":600,"cache_creation_token_details":{"ephemeral_5m_input_tokens":300}},
        "completion_tokens_details":{"reasoning_tokens":190}}
    assert price_usage(policy.model,raw) == price_usage(policy.model,inclusive)
    assert price_usage(policy.model,raw) == (1_535_000 if policy == H4 else 153_500)


def test_long_context_boundary_and_target_price():
    assert price_usage(H5.model,{"prompt_tokens":100000,"completion_tokens":100}) == 10_050_000
    assert price_usage(H5.model,{"prompt_tokens":100001,"completion_tokens":100}) == 50_250_500
    assert price_usage(H4.model,{"prompt_tokens":1000,"completion_tokens":100}) == 10*price_usage(H5.model,{"prompt_tokens":1000,"completion_tokens":100})


@pytest.mark.parametrize("usage",[
    {"prompt_tokens":1},
    {"prompt_tokens":1,"completion_tokens":1,"service_tier":"priority"},
    {"prompt_tokens":1,"completion_tokens":1,"inference_geo":"us"},
    {"prompt_tokens":True,"completion_tokens":1},
    {"prompt_tokens":1,"completion_tokens":1,"cache_read_input_tokens":2},
    {"prompt_tokens":1,"completion_tokens":1,"cache_creation":{"ephemeral_1h_input_tokens":1}},
    {"prompt_tokens":2,"completion_tokens":1,"cache_creation_input_tokens":1,
        "prompt_tokens_details":{"cache_creation_token_details":{"ephemeral_5m_input_tokens":2}}},
    {"prompt_tokens":1,"completion_tokens":1,"completion_tokens_details":{"reasoning_tokens":2}},
    {"prompt_tokens":200001,"completion_tokens":1},
    {"prompt_tokens":1,"completion_tokens":16001},
    {"prompt_tokens":1,"completion_tokens":1,"prompt_tokens_details":[1]},
])
def test_unsupported_or_conflicting_usage_fails_closed(usage):
    with pytest.raises(AccountingError):
        normalize_usage(usage,H4)


def test_wrong_actual_model_is_not_repriced_as_requested_model(tmp_path):
    b=Budget(tmp_path/"b.sqlite",NANO)
    token=b.reserve("job",H4.model,"a"*64)
    with pytest.raises(AccountingError):
        b.settle(token,usage={"prompt_tokens":1000,"completion_tokens":100},response_model=H5.response_models[0])
    assert b.summary()["accounted_plus_reserved_usd"] == .33
    with pytest.raises(AccountingError):
        b.settle(token,rejection_status=400)


def test_unknown_spend_survives_restart_and_settings_are_frozen(tmp_path):
    path=tmp_path/"b.sqlite"
    b=Budget(path,H4.maximum)
    token=b.reserve("job",H4.model,"b"*64)
    assert b.settle(token,error_type="TimeoutError") == H4.maximum
    reopened=Budget(path,H4.maximum)
    with pytest.raises(BudgetExhausted):reopened.reserve("job2",H4.model,"c"*64)
    with pytest.raises(AccountingError):Budget(path,NANO)
    with reopened.connection() as db:
        db.execute("update budget_settings set registry='tampered'")
    with pytest.raises(AccountingError):Budget(path,H4.maximum)


def test_no_missing_usage_or_legacy_ledger_accepted(tmp_path):
    b=Budget(tmp_path/"new.sqlite",NANO)
    token=b.reserve("job",H4.model,"a"*64)
    with pytest.raises(AccountingError):b.settle(token)
    assert b.summary()["accounted_plus_reserved_usd"] == .33
    with sqlite3.connect(tmp_path/"old.sqlite") as db:db.execute("create table old_calls (id text)")
    with pytest.raises(AccountingError):Budget(tmp_path/"old.sqlite",NANO)
    with pytest.raises(AccountingError):b.reserve("job","anthropic/unknown","a"*64)


def model():
    return TransferModel(model_name=H4.model,model_kwargs=H4.sampling(),cost_tracking="ignore_errors",set_cache_control="default_end")


def test_reservation_response_identity_and_format_error_charge(tmp_path):
    b=Budget(tmp_path/"b.sqlite",NANO)
    def fake(**kwargs):
        assert b.summary()["accounted_plus_reserved_usd"] == .33
        assert kwargs["model"] == H4.model and kwargs["drop_params"] is False
        assert kwargs["thinking"] == {"type":"enabled","budget_tokens":4096}
        assert kwargs["num_retries"] == kwargs["max_retries"] == 0
        return mock_reply(H4.model,"bad format")
    query=make_guarded_query(b,H4.model,"format",threading.Event(),completion=fake)
    with pytest.raises(FormatError) as exc:query(model(),[{"role":"user","content":"test"}])
    assert exc.value.messages[0]["extra"]["cost"] == .0015
    with b.connection() as db:
        row=dict(db.execute("select * from requests").fetchone())
    assert row["response_model"] == H4.response_models[0] and row["status"] == "settled"


@pytest.mark.parametrize("failure",["timeout","wrong_model","missing_usage"])
def test_transport_stops_without_retry_and_retains_liability(tmp_path,failure):
    b=Budget(tmp_path/"b.sqlite",NANO); stopped=threading.Event(); calls=[]
    def fake(**kwargs):
        calls.append(kwargs)
        if failure == "timeout":raise TimeoutError("must not be copied to logs")
        response=mock_reply(H5.model if failure == "wrong_model" else H4.model,"invalid")
        if failure == "missing_usage":response.usage=None
        return response
    query=make_guarded_query(b,H4.model,"failed",stopped,completion=fake)
    with pytest.raises(RuntimeError):query(model(),[{"role":"user","content":"x"}])
    assert stopped.is_set() and b.summary()["accounted_plus_reserved_usd"] == .33
    with pytest.raises(RuntimeError):query(model(),[{"role":"user","content":"x"}])
    assert len(calls) == 1


def test_pre_dispatch_guards_and_free_rejection(tmp_path):
    b=Budget(tmp_path/"b.sqlite",NANO)
    query=make_guarded_query(b,H4.model,"guard",threading.Event(),completion=lambda **kw:pytest.fail("dispatched"))
    m=model();m.config.model_kwargs["thinking"]={"type":"adaptive"}
    with pytest.raises(ValueError):query(m,[{"role":"user","content":"x"}])
    with pytest.raises(ValueError):query(model(),[{"role":"user","content":"x"*200000}])
    with pytest.raises(ValueError):query(model(),[{"role":"user","content":[{"type":"image_url","image_url":"x"}]}])
    assert b.summary()["requests"] == 0
    class Rejected(Exception):status_code=429
    def reject(**kwargs):raise Rejected()
    stop=threading.Event();query=make_guarded_query(b,H4.model,"rejected",stop,completion=reject)
    with pytest.raises(RuntimeError):query(model(),[{"role":"user","content":"x"}])
    assert stop.is_set() and b.summary()["accounted_plus_reserved_usd"] == 0


def test_read_only_source_does_not_create_store(tmp_path):
    with pytest.raises(sqlite3.OperationalError):RecordedStore(tmp_path/"absent")
    assert not (tmp_path/"absent").exists()


def test_complete_taxonomy_and_all_transfer_paths():
    summary=build()
    report=preflight()
    assert summary["decisions"] == 48 and summary["failed_dialogues"] == 7 and summary["distinct_tasks"] == 4
    assert summary["label_counts"] == {"clock_win_lost":5,"board_revisit":4,"false_attack_or_reply_claim":8,"actual_rook_loss":2}
    assert summary["resolved_harmful_reply_effects"] == 3 and summary["uncertain_interpretations"] == 8
    assert report["restore_checks"] == 192 and report["mock_full_continuations"] == 14
    assert report["api_calls"] == 0 and report["source_files_unchanged"]
