#!/usr/bin/env python3
"""Compare an independent review against the first M3 taxonomy review.

Reads  : review/taxonomy_review_sheet.csv  (your reviewer_* columns)
         experiments/m3_offline_v1/taxonomy.json  (first review, read-only)
Writes : review/review_agreement.json
         review/REVIEW_AGREEMENT.md

Reports agreement on labels and on the uncertain flag, and lists every
disagreement. It never edits the first review: a revision is published
alongside it, per the handoff.

Agreement here is one reviewer against one earlier assistant pass. It is not
a kappa over independent raters, and a high number does not make the first
review correct.
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TAX = ROOT / "experiments" / "m3_offline_v1" / "taxonomy.json"
SHEET = ROOT / "review" / "taxonomy_review_sheet.csv"
OUT = ROOT / "review"


def labels(raw: str) -> set[str]:
    return {p.strip() for p in (raw or "").replace(",", "|").split("|") if p.strip()}


def tri(raw: str) -> bool | None:
    v = (raw or "").strip().lower()
    if v in ("true", "t", "yes", "y", "1"):
        return True
    if v in ("false", "f", "no", "n", "0"):
        return False
    return None


def main() -> int:
    for p in (TAX, SHEET):
        if not p.exists():
            print(f"missing {p}", file=sys.stderr)
            return 1

    first = {d["decision_id"]: d for d in json.loads(TAX.read_text())["decisions"]}
    rows = list(csv.DictReader(SHEET.open()))

    vocab = set(json.loads(TAX.read_text())["summary"].get("definitions", {}))
    reviewed, label_same, unc_same = 0, 0, 0
    disagreements, unknown_labels, unreviewed = [], [], []

    for r in rows:
        did = r["decision_id"]
        src = first.get(did)
        if src is None:
            print(f"unknown decision_id in sheet: {did}", file=sys.stderr)
            return 1

        mine_l, mine_u, note = labels(r.get("reviewer_labels", "")), tri(r.get("reviewer_uncertain", "")), (r.get("reviewer_note") or "").strip()
        touched = bool(r.get("reviewer_labels", "").strip() or r.get("reviewer_uncertain", "").strip() or note)
        if not touched:
            unreviewed.append(did)
            continue

        reviewed += 1
        theirs_l = set(src.get("observed_labels") or [])
        theirs_u = bool(src.get("uncertain_interpretation"))
        if mine_u is None:
            mine_u = theirs_u

        bad = mine_l - vocab
        if bad:
            unknown_labels.append({"decision_id": did, "labels": sorted(bad)})

        l_ok, u_ok = mine_l == theirs_l, mine_u == theirs_u
        label_same += l_ok
        unc_same += u_ok
        if not (l_ok and u_ok):
            disagreements.append({
                "decision_id": did, "command": src["command"],
                "step": src["step"], "task_id": src["task_id"],
                "first_labels": sorted(theirs_l), "reviewer_labels": sorted(mine_l),
                "first_uncertain": theirs_u, "reviewer_uncertain": mine_u,
                "first_note": src.get("review_note", ""), "reviewer_note": note,
                "causal_status": src.get("causal_status"),
            })

    result = {
        "schema": "caaf.m3.review_agreement/1",
        "decisions_total": len(first),
        "decisions_reviewed": reviewed,
        "decisions_not_reviewed": len(unreviewed),
        "label_agreement": round(label_same / reviewed, 4) if reviewed else None,
        "uncertain_agreement": round(unc_same / reviewed, 4) if reviewed else None,
        "disagreements": len(disagreements),
        "unknown_labels": unknown_labels,
        "not_reviewed_ids": unreviewed,
        "detail": disagreements,
        "api_calls": 0,
        "note": "One reviewer against one earlier assistant pass; not an inter-rater kappa.",
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "review_agreement.json").write_text(json.dumps(result, indent=1))

    md = [
        "# Review agreement — M3 failure taxonomy",
        "",
        f"Reviewed {reviewed} of {len(first)} decisions.",
        "",
    ]
    if reviewed:
        md += [
            f"- Label agreement: **{result['label_agreement']:.1%}**",
            f"- Uncertain-flag agreement: **{result['uncertain_agreement']:.1%}**",
            f"- Disagreements: **{len(disagreements)}**",
            "",
        ]
    if unknown_labels:
        md += ["> Labels outside the declared vocabulary: "
               + ", ".join(f"`{u['decision_id']}` ({', '.join(u['labels'])})" for u in unknown_labels), ""]
    if unreviewed:
        md += [f"> Not yet reviewed: {len(unreviewed)} decisions.", ""]

    if disagreements:
        md += ["## Disagreements", ""]
        for d in disagreements:
            md += [
                f"### `{d['decision_id']}` — step {d['step']}: `{d['command']}`",
                "",
                f"- First review: {', '.join(d['first_labels']) or '_none_'}"
                f" · uncertain={d['first_uncertain']} · {d['causal_status']}",
                f"- This review: {', '.join(d['reviewer_labels']) or '_none_'}"
                f" · uncertain={d['reviewer_uncertain']}",
                f"- First note: {d['first_note']}",
                f"- This note: {d['reviewer_note'] or '_none_'}",
                "",
            ]
    else:
        md += ["No disagreements recorded.", ""]

    md += [
        "## How to read this",
        "",
        "This compares one reviewer against one earlier assistant pass. It is not an",
        "inter-rater kappa, and agreement does not make either pass correct. Both",
        "versions are kept; neither replaces the other.",
        "",
    ]
    (OUT / "REVIEW_AGREEMENT.md").write_text("\n".join(md))

    print(json.dumps({k: v for k, v in result.items() if k != "detail"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
