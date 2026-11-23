#!/usr/bin/env python3
"""Report the M3 live pilot: feasibility metrics and descriptive recovery rates.

Reads  : experiments/m3_live_v1/experiment_manifest.json, results_live.json,
         ledger.sqlite (read-only)
Writes : experiments/m3_live_v1/report.json, REPORT.md

No model calls; the network stays blocked. Recovery rates are descriptive
only, as frozen in the manifest: no multiplicity correction, no claim.
"""

from __future__ import annotations

import collections
import json
import sqlite3
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from m3_offline_common import ROOT  # noqa: E402  (blocks the network)

import caaf_utils  # noqa: E402

STAGE = ROOT / "experiments" / "m3_live_v1"
FORECAST = ROOT / "experiments" / "m3_plan_v1" / "cost_forecast.json"
TARGET_RESPONSE_MODEL = "claude-haiku-4-5-20251001"
NANO = 1_000_000_000


def ledger_rows() -> list[dict]:
    uri = f"file:{STAGE / 'ledger.sqlite'}?mode=ro"
    with sqlite3.connect(uri, uri=True) as db:
        db.row_factory = sqlite3.Row
        return [dict(r) for r in db.execute("select * from requests")]


def interval(lo_hi) -> list[float]:
    return [round(lo_hi[0], 3), round(lo_hi[1], 3)]


