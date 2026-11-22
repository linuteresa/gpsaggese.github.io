#!/usr/bin/env python3
"""Build an independent-review sheet for the M3 failure taxonomy.

Reads  : experiments/m3_offline_v1/taxonomy.json   (first review, read-only)
Writes : review/taxonomy_review_sheet.csv          (fill in the reviewer_* columns)
         review/REVIEW_SHEET.md                    (readable, full context)

No model calls, no network, no writes outside review/.
The first review is never modified: your answers go in new columns.
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TAX = ROOT / "experiments" / "m3_offline_v1" / "taxonomy.json"
OUT = ROOT / "review"

READ_ONLY = ("m2_repair_gain", "m2_holm_p", "m2_causal_status")
REVIEWER = ("reviewer_labels", "reviewer_uncertain", "reviewer_note", "agree_with_first")

FIELDS = [
    "decision_id", "task_id", "trial", "step", "command",
    "before_fen", "after_fen", "oracle_before", "oracle_after",
    "reply_thought",
    "first_labels", "first_uncertain", "first_note", "first_claim_check",
    *READ_ONLY,
    *REVIEWER,
]


def thought(reply: str) -> str:
    """The public reasoning line, without the fenced command block."""
    text = reply.split("```")[0].strip()
    return text[len("THOUGHT:"):].strip() if text.startswith("THOUGHT:") else text


def oracle(o: dict | None) -> str:
    if not o:
        return ""
    verdict = {2: "win", 1: "cursed win", 0: "draw", -1: "blessed loss", -2: "loss"}.get(o.get("wdl"), "?")
    return f"{verdict} dtz={o.get('dtz')} clock={o.get('clock')}"


def main() -> int:
    if not TAX.exists():
        print(f"missing {TAX}", file=sys.stderr)
        return 1
    tax = json.loads(TAX.read_text())
    decisions, summary = tax["decisions"], tax["summary"]
    OUT.mkdir(exist_ok=True)

    # ---------- CSV ----------
    with (OUT / "taxonomy_review_sheet.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for d in decisions:
            stats = d.get("m2_primary_statistics") or {}
            w.writerow({
                "decision_id": d["decision_id"], "task_id": d["task_id"],
                "trial": d["trial"], "step": d["step"], "command": d["command"],
                "before_fen": d["before_fen"], "after_fen": d["after_fen"],
                "oracle_before": oracle(d.get("oracle_before")),
                "oracle_after": oracle(d.get("oracle_after")),
                "reply_thought": thought(d.get("reply_text", "")),
                "first_labels": "|".join(d.get("observed_labels") or []),
                "first_uncertain": d.get("uncertain_interpretation"),
                "first_note": d.get("review_note", ""),
                "first_claim_check": json.dumps(d["claim_check"]) if d.get("claim_check") else "",
                "m2_repair_gain": stats.get("repair_gain", ""),
                "m2_holm_p": stats.get("holm_p", ""),
                "m2_causal_status": d.get("causal_status", ""),
                **{k: "" for k in REVIEWER},
            })

    # ---------- Markdown ----------
    defs = summary.get("definitions", {})
    lines = [
        "# Independent review sheet — M3 failure taxonomy",
        "",
        f"First review dated {summary.get('date')}, {summary['decisions']} decisions across "
        f"{summary['failed_dialogues']} failed dialogues and {summary['distinct_tasks']} positions.",
        "",
        "Fill in `reviewer_labels`, `reviewer_uncertain`, `reviewer_note` and `agree_with_first` "
        "in `taxonomy_review_sheet.csv`, then run `scripts/diff_taxonomy_review.py`.",
        "Do not edit `taxonomy.json` or the `m2_*` columns: those are frozen.",
        "",
        "## Label vocabulary",
        "",
    ]
    for name, text in defs.items():
        lines += [f"- **`{name}`** — {text}", ""]
    lines += [
        "Leave `reviewer_labels` empty for no label. Separate several labels with `|`.",
        "`reviewer_uncertain` is `True` or `False`: the reply's planning or wording is open to "
        "more than one reading, separately from any factual error.",
        "",
        "## Decisions",
        "",
    ]

    by_run: dict[str, list[dict]] = {}
    for d in decisions:
        by_run.setdefault(f"{d['task_id']} trial {d['trial']}", []).append(d)

    for run, items in by_run.items():
        lines += [f"### {run}", ""]
        for d in sorted(items, key=lambda x: x["step"]):
            stats = d.get("m2_primary_statistics") or {}
            flags = []
            if d.get("observed_labels"):
                flags.append(" ".join(f"`{x}`" for x in d["observed_labels"]))
            if d.get("uncertain_interpretation"):
                flags.append("**uncertain**")
            if d.get("causal_status") == "resolved_harmful":
                flags.append("**Holm-resolved harmful**")
            lines += [
                f"#### `{d['decision_id']}` — step {d['step']}: `{d['command']}`",
                "",
                f"- Position before: `{d['before_fen']}`",
                f"- Position after: `{d['after_fen']}`",
                f"- Tablebase: {oracle(d.get('oracle_before'))} -> {oracle(d.get('oracle_after'))}",
                f"- M2: gain {stats.get('repair_gain')}, Holm p {stats.get('holm_p')}, "
                f"keep {stats.get('keep_wins')}/{stats.get('keep_n')}, "
                f"re-decide {stats.get('redecide_wins')}/{stats.get('redecide_n')}",
                "",
                "> " + thought(d.get("reply_text", "")).replace("\n", "\n> "),
                "",
                f"First review: {' '.join(flags) if flags else '_no label_'} — {d.get('review_note', '')}",
                "",
                "Your verdict: _______________________________________________",
                "",
            ]

    (OUT / "REVIEW_SHEET.md").write_text("\n".join(lines))
    print(json.dumps({
        "decisions": len(decisions),
        "labelled_by_first_review": sum(1 for d in decisions if d.get("observed_labels")),
        "uncertain": sum(1 for d in decisions if d.get("uncertain_interpretation")),
        "csv": str((OUT / 'taxonomy_review_sheet.csv').relative_to(ROOT)),
        "markdown": str((OUT / 'REVIEW_SHEET.md').relative_to(ROOT)),
        "api_calls": 0,
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
