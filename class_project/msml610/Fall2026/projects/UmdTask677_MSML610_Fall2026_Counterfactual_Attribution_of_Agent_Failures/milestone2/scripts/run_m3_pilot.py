#!/usr/bin/env python3
"""Run the frozen M3 live pilot stage.

Two modes:

  --preflight   (default) Fork every job in the manifest, verify the restored
                prefix, board and target policy, then close it without
                dispatching. Zero API calls, no credentials read. Proves
                everything up to the provider boundary.

  --live        Dispatch for real. Requires:
                  * ANTHROPIC_API_KEY in the environment (this script never
                    reads a key file, never prints a key, never stores one)
                  * authorization.authorized_usd > 0 in the manifest
                Stops on the first transport failure. No retries.

Resume is automatic: completed job_ids in results.json are skipped.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from m3_offline_common import ROOT, agent  # noqa: E402  (installs the offline-safe import path)

from m2_runtime.compact_store import CompactStore, seed_pilot_store  # noqa: E402
from m3_runtime.budget import Budget, BudgetExhausted  # noqa: E402
from m3_runtime.policies import NANO, policy_for, registry_document  # noqa: E402
from m3_runtime.transfer import fork_transfer, visible_hash  # noqa: E402
from m3_runtime.transport import make_guarded_query  # noqa: E402

STAGE = ROOT / "experiments" / "m3_live_v1"
MANIFEST = STAGE / "experiment_manifest.json"
STORE = STAGE / "store"
LEDGER = STAGE / "ledger.sqlite"


def save(name: str, payload) -> None:
    STAGE.mkdir(parents=True, exist_ok=True)
    tmp = STAGE / (name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n")
    tmp.replace(STAGE / name)


def load_results() -> dict:
    p = STAGE / "results.json"
    if not p.exists():
        return {}
    return {r["job_id"]: r for r in json.loads(p.read_text())}


def seed_store_once(manifest) -> None:
    """Seed the writable store once, single-threaded. Workers open their own handle:
    one SQLite connection per job, as the M2 runner does."""
    branches = sorted({d["source_branch_id"] for d in manifest["decisions"]})
    if not STORE.exists():
        seed_pilot_store(ROOT / "inputs/m1_original/runs/m1_think", STORE, branches)


def verify_fork(branch, store, job, manifest_decision) -> dict:
    """Checks that hold identically in preflight and live mode."""
    parent = store.snapshot(job["before_checkpoint"])
    original = json.loads(store.get_blob("context", parent["context_hash"]))
    policy = policy_for(job["target_model"])
    facts = {
        "visible_prefix_preserved": visible_hash(branch.agent.messages) == visible_hash(original["messages"]),
        "step_counter_correct": branch.agent.n_calls == int(manifest_decision["step"]) - 1,
        "target_policy_installed": branch.agent.model.config.model_name == policy.model,
        "sampling_installed": branch.agent.sampling() == policy.sampling(),
    }
    if not all(facts.values()):
        raise RuntimeError(f"fork verification failed: {facts}")
    return facts


def main() -> int:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", default=True)
    mode.add_argument("--live", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0, help="run only the first N pending jobs")
    args = ap.parse_args()
    live = bool(args.live)

    if not MANIFEST.exists():
        print("no frozen manifest: run scripts/build_m3_live_manifest.py first", file=sys.stderr)
        return 1
    manifest = json.loads(MANIFEST.read_text())
    decisions = {d["decision_id"]: d for d in manifest["decisions"]}
    cap_usd = manifest["budget"]["ceiling_usd"]
    authorized = manifest["authorization"]["authorized_usd"]

    if live:
        if not authorized:
            print("manifest authorization.authorized_usd is 0: paid execution refused", file=sys.stderr)
            return 2
        if authorized > cap_usd:
            print("authorized_usd exceeds the declared ceiling", file=sys.stderr)
            return 2
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("ANTHROPIC_API_KEY is not set in the environment; refusing to run live",
                  file=sys.stderr)
            return 2
        import litellm  # imported only in live mode
        litellm.drop_params = False
        completion_fn = litellm.completion
    else:
        completion_fn = None

    done = load_results()
    pending = [j for j in manifest["jobs"] if j["job_id"] not in done]
    if args.limit:
        pending = pending[:args.limit]

    seed_store_once(manifest)
    stopped = threading.Event()
    budget = Budget(LEDGER, int(round(authorized * NANO))) if live else None
    started = time.monotonic()
    results = list(done.values())
    lock = threading.Lock()

    def run_job(job) -> dict:
        base = {"job_id": job["job_id"], "decision_id": job["decision_id"],
                "arm": job["arm"], "replicate": job["replicate"],
                "target_model": job["target_model"], "mode": "live" if live else "preflight"}
        branch = None
        store = CompactStore(STORE)
        config = agent.load_config("chess_haiku_think.yaml")
        config["model"].pop("budget", None)
        try:
            branch = fork_transfer(
                store, job["before_checkpoint"], config=config,
                target_model=job["target_model"], job_id=job["job_id"],
                arm=job["arm"], source_branch_id=job["source_branch_id"])
            facts = verify_fork(branch, store, job, decisions[job["decision_id"]])

            if not live:
                branch.agent.tape.close()
                store.finish_branch(branch.branch_id, "preflight_only", {"dispatched": False})
                return {**base, "status": "preflight_ok", "branch_id": branch.branch_id,
                        "verification": facts, "api_calls": 0}

            branch.agent.model.guarded_query = make_guarded_query(
                budget, job["target_model"], job["job_id"], stopped, completion=completion_fn)
            outcome = agent.run_to_end(branch)
            tape = store.read_tape(branch.branch_id)
            calls = [e for e in tape if e["kind"] == "model_call"]
            forced = sum(e["response"].get("source") == "forced" for e in calls)
            if job["arm"] == "keep_original_reply" and forced != 1:
                raise RuntimeError(f"keep arm forced the original reply {forced} times")
            if job["arm"] == "redecide_reply" and forced:
                raise RuntimeError("redecide arm must not force a reply")
            if not all(e["request"]["model"] == job["target_model"] for e in calls):
                raise RuntimeError("a call used a model other than the pinned target")
            return {**base, "status": "completed", "branch_id": branch.branch_id,
                    "verification": facts, "outcome": outcome,
                    "model_calls": len(calls), "forced_replies": forced}
        except BudgetExhausted:
            stopped.set()
            return {**base, "status": "budget_exhausted"}
        except BaseException as exc:
            stopped.set()
            if branch is not None:
                try:
                    branch.agent.tape.close()
                    store.finish_branch(branch.branch_id, "failed", {"error_type": type(exc).__name__})
                except BaseException:
                    pass
            # Only the exception type is persisted: messages can carry provider internals.
            return {**base, "status": "error", "error_type": type(exc).__name__,
                    "branch_id": branch.branch_id if branch else None}
        finally:
            try:
                store.db.close()
            except BaseException:
                pass

    def checkpoint() -> dict:
        summary = {
            "stage": manifest["stage"], "mode": "live" if live else "preflight",
            "jobs_total": len(manifest["jobs"]), "jobs_recorded": len(results),
            "preflight_ok": sum(r["status"] == "preflight_ok" for r in results),
            "completed": sum(r["status"] == "completed" for r in results),
            "errors": sum(r["status"] not in ("completed", "preflight_ok") for r in results),
            "elapsed_seconds": round(time.monotonic() - started),
            "budget": budget.summary() if budget else {"cap_usd": 0, "api_calls": 0},
            "model_registry": registry_document(),
        }
        save("results.json", sorted(results, key=lambda r: r["job_id"]))
        save("progress.json", summary)
        return summary

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(run_job, j) for j in pending]
        for fut in as_completed(futures):
            with lock:
                results.append(fut.result())
                summary = checkpoint()

    summary = checkpoint()
    print(json.dumps({k: v for k, v in summary.items() if k != "model_registry"}, indent=1))
    return 0 if summary["errors"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
