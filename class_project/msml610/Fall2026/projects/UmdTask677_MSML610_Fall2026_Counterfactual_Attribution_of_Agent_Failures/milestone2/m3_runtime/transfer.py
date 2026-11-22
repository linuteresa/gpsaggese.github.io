"""Explicit model-policy intervention, with live inference disabled by default."""
from copy import deepcopy
import hashlib
import json

import caaf_agent as agent
import caaf_chess as board
import caaf_store as base

from .policies import canonical, policy_for


class LiveExecutionDisabled(RuntimeError):
    pass


class TransferModel(agent.CaafModel):
    guarded_query = None

    def query(self, messages, **kwargs):
        if self.guarded_query is None:
            raise LiveExecutionDisabled("No transport is installed; this offline preparation cannot call a provider")
        return self.guarded_query(self, messages, **kwargs)


def visible_hash(messages):
    return hashlib.sha256(canonical(agent.api_messages(messages))).hexdigest()


def fork_transfer(store, snapshot_id, *, config, target_model, job_id,
                  arm="redecide_reply", source_branch_id=None):
    policy = policy_for(target_model)
    if arm not in {"keep_original_reply", "redecide_reply"} or not job_id:
        raise ValueError("An explicit arm and job identity are required")
    snap = store.snapshot(snapshot_id)
    ctx = json.loads(store.get_blob("context", snap["context_hash"]))
    state = store.get_blob("env", snap["env_hash"])
    if ctx["messages"][-1]["role"] == "exit" or ctx["counters"]["n_calls"] >= ctx["counters"]["step_limit"]:
        raise ValueError("Cannot fork a terminal or exhausted decision boundary")
    env = board.ChessEnv(json.loads(state)["start_fen"])
    env.restore(state, snap["env_hash"])
    if env.game["status"] != "ongoing":
        raise ValueError("Cannot fork a finished game")
    overrides = {}
    forced_sha = None
    if arm == "keep_original_reply":
        if not source_branch_id:
            raise ValueError("The keep arm requires the original recorded branch")
        tape = store.read_tape(source_branch_id)
        if not base.verify_tape(tape):
            raise ValueError("Original tape does not verify")
        step = ctx["counters"]["n_calls"] + 1
        matches = [e for e in tape if e["kind"] == "model_call" and e["step"] == step]
        if len(matches) != 1 or matches[0]["request"]["input_hash"] != visible_hash(ctx["messages"]):
            raise ValueError("Original reply is not from this API-visible prefix")
        parents = [s for s in store.snapshots(source_branch_id) if s["step"] == step-1]
        if not parents or parents[0]["env_hash"] != snap["env_hash"]:
            raise ValueError("Original reply is not from this board state")
        text = matches[0]["response"]["content"]
        overrides[step] = {"content": text, "source": "forced"}
        forced_sha = hashlib.sha256(text.encode()).hexdigest()
    model_cfg = deepcopy(config["model"])
    model_cfg.pop("budget", None)
    model_cfg["model_name"] = policy.model
    model_cfg["model_kwargs"] = policy.sampling()  # Replace; never merge the old policy.
    extra = {k:model_cfg[k] for k in ("observation_template", "format_error_template", "set_cache_control") if k in model_cfg}
    model = TransferModel(model_name=policy.model, model_kwargs=policy.sampling(), cost_tracking="ignore_errors", **extra)
    intervention = {"type":"cross_model_policy", "schema":"caaf.m3.transfer/1", "job_id":job_id,
        "arm":arm, "source_model":ctx["model"]["name"], "source_sampling":ctx["model"]["sampling"],
        "target_model":policy.model, "target_sampling":policy.sampling(), "policy_sha256":policy.fingerprint,
        "parent_context_sha256":snap["context_hash"], "parent_env_sha256":snap["env_hash"],
        "visible_prefix_sha256":visible_hash(ctx["messages"]), "source_branch_id":source_branch_id,
        "forced_reply_sha256":forced_sha}
    bid = store.new_branch(snap["run_id"], parent_snapshot_id=snapshot_id,
                           fork_step=snap["step"], intervention=intervention)
    harness = {k:v for k,v in ctx["harness"].items() if k != "mini_swe_agent"}
    recording = agent.RecordingAgent(model, env, store=store, run_id=snap["run_id"],
        branch_id=bid, overrides=overrides, harness=harness, **ctx["agent_config"])
    recording.restore_context(ctx)
    restored = recording.context()
    for key in set(ctx) | set(restored):
        if key != "model" and canonical(restored.get(key)) != canonical(ctx.get(key)):
            recording.tape.close()
            raise RuntimeError(f"Non-policy checkpoint field changed: {key}")
    if recording.model.config.model_name != policy.model or recording.sampling() != policy.sampling():
        raise RuntimeError("Requested target policy did not survive restoration")
    if visible_hash(recording.messages) != intervention["visible_prefix_sha256"] or base.sha256(env.state()) != snap["env_hash"]:
        raise RuntimeError("Transfer changed the saved prefix or board")
    recording.last_snapshot_id = snapshot_id
    initial = recording.take_snapshot()
    return agent.Branch(store, recording, env, snap["run_id"], bid,
        {"parent":snapshot_id, "snapshot0":initial["id"], "env_verified":True,
         "visible_context_verified":True, "model_change_explicit":True, "intervention":intervention})
