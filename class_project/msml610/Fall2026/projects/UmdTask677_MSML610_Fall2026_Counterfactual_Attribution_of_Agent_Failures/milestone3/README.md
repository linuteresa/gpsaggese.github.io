# Milestone 3: Taxonomy and Transfer (chess)

Failure taxonomy over the Milestone 2 decisions, and a matched-prefix
cross-model transfer study: restore a checkpoint from a Haiku 5.5 run and let
Haiku 4.5 continue from the identical prefix and board.

Source: Sri Ramm's handoff bundle `caaf_chess_m3_handoff_20261121`, M1 source
pin `8799acfc484febd0c9156ccca0bfa00fb0724aeb`. Milestone 2 lives in
`../milestone2/` (PR #977) and stays frozen. This folder reads it through
relative links: `m2_runtime`, `inputs` and `experiments/m2_direct_v2` point
into `../milestone2/`, and `vendor/pr917` points to the M1 project root.

## Status

| Area | Status |
| :--- | :----- |
| Taxonomy of 7 failures / 48 decisions | First review done; independent review pending |
| Explicit model-switch transfer path | Implemented, verified offline |
| Model-specific spending guard | Implemented, tested offline |
| Live path | Verified end to end, first against a local fake server ($0), then live |
| Live provider compatibility | Verified 2026-11-22 after five pre-run fixes (see `pre_run_amendments`) |
| Paid pilot | Done 2026-11-22: 160/160 jobs, $2.25 settled; see `experiments/m3_live_v1/REPORT.md` |
| Cross-model transfer conclusion | Not measurable: Haiku 4.5 is at the floor (1/160 wins) |

## Setup

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r ../milestone2/requirements-analysis.lock
.venv/bin/python scripts/verify_m3_offline.py     # expect 59 passed
```

The suite runs the M3 tests, the frozen M2 regressions in `../milestone2/tests`
and the pinned M1 chess tests, with the network blocked. It needs
`../milestone2/inputs/` restored from the M1 archive (`bootstrap_offline.py` in
the handoff bundle); `inputs/` is not in git.

## Taxonomy review

```bash
.venv/bin/python scripts/build_review_sheet.py    # review/REVIEW_SHEET.md + .csv
# fill reviewer_* columns in review/taxonomy_review_sheet.csv
.venv/bin/python scripts/diff_taxonomy_review.py  # agreement + disagreements
```

The first review is never overwritten. The revision is published beside it,
with disagreements recorded.

## Live pilot

The design is frozen in `experiments/m3_live_v1/experiment_manifest.json`:
8 decisions across all 4 represented positions, two arms, 10 continuations per
arm, 160 total, Haiku 4.5, ceiling $15. It is a technical and cost feasibility
stage and is **not** used for confirmatory transfer labels.

```bash
.venv/bin/python scripts/run_m3_pilot.py --preflight      # 0 API calls
set -a; source ../milestone2/.env; set +a        # ANTHROPIC_API_KEY
.venv/bin/python scripts/run_m3_pilot.py --live --workers 4
```

Live mode refuses to start unless `ANTHROPIC_API_KEY` is set and
`authorization.authorized_usd` in the manifest is greater than zero. It stops on
the first transport failure, never retries, and resumes by skipping job IDs
already recorded for the same mode. Preflight writes `results.json` and
`progress.json`; live writes `results_live.json` and `progress_live.json`. The
three runner fixes made before any outcome are listed under
`pre_run_amendments` in the manifest.

## Pilot report

```bash
.venv/bin/python scripts/report_m3_pilot.py   # report.json + REPORT.md, 0 API calls
```

Write-up: [`../docs/milestone3.md`](../docs/milestone3.md).

## Limits

Matched-prefix transfer is conditional on Haiku 5.5's histories and original
replies. It does not establish Haiku 4.5's own failure taxonomy. The 48
decisions come from 7 failures across 4 positions and are not 48 independent
tasks. Haiku 4.5 is listed as legacy and past its earliest stated retirement
date.
