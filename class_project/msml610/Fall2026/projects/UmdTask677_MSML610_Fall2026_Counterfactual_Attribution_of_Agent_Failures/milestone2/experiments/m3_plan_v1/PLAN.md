# Milestone 3 proposal — taxonomy and transfer

Draft, November 19, 2026. **No M3 paid work is authorized or started.**
This draft does not alter the frozen M2 experiment, its evidence archive, or
the paused retail pilot. `cost_forecast.json` records the proposed sample
counts, selected checkpoints, empirical cost basis and current list prices.

## What Milestone 3 requires

The [original project specification](https://github.com/gpsaggese/gpsaggese.github.io/issues/677)
calls for recurring failure categories with frequencies, and analysis across
models and task families. The pinned chess plan at
`vendor/pr917/docs/04-plan.md` permits a smaller feasibility adaptation, including
deciding between a second model and different Haiku settings.

The recommended next study is explicitly a **chess taxonomy and matched-prefix
cross-model feasibility study**. It does not complete the original cross-family
requirement. More KRvK difficulty bins still belong to one chess task family.

## 1. Build the taxonomy offline — $0 API usage

Review all seven original failed trajectories and all 48 original decisions.
Use categories grounded in observable traces and legal board transitions:
incorrect attack/legal-reply reasoning, material safety, clock-aware planning,
command/format errors where actually observed, and unresolved cases. Do not
invent categories with nonzero frequencies or infer a failure cause from a
flat profile alone. Multiple labels and uncertain labels are allowed.

Keep behavioral labels separate from causal evidence: only three original
replies currently survive the primary 48-test Holm correction. Those occur
in two trajectories from one starting position. Report denominators by reply,
run and starting position; these selected failures do not estimate benchmark
or population frequencies. Group profiles descriptively; seven profiles are
insufficient to validate a stable unsupervised clustering taxonomy. Labeling
is post hoc, and independent human review should be recorded if performed.

Deliverables: decision annotation table, category definitions, trace-linked
examples, frequency table, unresolved cases and descriptive profile groups.

## 2. Prepare an explicit cross-model fork offline

The existing `caaf_agent.fork` restores the parent checkpoint's model and
sampling settings even when passed another config. A new, versioned transfer
fork must record the intentional model-policy change, preserve the API-visible
prefix, board, clock and remaining-call limits, and demonstrate the requested
model switch with a mocked transport before any live inference.

Use a new model-aware reservation guard. Preserve frozen M2 code. Verify each
model's prices, context/output bounds, actual response model ID, usage, hidden
retry settings and unknown-request liabilities. Do not silently truncate
history. Retain the existing evidence-preservation and interruption rules.

## 3. Run a separate technical/cost pilot — proposed ceiling $15

The economical second-model candidate is pinned
`claude-haiku-4-5-20251001`. It uses manual extended thinking, rather than
Haiku 5.5's adaptive thinking; the comparison is between recorded model
policies, not an isolation of model weights. Proposed settings are a fixed
4,096-token thinking budget and 16,000 maximum output tokens, subject to
offline compatibility tests and a live access check after authorization.

Use eight preselected checkpoints: the three corrected harmful decisions,
two helpful-direction controls, one early unresolved case, and two flat
controls, covering all four represented positions. Sample 10 keep and 10
re-decide continuations at each: **160 continuations**. The exact IDs are in
the JSON proposal. This is feasibility/cost evidence, not a powered transfer
test. Exclude these pilot samples from later confirmation labels.

Report results and actual cost before releasing a later paid phase. If the
model is inaccessible, cannot resume faithfully, or shows too little usable
outcome variation, report the limitation and revise the proposal before
changing the model or sampling. A floor result does not prove no transfer.

## 4. Fresh confirmation if the pilot supports proceeding

Before these outcomes, freeze the final settings, counts, comparison metric,
uncertainty method, multiplicity treatment, and rules for inconclusive transfer.

- **780 fresh Haiku 5.5 continuations:** 30 per arm at the union of the eight
  transfer checkpoints and all nine decisions in the two krk-m4-1 failures.
  This is 13 distinct decisions, without duplicate sampling at overlap points.
  It independently repeats the M2 discovery profiles and supplies fresh
  reference comparisons, reducing dependence on discovery-stage selection.
- **480 fresh second-model continuations:** 30 per arm at the eight transfer
  checkpoints. These are separate from the technical pilot.

Compare gain magnitudes, ranks and directions with uncertainty. A significant
effect in one model and a nonsignificant effect in the other is not itself
evidence of a cross-model difference. Preserve whole-task dependence, flat
controls and unresolved outcomes. No outcome-driven sample expansion.

This tests transfer conditional on Haiku 5.5-generated histories and original
replies. It does not establish the taxonomy of the second model's own fresh
natural failures. That requires additional task-level runs and profiling.

## Cost basis

Current [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
lists Haiku 4.5 at $1 input / $5 output per million tokens, versus Haiku 5.5
at $0.10 / $0.50 for these short prompts. Prices were checked November 19.

Repricing the actual matched M2 traces gives:

| Phase | Continuations | Same-usage cost proxy |
| --- | ---: | ---: |
| Offline taxonomy and protocol checks | 0 | $0 |
| Second-model technical/cost pilot | 160 | $7.23 |
| Fresh reference plus M2 discovery-profile repeats | 780 | $2.83 |
| Fresh second-model confirmation | 480 | $21.69 |
| Total chess study | 1,420 | $31.75 |

The proxy is about **6,000 model calls, 14.8 million input tokens and
10.6 million output tokens**. With the same token counts but no input-cache
discounts, it is about $37.52. New-model reasoning length, tokenizer and
continuation length can differ substantially: this is not a confidence
interval or quote. Plan approximately **$30–50** and propose a **shared $60
hard ceiling**, with only the first **$15 pilot stage** released initially.
The proposed later-stage allowance is at most $45, subject to reviewing the
pilot. No approval is inferred from this draft or M2's unused allowance.

## Completing the broader original M3

A second validated task family and, for model-owned taxonomy claims, fresh
second-model natural trajectories must be added. Retail could eventually
supply that family after its existing customer-fidelity defect is fixed in a
new release and a targeted pilot passes. Retail is not a dependency for
starting the offline taxonomy or the chess transfer pilot. Do not reuse the
paused retail results as certified data or modify/resubmit its frozen pilot.

Second-family collection and evaluation need a separate measured forecast;
the $60 chess proposal excludes them and excludes M4 training/scaffold trials.
The M4 handoff must retain task-group splits and explicit candidate-reply
feature timing, because identical pre-generation states in M2 precede
opposite reply-specific point gain estimates.
