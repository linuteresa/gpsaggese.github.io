#!/usr/bin/env python3
"""Freeze the M3 live pilot stage manifest.

Writes experiments/m3_live_v1/experiment_manifest.json: the declared design that
handoff step 4 requires frozen BEFORE any outcome is collected. Pins the eight
selected decisions with their checkpoint and branch identities, the arms, the
sample counts, both model policies, the metrics, the multiplicity treatment, the
stopping rules and the spending ceiling.

Run once. Re-running refuses to overwrite a manifest that results already exist
for, so a design cannot be edited after outcomes are seen.

No model calls, no network, no credentials.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "m3_live_v1"
TAX = ROOT / "experiments" / "m3_offline_v1" / "taxonomy.json"
FORECAST = ROOT / "experiments" / "m3_plan_v1" / "cost_forecast.json"

TARGET = "anthropic/claude-haiku-4-5-20251001"
REFERENCE = "anthropic/claude-haiku-5-5"
ARMS = ("keep_original_reply", "redecide_reply")
PER_ARM = 10
CAP_USD = 15


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    target_path = OUT / "experiment_manifest.json"
    if (OUT / "results.json").exists():
        print("results.json exists: refusing to rewrite a frozen design", file=sys.stderr)
        return 1

    forecast = json.loads(FORECAST.read_text())
    tax = {d["decision_id"]: d for d in json.loads(TAX.read_text())["decisions"]}
    selected = forecast["selected_decisions"]

    decisions, jobs = [], []
    for did in selected:
        d = tax[did]
        stats = d["m2_primary_statistics"]
        decisions.append({
            "decision_id": did,
            "task_id": d["task_id"], "trial": d["trial"], "step": d["step"],
            "before_checkpoint": d["before_checkpoint"],
            "after_checkpoint": d["after_checkpoint"],
            "source_branch_id": d["branch_id"], "run_id": d["run_id"],
            "original_reply_sha256": d["reply_sha256"],
            "m2_repair_gain": stats["repair_gain"], "m2_holm_p": stats["holm_p"],
            "m2_keep": [stats["keep_wins"], stats["keep_n"]],
            "m2_redecide": [stats["redecide_wins"], stats["redecide_n"]],
            "causal_status": d["causal_status"],
            "selection_role": ("resolved_harmful" if d["causal_status"].startswith("resolved")
                               else "control_or_unresolved"),
        })
        for arm in ARMS:
            for rep in range(PER_ARM):
                jobs.append({
                    "job_id": f"{did}:{TARGET}:{arm}:{rep:02d}",
                    "decision_id": did, "arm": arm, "replicate": rep,
                    "target_model": TARGET,
                    "before_checkpoint": d["before_checkpoint"],
                    "source_branch_id": d["branch_id"],
                })

    manifest = {
        "schema": "caaf.m3.live_stage/1",
        "stage": "m3_live_v1_pilot",
        "status": "FROZEN_PENDING_AUTHORIZATION",
        "frozen_before_any_outcome": True,
        "supersedes": None,
        "historical_proposal": "experiments/m3_plan_v1/PLAN.md (not an authorization)",

        "purpose": (
            "Technical and cost feasibility of matched-prefix cross-model transfer. "
            "Establishes that the live provider accepts the declared Haiku 4.5 policy, "
            "that the explicit transfer fork preserves the saved prefix and board, and "
            "what a continuation actually costs. NOT a powered transfer test."
        ),
        "not_used_for": [
            "Confirmatory transfer labels or effect claims.",
            "Any statement about the target model's own failure taxonomy.",
            "Population or benchmark frequencies.",
        ],

        "selection": {
            "source": "experiments/m3_plan_v1/cost_forecast.json selected_decisions",
            "rule": ("Three Holm-resolved harmful decisions, two helpful-direction controls, "
                     "one early unresolved case and two flat controls, covering all four "
                     "represented starting positions. Selection is fixed by M2 statistics "
                     "and is independent of the behavioural taxonomy labels."),
            "decisions": len(decisions),
            "positions_represented": sorted({d["task_id"] for d in decisions}),
        },
        "decisions": decisions,

        "design": {
            "arms": list(ARMS),
            "arm_definitions": {
                "keep_original_reply": ("Restore the checkpoint, force the complete original "
                                        "Haiku 5.5 reply exactly once, then every later call uses "
                                        "the target model."),
                "redecide_reply": "Restore the checkpoint; the target model decides immediately.",
            },
            "continuations_per_arm": PER_ARM,
            "continuations_total": len(jobs),
            "paired": "Both arms run from the identical before-step checkpoint.",
            "randomisation": ("None. Replicates differ only by provider sampling; the prefix, "
                              "board and policy are identical by construction."),
        },
        "jobs": jobs,

        "models": {
            "target": {"id": TARGET, "role": "second model under test",
                       "listed_status": "Active (legacy); docs advise migrating to Haiku 5.5",
                       "retirement_stated": "not sooner than 2026-10-15; no firm date published"},
            "reference": {"id": REFERENCE, "role": "original M2 model; not dispatched in this stage"},
            "policy_source": "m3_runtime/policies.py (registry fingerprint recorded at run time)",
            "declared_change": ("M3 sets drop_params=False where M2 recorded True, and Haiku 4.5 "
                                "uses an explicit 4096-token thinking budget where Haiku 5.5 used "
                                "adaptive thinking. This is a declared model-policy transfer, not "
                                "isolation of model weights."),
        },

        "metrics": {
            "primary_feasibility": [
                "dispatch_success_rate",
                "response_model_identity_verified_on_every_call",
                "prefix_and_board_preserved_on_every_fork",
                "forced_reply_dispatched_exactly_once_in_keep_arm",
                "actual_usd_per_continuation",
                "actual_vs_proxy_token_ratio",
            ],
            "descriptive_only": [
                "recovery rate per arm per decision, with interval, labelled non-confirmatory",
            ],
            "multiplicity": ("None applied. No confirmatory claim is made from this stage. The "
                             "confirmation stage will declare and freeze its own Holm family "
                             "before its outcomes are collected."),
        },

        "budget": {
            "ceiling_usd": CAP_USD,
            "ledger": "experiments/m3_live_v1/ledger.sqlite",
            "shared": "One transactional cap across all jobs and worker processes.",
            "proxy_expectation_usd": 7.230300466666667,
            "proxy_basis": "same-usage proxy from M2 token counts at current Haiku 4.5 list prices",
            "note": ("Proxy may overestimate input tokens: Haiku 5.5's newer tokenizer yields "
                     "about 30% more tokens for the same text. It may underestimate output if "
                     "the 4096-token thinking budget exceeds Haiku 5.5's adaptive usage."),
            "unknown_usage_policy": "Maximum liability retained until usage and model identity are confirmed.",
        },

        "stopping_and_interruption": {
            "hard_stop": "Budget cap; no call starts that could exceed it.",
            "on_transport_failure": "Stop the run. No retries are configured or permitted.",
            "resume": ("Completed job_ids are skipped on restart. Reservations survive "
                       "interruption; no paid prefix is redrawn."),
            "abort_conditions": [
                "Any response whose model id is not the pinned target.",
                "Any fork that fails prefix, board or non-policy context verification.",
                "Any response missing usage.",
            ],
        },

        "provenance": {
            "taxonomy_sha256": sha256_file(TAX),
            "forecast_sha256": sha256_file(FORECAST),
            "m1_source_pin": "8799acfc484febd0c9156ccca0bfa00fb0724aeb",
            "store": "inputs/m1_original/runs/m1_think (read-only seed)",
        },

        "authorization": {
            "authorized_usd": 0,
            "authorized_by": None,
            "authorized_on": None,
            "note": ("No paid call may run until authorized_usd is set to the approved figure "
                     "by the project owner and this manifest is re-frozen."),
        },
    }

    OUT.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({
        "manifest": str(target_path.relative_to(ROOT)),
        "decisions": len(decisions), "jobs": len(jobs),
        "positions": manifest["selection"]["positions_represented"],
        "ceiling_usd": CAP_USD, "authorized_usd": 0,
        "api_calls": 0,
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
