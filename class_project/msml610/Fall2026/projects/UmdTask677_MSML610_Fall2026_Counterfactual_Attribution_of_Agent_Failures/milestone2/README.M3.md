# Milestone 3: Taxonomy and Transfer (chess)

Failure taxonomy over the Milestone 2 decisions, and a matched-prefix
cross-model transfer study: restore a checkpoint from a Haiku 5.5 run and let
Haiku 4.5 continue from the identical prefix and board.

Source: Sri Ramm's handoff bundle `caaf_chess_m3_handoff_20261121`, M1 source
pin `8799acfc484febd0c9156ccca0bfa00fb0724aeb`. Milestone 2 is merged in
`../milestone2/` (PR #977); `m2_runtime` and `vendor/pr917` are symlinks to it
and to the M1 project root.

## Status

| Area | Status |
| :--- | :----- |
| Taxonomy of 7 failures / 48 decisions | First review done; independent review pending |
| Explicit model-switch transfer path | Implemented, verified offline |
| Model-specific spending guard | Implemented, tested offline |
| Live provider compatibility | Not tested |
| Paid pilot | Frozen manifest, not authorized |
| Cross-model transfer conclusion | Not measured |

## Setup

```bash
python3.12 bootstrap_offline.py          # restores inputs/ from the M1 archive
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-analysis.lock
.venv/bin/python scripts/verify_m3_offline.py     # expect 55 passed
```

`bootstrap_offline.py` needs `inputs/archive/m1_runs.tar.gz` from the handoff
bundle or the shared Drive folder; `inputs/` is not in git.

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
set -a; source .env; set +a
.venv/bin/python scripts/run_m3_pilot.py --live --workers 4
```

Live mode refuses to start unless `ANTHROPIC_API_KEY` is set and
`authorization.authorized_usd` in the manifest is greater than zero. It stops on
the first transport failure, never retries, and resumes by skipping completed
job IDs.

## Limits

Matched-prefix transfer is conditional on Haiku 5.5's histories and original
replies. It does not establish Haiku 4.5's own failure taxonomy. The 48
decisions come from 7 failures across 4 positions and are not 48 independent
tasks. Haiku 4.5 is listed as legacy and past its earliest stated retirement
date.
