# Milestone 3: Taxonomy and Transfer (chess)

- **Goal**: Group the Milestone 2 failures into observable failure modes, and
  test whether the blamed decisions transfer to a second model.
- **Scope**: The seven Milestone 2 failures (48 decisions, four starting
  positions) and a matched-prefix transfer pilot on eight of those decisions.
  This is a feasibility result for
  [the Milestone 3 plan](04-plan.md#milestone-3-taxonomy-and-transfer); it does
  not cover a second task family.
- **Code and data**: [`milestone3/`](../milestone3/README.md). It reads the
  frozen Milestone 2 evidence in `../milestone2/` without changing it.

## Taxonomy

- Reviewed all 48 original replies against the board, with deterministic chess
  checks ([TAXONOMY.md](../milestone3/experiments/m3_offline_v1/TAXONOMY.md)):

  | Observed label | Decisions / 48 | Runs / 7 |
  | :------------- | -------------: | -------: |
  | False attack or legal-reply claim | 8 | 7 |
  | Clock-aware win lost without rook capture | 5 | 5 |
  | Board revisited while spending clock | 4 | 3 |
  | Actual rook loss | 2 | 2 |
  | Uncertain planning or wording (kept separate) | 8 | - |

- Labels overlap. All 48 commands were legal and well formed; no false
  completion claim was observed
- Behavioural labels are not causal evidence: only three replies have a
  harmful effect resolved by the Milestone 2 Holm family (`krk-m4-1` trial 0
  steps 3 and 5, trial 1 step 1). Ke2 at trial 0 step 3 makes a false
  rook-ray claim and has the largest measured effect (+67 pp)
- Status: first review by an assistant; Linu's independent review is pending
  ([review sheet](../milestone3/review/REVIEW_SHEET.md))

## Transfer: Second Model or Different Settings

- Decision: a second model, `claude-haiku-4-5-20251001` with a fixed
  4,096-token thinking budget, continuing Haiku 5.5's saved games from the
  identical conversation and board (`m3_runtime/transfer.py`)
- This is a declared model-policy transfer (model and thinking mode both
  change), not an isolation of model weights

## Live Pilot (2026-11-22)

- Design frozen before any outcome
  ([manifest](../milestone3/experiments/m3_live_v1/experiment_manifest.json)):
  8 decisions, keep-original-reply and re-decide arms, 10 continuations per
  arm, 160 in total, $15 ceiling, approved by Linu on 2026-11-22
- Five runner defects were found and fixed before any outcome, each with a test;
  they are listed under `pre_run_amendments` in the manifest:
  - Live resume read the preflight records and would have skipped every job
  - The offline network block was never lifted in live mode
  - `service_tier` is rejected by litellm with `drop_params=False`; M2 never
    actually sent it
  - Haiku 4.5 rejects `inference_geo` (400)
  - Haiku 4.5 reports `inference_geo: "not_available"`, which the usage check
    refused; two requests kept their $0.33 maximum liability as a result
- Feasibility ([report](../milestone3/experiments/m3_live_v1/REPORT.md)):

  | Check | Result |
  | :---- | :----- |
  | Jobs completed | 160 / 160, 0 errors |
  | Response model `claude-haiku-4-5-20251001` on every one of 256 calls | Yes |
  | Prefix, board and counters preserved on every fork | Yes |
  | Original reply forced exactly once in the keep arm, never in re-decide | Yes |
  | Settled cost | $2.25, $0.014 per continuation (proxy forecast $7.23) |
  | Ledger total against the $15 cap | $2.91, including the $0.66 retained maximum |

- Outcome: a floor. Haiku 4.5 won 1 of 160 games (keep 0/80, re-decide
  1/80); 156 games ended in insufficient material after it lost the rook,
  usually within one or two moves of taking over
  - At the three decisions where re-deciding helped Haiku 5.5 by +37 to +67 pp,
    Haiku 4.5's gains are 0, +10 and 0 pp, each with an interval of about
    +/-28 pp at 10 per arm
- Interpretation: the pilot shows the transfer machinery works and is cheap,
  but this Haiku 4.5 policy is too weak at KRvK to measure transfer. A floor
  does not show that the blamed decisions fail to transfer; it shows there is
  no variation to compare. As the pilot plan requires, the limitation is
  reported before any later paid phase
- These outcomes are descriptive and excluded from any confirmation labels

## Limits

- Seven selected failures from four positions in one task family; frequencies
  are not population estimates, and 48 decisions are not 48 independent tasks
- Matched-prefix transfer is conditional on Haiku 5.5's histories; it says
  nothing about Haiku 4.5's own failure modes
- The two retained maximum liabilities ($0.66) are an upper bound; their actual
  cost is not recorded in the ledger. One diagnostic call outside the ledger
  (82 tokens, about $0.0002) captured the usage format