def main() -> int:
    manifest = json.loads((STAGE / "experiment_manifest.json").read_text())
    results = json.loads((STAGE / "results_live.json").read_text())
    rows = ledger_rows()
    completed = [r for r in results if r["status"] == "completed"]
    done_ids = {r["job_id"] for r in completed}

    # ---- Feasibility ----
    settled = [r for r in rows if r["status"] == "settled"]
    stage_settled = [r for r in settled if r["job_id"] in done_ids]
    uncertain = [r for r in rows if r["status"] == "uncertain_maximum_retained"]
    rejected = [r for r in rows if r["status"] == "rejected_before_inference"]
    usage = [json.loads(r["usage_json"]) for r in stage_settled]
    tokens_in = sum(u["prompt_tokens"] for u in usage)
    tokens_out = sum(u["completion_tokens"] for u in usage)
    cost_done = sum(r["liability"] for r in stage_settled) / NANO
    basis = json.loads(FORECAST.read_text())["empirical_cost_basis"][
        "matched_8_M2_decisions_480_continuations"
    ]
    per_cont_proxy_in = basis["input_tokens"] / 480
    per_cont_proxy_out = basis["output_tokens"] / 480
    n = max(1, len(completed))
    keep = [r for r in completed if r["arm"] == "keep_original_reply"]
    redecide = [r for r in completed if r["arm"] == "redecide_reply"]
    feasibility = {
        "jobs_planned": len(manifest["jobs"]),
        "jobs_completed": len(completed),
        "jobs_not_completed": len(manifest["jobs"]) - len(completed),
        "dispatch_success_rate": round(
            len(settled) / max(1, len(settled) + len(uncertain)), 4
        ),
        "paid_calls_settled_for_completed_jobs": len(stage_settled),
        "response_model_identity_verified_on_every_call": all(
            r["response_model"] == TARGET_RESPONSE_MODEL for r in stage_settled
        ),
        "prefix_and_board_preserved_on_every_fork": all(
            all(r["verification"].values()) for r in completed
        ),
        "forced_reply_dispatched_exactly_once_in_keep_arm": all(
            r["forced_replies"] == 1 for r in keep
        ),
        "no_forced_reply_in_redecide_arm": all(
            r["forced_replies"] == 0 for r in redecide
        ),
        "actual_usd_completed_jobs": round(cost_done, 6),
        "actual_usd_per_continuation": round(cost_done / n, 6),
        "input_tokens_per_continuation": round(tokens_in / n, 1),
        "output_tokens_per_continuation": round(tokens_out / n, 1),
        "actual_vs_proxy_token_ratio": {
            "input": round(tokens_in / n / per_cont_proxy_in, 3),
            "output": round(tokens_out / n / per_cont_proxy_out, 3),
        },
        "proxy_usd_for_160": round(
            manifest["budget"]["proxy_expectation_usd"], 4
        ),
        "ledger": {
            "settled_requests": len(settled),
            "settled_usd": round(sum(r["liability"] for r in settled) / NANO, 6),
            "uncertain_maximum_retained_requests": len(uncertain),
            "uncertain_maximum_retained_usd": round(
                sum(r["liability"] for r in uncertain) / NANO, 6
            ),
            "rejected_before_inference_requests": len(rejected),
            "accounted_plus_reserved_usd": round(
                sum(r["liability"] for r in rows) / NANO, 6
            ),
            "cap_usd": manifest["budget"]["ceiling_usd"],
        },
    }

    # ---- Descriptive recovery rates ----
    by = collections.defaultdict(
        lambda: {"keep_original_reply": [], "redecide_reply": []}
    )
    for r in completed:
        by[r["decision_id"]][r["arm"]].append(r)
    decisions = []
    for d in manifest["decisions"]:
        arms = by[d["decision_id"]]
        kw = sum(r["outcome"]["won"] for r in arms["keep_original_reply"])
        kn = len(arms["keep_original_reply"])
        rw = sum(r["outcome"]["won"] for r in arms["redecide_reply"])
        rn = len(arms["redecide_reply"])
        ends = collections.Counter(
            r["outcome"]["end"] for a in arms.values() for r in a
        )
        row = {
            "decision_id": d["decision_id"],
            "selection_role": d["selection_role"],
            "h45_keep": [kw, kn],
            "h45_redecide": [rw, rn],
            "h45_gain": None,
            "h45_gain_interval": None,
            "h55_m2_keep": d["m2_keep"],
            "h55_m2_redecide": d["m2_redecide"],
            "h55_m2_gain": round(d["m2_repair_gain"], 3),
            "h55_m2_holm_p": d["m2_holm_p"],
            "ends": dict(ends),
        }
        if kn and rn:
            row["h45_gain"] = round(rw / rn - kw / kn, 3)
            row["h45_gain_interval"] = interval(
                caaf_utils.newcombe_diff(rw, rn, kw, kn)
            )
            row["h45_keep_interval"] = interval(caaf_utils.wilson(kw, kn))
            row["h45_redecide_interval"] = interval(caaf_utils.wilson(rw, rn))
        decisions.append(row)

    report = {
        "stage": manifest["stage"],
        "label": "Technical and cost feasibility. Recovery rates are descriptive, non-confirmatory, "
        "and excluded from later confirmation labels.",
        "feasibility": feasibility,
        "decisions": decisions,
        "ends_overall": dict(
            collections.Counter(r["outcome"]["end"] for r in completed)
        ),
        "wins_overall": {
            "keep_original_reply": [
                sum(r["outcome"]["won"] for r in keep),
                len(keep),
            ],
            "redecide_reply": [
                sum(r["outcome"]["won"] for r in redecide),
                len(redecide),
            ],
        },
    }
    (STAGE / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    (STAGE / "REPORT.md").write_text(markdown(report))
    print(json.dumps(feasibility, indent=1))
    return 0


def pct(x) -> str:
    return "n/a" if x is None else f"{100 * x:+.0f}"


def markdown(rep: dict) -> str:
    f, led = rep["feasibility"], rep["feasibility"]["ledger"]
    yes = lambda b: "yes" if b else "**no**"  # noqa: E731
    lines = [
        "# M3 live pilot: Haiku 4.5 continuing Haiku 5.5 checkpoints",
        "",
        rep["label"],
        "",
        "## Feasibility",
        "",
        "| Check | Result |",
        "| :--- | :--- |",
        f"| Jobs completed | {f['jobs_completed']} / {f['jobs_planned']} |",
        f"| Paid calls settled for completed jobs | {f['paid_calls_settled_for_completed_jobs']} |",
        f"| Dispatch success (settled / all requests that reached inference, incl. the pre-fix aborts) | {f['dispatch_success_rate']:.1%} |",
        f"| Response model was `claude-haiku-4-5-20251001` on every call | {yes(f['response_model_identity_verified_on_every_call'])} |",
        f"| Prefix, board and counters preserved on every fork | {yes(f['prefix_and_board_preserved_on_every_fork'])} |",
        f"| Keep arm forced the original reply exactly once | {yes(f['forced_reply_dispatched_exactly_once_in_keep_arm'])} |",
        f"| Re-decide arm forced no reply | {yes(f['no_forced_reply_in_redecide_arm'])} |",
        f"| Cost of completed jobs | ${f['actual_usd_completed_jobs']:.4f} (${f['actual_usd_per_continuation']:.4f} per continuation) |",
        f"| Same-usage proxy for 160 | ${f['proxy_usd_for_160']:.2f} |",
        f"| Tokens per continuation, actual / proxy | input {f['actual_vs_proxy_token_ratio']['input']}, output {f['actual_vs_proxy_token_ratio']['output']} |",
        f"| Ledger: settled | {led['settled_requests']} requests, ${led['settled_usd']:.4f} |",
        f"| Ledger: maximum retained (uncertain) | {led['uncertain_maximum_retained_requests']} requests, ${led['uncertain_maximum_retained_usd']:.2f} |",
        f"| Ledger: rejected before inference | {led['rejected_before_inference_requests']} requests, $0 |",
        f"| Ledger total against the ${led['cap_usd']} cap | ${led['accounted_plus_reserved_usd']:.4f} |",
        "",
        "## Recovery rates (descriptive)",
        "",
        "Gain = P(win | re-decide) - P(win | keep original reply), in percentage points. "
        "Haiku 4.5 has 10 continuations per arm (Newcombe 95% interval, unadjusted). "
        "The Haiku 5.5 columns are the frozen M2 estimates at 30 per arm.",
        "",
        "| Decision | Role | H4.5 keep | H4.5 re-decide | H4.5 gain (pp) | 95% interval (pp) | H5.5 M2 gain (pp) | H5.5 Holm p |",
        "| :--- | :--- | ---: | ---: | ---: | :--- | ---: | ---: |",
    ]
    for d in rep["decisions"]:
        iv = d["h45_gain_interval"]
        ivs = (
            "n/a" if iv is None else f"[{100 * iv[0]:+.0f}, {100 * iv[1]:+.0f}]"
        )
        lines.append(
            f"| `{d['decision_id']}` | {d['selection_role']} | {d['h45_keep'][0]}/{d['h45_keep'][1]} "
            f"| {d['h45_redecide'][0]}/{d['h45_redecide'][1]} | {pct(d['h45_gain'])} | {ivs} "
            f"| {pct(d['h55_m2_gain'])} | {d['h55_m2_holm_p']:.3g} |"
        )
    w = rep["wins_overall"]
    lines += [
        "",
        f"Overall wins: keep {w['keep_original_reply'][0]}/{w['keep_original_reply'][1]}, "
        f"re-decide {w['redecide_reply'][0]}/{w['redecide_reply'][1]}. "
        f"Game endings: {', '.join(f'{k} {v}' for k, v in sorted(rep['ends_overall'].items()))}.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
