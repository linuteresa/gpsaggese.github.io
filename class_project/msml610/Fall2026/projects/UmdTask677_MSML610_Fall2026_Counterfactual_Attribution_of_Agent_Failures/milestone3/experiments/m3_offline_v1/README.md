# Offline Milestone 3 preparation

Completed November 20, 2026: the failure taxonomy and cross-model runtime
preparation requested for this stage. **Actual API calls: 0. Actual API cost: $0.**
No paid M3 run is authorized or launched by this preparation. Full Milestone 3
is not complete; cross-model statistical effects have not been measured.

## Failure taxonomy

[TAXONOMY.md](TAXONOMY.md) contains the review of every original decision.
[taxonomy.csv](taxonomy.csv) is the compact annotation table;
[taxonomy.json](taxonomy.json) adds board facts, M2 statistics and evidence hashes.
The seven complete public dialogue histories are in
[DIALOGUES.md](DIALOGUES.md) and [dialogues.json](dialogues.json).

| Observation | Decisions / 48 |
|---|---:|
| Verified false attack or legal-reply claim | 8 |
| Actual rook loss to the defender | 2 |
| Clock-aware theoretical win lost without rook capture | 5 |
| Board revisited while consuming clock | 4 |
| Separate uncertain planning/text interpretation | 8 |

Labels overlap. The denominator is 48 decisions from seven selected failures
and four starting positions, not an independent sample of 48 tasks. Two false
claims describe hypothetical final-turn replies: the actual game stops at
clock 100 before Black can move. Those are not counted as actual rook losses.
The ambiguous c5 parenthetical in m8 trial 1 step 12 is not used as an
established error; its explicit claim that Kd4 keeps the rook safe is
independently refuted by the geometrically legal Kxd7.

All original commands were legal and correctly formatted. No false completion
claim was observed. No hidden chain of thought was inspected or inferred.
This is a post-hoc assistant review with deterministic chess checks;
independent human annotation and inter-rater agreement remain pending.

The only harmful reply effects resolved by the frozen M2 primary Holm family
are m4 trial 0 step 3 (Ke2), m4 trial 0 step 5 (Rd1+), and m4 trial 1 step 1
(Rh3). All other 45 comparisons remain unresolved. The intervals retained
from M2 are pointwise 95% intervals, not family-wise intervals.

An observed mistake does not establish its causal mechanism. The intervention
forces the entire original reply, including prose and command. For example,
m8 trial 0 step 3 actually loses its rook, but both M2 arms win 0/30; a harmful
intervention effect is unresolved. Tablebase loss of a feasible win is also
distinct from a model's probability of repair.

## Explicit model transfer

[fork_transfer](../../m3_runtime/transfer.py) implements a separate policy
intervention. The original vendor fork restores the saved model and sampling
parameters and therefore cannot be used to switch models just by editing YAML.
The vendor implementation and all M2 experiment files remain unchanged.

The new path requires an explicit target model, arm and job ID. It restores the
complete saved public message history, board, counters, limits, templates,
agent configuration and harness metadata. It verifies every non-model context
field, then takes a new child checkpoint recording the deliberate model change.
Target sampling parameters replace the original parameters; they are not merged.
An unsupported model or incompatible checkpoint fails before execution.

The keep arm verifies the original tape chain, reply digest, prefix and board,
then forces that reply once. All subsequent model calls use the target policy.
The redecide arm uses the target at the decision boundary. A forced reply still
consumes one original step. The default model transport refuses inference;
there is no credential loader or live execution command in this preparation.
The optional guarded transport must be explicitly injected by a future executor.

The registry supports the original Haiku 5.5 policy and the proposed pinned
Haiku 4.5 target `anthropic/claude-haiku-4-5-20251001`. Haiku 4.5 uses a declared
4,096-token enabled-thinking budget; Haiku 5.5 uses adaptive thinking. Both
cap output at 16,000 tokens and disable silent parameter dropping. Thus a future
comparison is a **declared model-policy transfer**, not isolation of model
weights alone. The saved source uses an alias; this preparation cannot create
an immutable historical provider model digest retroactively.

## Model-specific spending controls

[policies.py](../../m3_runtime/policies.py) and
[budget.py](../../m3_runtime/budget.py) use integer nanodollars and one
transactional SQLite cap shared across models and processes. Each request
reserves its model's maximum possible input/cache-write plus output charge:

| Model | Input bound | Output bound | Maximum reservation / request |
|---|---:|---:|---:|
| Haiku 5.5 | 1,000,000 | 16,000 | $0.665 |
| Haiku 4.5 | 200,000 | 16,000 | $0.330 |

These are conservative request reservations, not forecasts or approved spending.
The target reservation is lower because its context bound is smaller; at short
contexts its standard per-token rates are ten times the source model's rates.
Rates and assumptions are recorded in [model_policies.json](model_policies.json),
checked against [official pricing](https://platform.claude.com/docs/en/about-claude/pricing)
on November 20. The
[Haiku 4.5 model specification](https://platform.claude.com/docs/en/models/haiku-4-5/overview)
and [thinking documentation](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
support its declared context/thinking policy. Recheck prices and API compatibility
before any separately authorized live pilot.

Settlement requires the actual response model identity to match the pinned
allowlist, and prices that model's inclusive output (including reasoning),
uncached input, cache writes and reads. Conflicting/missing usage, an unexpected
model, unrecognized billing tier, or ambiguous failure retains the full maximum.
Only documented pre-inference rejection statuses can release a request for free.
Unsettled and uncertain liabilities survive restart; the cap and price registry
cannot silently change. The transport stops on failure, disables retries, and
retains response identity/usage accounting. Context is screened conservatively
without truncating history; this is not an exact tokenizer.

## Verification and reproduction

[preflight.json](preflight.json) records **192** successful restorations:
48 decisions × 2 models × 2 arms. All model queries without an injected transport
fail closed. **14** complete continuations (seven dialogues × two arms) replay
through Haiku 4.5-shaped mocked responses, totaling 89 mock dispatches. They
match the original final board and public conversation, verify target request
and response identities, and verify force-once behavior. Any simulated ledger
charges in that file are test accounting, not real expenditure.

[test_results.json](test_results.json) records **55 passing tests**: the 30
existing regressions and 25 new accounting/transfer checks. These include
concurrent mixed-model reservations, cache/long-context prices, durable unknown
liabilities, wrong response models, format-error charges, rejection handling,
read-only inputs and the complete transfer preflight. Network connections are
blocked before harness imports; no API credential is read or provider probe made.
The only pytest warning concerns assertion rewriting of an already loaded module.

With the original local evidence inputs and the existing locked environment:

```bash
.venv/bin/python scripts/build_m3_taxonomy.py
.venv/bin/python scripts/preflight_m3_offline.py
.venv/bin/python scripts/verify_m3_offline.py
```

All writable stores and ledgers are temporary. Referenced source databases,
checkpoint blobs, tapes, M2 manifest and profile table are hashed before/after
the preflight and unchanged. The preparation does not validate live provider
compatibility, measure transfer effects, certify M3, or authorize use of the
remaining M2 allowance. A paid stage still requires its own frozen design,
explicit budget, and bounded live compatibility pilot.
