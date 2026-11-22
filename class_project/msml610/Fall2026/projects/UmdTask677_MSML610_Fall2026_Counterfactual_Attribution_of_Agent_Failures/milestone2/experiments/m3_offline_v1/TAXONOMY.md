# Original chess failure taxonomy

Reviewed all 7 failed dialogues and 48 decisions across 4 starting positions. API cost: $0.

This is a post-hoc assistant review of recorded public text with deterministic chess checks. Independent human annotation has not been performed. The 7 complete histories are in dialogues.json; every decision has checkpoint, reply and tape identities in taxonomy.json.

| Observed label | Decisions / 48 | Runs / 7 |
|---|---:|---:|
| clock_win_lost | 5 | 5 |
| board_revisit | 4 | 3 |
| false_attack_or_reply_claim | 8 | 7 |
| actual_rook_loss | 2 | 2 |

Labels overlap. Five trajectories end at the fifty-move limit; two end after actual rook captures. Eight replies contain verified false attack or legal-reply claims, including two final-turn hypothetical claims where the clock prevents any Black reply. Four decisions revisit a board while spending clock. Eight planning or textual interpretations remain explicitly uncertain; a decision may have both a confirmed error and a separate uncertain interpretation.

All 48 original commands are legal, with no recorded format errors. No false completion claim was observed. These zero counts are bounded to the original seven dialogues.

## Observations and measured effects

Only three replies have a harmful effect resolved by the frozen M2 primary Holm-corrected family: m4 trial 0 step 3 (Ke2), m4 trial 0 step 5 (Rd1+), and m4 trial 1 step 1 (Rh3). The other 45 are unresolved. Repair gain is P(win | redecide) − P(win | keep entire original reply). Intervals below are the existing pointwise 95% intervals, not simultaneous intervals; discovery status uses Holm p < 0.05 across all 48 primary comparisons.

Ke2 makes a false rook-ray claim without immediately losing the theoretical win, yet has a resolved harmful reply effect. Conversely, m8 trial 0's Ra3 demonstrably hangs the rook, but both M2 arms win 0/30: its intervention effect remains unresolved. Do not turn an observed mistake into a statistically demonstrated mechanism. Clock-aware tablebase pivots establish loss of a feasible perfect-play win, not the probability of repair under this agent.

The taxonomy does not establish sparse versus diffuse failure clusters, general model weakness, or transferability. It is suitable for selecting follow-up hypotheses, with post-hoc selection disclosed. No new statistical tests or paid continuations were performed.

## Decision-by-decision review

### krk-m3-1_trial0_step001 — play move Rb2

Rb2 confines the king to c1/e1; the stated immediate reply set is correct.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.033, interval [-0.127, 0.197], Holm p=1.

### krk-m3-1_trial0_step002 — play move Kc3

Kc3 protects b2 and leaves only Kd1. Locally correct reply reasoning nevertheless loses the clock-aware theoretical win.

Observed labels: clock_win_lost. Uncertain interpretation: False. M2 status: unresolved; G=0.033, interval [-0.083, 0.167], Holm p=1.

### krk-m3-1_trial0_step003 — play move Kd3

Kd3 leaves c1/e1 as stated. The position had already lost its clock-aware win; no additional local error established.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m3-1_trial0_step004 — play move Ke3

Ke3 leaves d1/f1 as stated. No new factual error established in this reply.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m3-1_trial0_step005 — play move Kd3

Kd3 returns to the earlier board with four fewer half-moves. The claim that this is most restrictive is not established by the transcript.

Observed labels: board_revisit. Uncertain interpretation: True. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m3-1_trial0_step006 — play move Rb1+

Rb1+ leaves Kf2 as stated. This correct immediate check does not restore the clock-aware win.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m3-1_trial0_step007 — play move Rb2+

Acknowledges no mate in one. Lists g2 as a possible escape although the rook on b2 attacks g2; these are hypothetical replies because the game ends at clock 100 immediately after White moves.

Observed labels: false_attack_or_reply_claim. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m3-1_trial1_step001 — play move Rb2

Rb2 leaves c1/e1 as stated; no factual error established.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.133, interval [-0.029, 0.305], Holm p=1.

### krk-m3-1_trial1_step002 — play move Kc3

Kc3 loses the clock-aware win. The stated b1 alternative is illegal because the rook on b2 attacks b1; only Kd1 is legal.

Observed labels: false_attack_or_reply_claim, clock_win_lost. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m3-1_trial1_step003 — play move Kd3

Kd3 leaves c1/e1 as stated, from an already clock-lost position.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m3-1_trial1_step004 — play move Ke3

Ke3 leaves d1/f1 as stated; no new factual error established.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m3-1_trial1_step005 — play move Kd3

Kd3 repeats the board after step 3 while consuming four half-moves; c1/e1 is the correct immediate reply set.

Observed labels: board_revisit. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m3-1_trial1_step006 — play move Ke3

Ke3 repeats the board after step 4. Expresses uncertainty about a forced mate in two; this is not a false completion claim.

Observed labels: board_revisit. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m3-1_trial1_step007 — play move Rb1+

Rb1+ does not mate, as acknowledged. The geometrical c2 escape is legal, but clock 100 terminates play before any Black reply.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m4-1_trial0_step001 — play move Ke1

Ke1 protects the rook plan and covers f1/f2. Rejecting Rg3+ because of Kxg3 is sound. The primary corrected analysis does not resolve a helpful effect despite its negative point estimate.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=-0.333, interval [-0.532, -0.081], Holm p=0.840227.

### krk-m4-1_trial0_step002 — play move Rd2

Rd2 is protected by Ke1 and leaves only Kh1 as stated. No factual error established.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=-0.300, interval [-0.492, -0.072], Holm p=0.87603.

### krk-m4-1_trial0_step003 — play move Ke2

Ke2 blocks its own rook's second-rank ray. Contrary to the only-Kg1 claim, Kh2 and Kg2 are also legal. Theoretical winning status survives, but M2 resolves a harmful keep-versus-redecide effect for this entire reply.

Observed labels: false_attack_or_reply_claim. Uncertain interpretation: False. M2 status: resolved_harmful_reply_effect; G=0.667, interval [0.428, 0.799], Holm p=1.71079e-05.

### krk-m4-1_trial0_step004 — play move Rd3

Rd3 reply lists f1 among Black's choices; Ke2 attacks f1. The other listed g1/h1/h2 replies are legal. The causal effect remains unresolved.

Observed labels: false_attack_or_reply_claim. Uncertain interpretation: False. M2 status: unresolved; G=-0.167, interval [-0.378, 0.067], Holm p=1.

### krk-m4-1_trial0_step005 — play move Rd1+

Rd1+ has the stated h2/g2 replies but loses the clock-aware theoretical win. The promise to work out mate after the reply does not establish a feasible plan; M2 resolves a harmful reply effect.

Observed labels: clock_win_lost. Uncertain interpretation: True. M2 status: resolved_harmful_reply_effect; G=0.367, interval [0.180, 0.545], Holm p=0.0149838.

### krk-m4-1_trial0_step006 — play move Ra1

Ra1 leaves g3/h3/h2 as stated; the clock-aware win had already been lost.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m4-1_trial0_step007 — play move Ra3+

Ra3+ is followed by Kf4. The reply acknowledges a forced mate in two is not established; its proposed future plan remains unverified.

Observed labels: none established. Uncertain interpretation: True. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m4-1_trial0_step008 — play move Ra4+

Ra4+ is not mate as acknowledged. Escape examples are non-exhaustive, not an explicit only-replies assertion; omission of Kg3 alone is not labeled a false claim.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m4-1_trial1_step001 — play move Rh3

Rh3 is claimed uncapturable with only Kg1 available. Kxh3 is legal and is actually played, losing the rook and ending in insufficient material. M2 resolves a harmful effect for this reply.

Observed labels: false_attack_or_reply_claim, actual_rook_loss. Uncertain interpretation: False. M2 status: resolved_harmful_reply_effect; G=0.367, interval [0.180, 0.545], Holm p=0.0149838.

### krk-m6-1_trial0_step001 — play move Rg6

Rg6 confines Black to ranks 7/8 as stated; no factual error established.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=-0.200, interval [-0.378, -0.024], Holm p=1.

### krk-m6-1_trial0_step002 — play move Rg7

Rg7 confines Black to rank 8. General rank examples are not treated as an exhaustive immediate move list.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=-0.133, interval [-0.341, 0.090], Holm p=1.

### krk-m6-1_trial0_step003 — play move Kd7

Kd7 blocks its own rook's seventh-rank ray. The claim that Black must stay on rank 8 is false: Ka7 and Kb7 are legal. Theoretical winning status survives; Holm-corrected causal evidence is unresolved.

Observed labels: false_attack_or_reply_claim. Uncertain interpretation: False. M2 status: unresolved; G=0.267, interval [0.042, 0.461], Holm p=1.

### krk-m6-1_trial0_step004 — play move Rg8

Rg8 leaves a6/a7/b6 as stated. This boundary is still theoretically winning; the clock pivot occurs at the next decision, not here.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.267, interval [0.098, 0.444], Holm p=0.205878.

### krk-m6-1_trial0_step005 — play move Kd6

Kd6 has the stated local replies, but changes clock/DTZ feasibility from 89+9 to 91+13 and loses the theoretical win. Statistical harmful-effect evidence is unresolved.

Observed labels: clock_win_lost. Uncertain interpretation: False. M2 status: unresolved; G=0.033, interval [-0.083, 0.167], Holm p=1.

### krk-m6-1_trial0_step006 — play move Rb8+

Rb8+ forces Black off the b-file as stated; the clock-aware win is already lost.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m6-1_trial0_step007 — play move Ke5

Ke5 avoids the proposed Rb4+ line that would allow Kxb4. This tactical caution is correct; no new factual error established.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m6-1_trial0_step008 — play move Rc8+

Rc8+ cannot be answered by Kd4 because Ke5 attacks d4, as stated. No new factual error established.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m6-1_trial0_step009 — play move Rd8+

Rd8+ is not immediately capturable; doubts about mate in two are not labeled a false claim.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m6-1_trial0_step010 — play move Rc8+

Rc8+ does not mate; the reply acknowledges the draw. Clock 100 ends play before a Black reply.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m8-1_trial0_step001 — play move Rh3+

Rh3+ begins a checking/confinement plan. The generic plan is not sufficiently specified to certify or refute from prose alone.

Observed labels: none established. Uncertain interpretation: True. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m8-1_trial0_step002 — play move Kd4

Kd4 keeps the third rank covered by Rh3 and leaves a5/b4/b5 as stated.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m8-1_trial0_step003 — play move Ra3

Ra3 is claimed to leave only Kb5. Kxa3 is legal and actually occurs, losing the rook and drawing. Both M2 arms had zero wins, so a harmful intervention effect is not statistically resolved.

Observed labels: false_attack_or_reply_claim, actual_rook_loss. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m8-1_trial1_step001 — play move Rh3+

Rh3+ leaves a2/b2/a4/b4 as stated; no factual error established.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.033, interval [-0.083, 0.167], Holm p=1.

### krk-m8-1_trial1_step002 — play move Kd4

Kd4 keeps the third rank covered as stated; no factual error established.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m8-1_trial1_step003 — play move Kd5

Kd5 leaves a4/a5/b5 as stated; no factual error established.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.067, interval [-0.057, 0.213], Holm p=1.

### krk-m8-1_trial1_step004 — play move Rh4

Rh4 leaves a5/a6/b6 as stated; no factual error established.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.136, 0.136], Holm p=1.

### krk-m8-1_trial1_step005 — play move Rb4+

Rb4+ has the stated local replies but loses the clock-aware theoretical win: 85+15 becomes 87+15. Its harmful effect is statistically unresolved.

Observed labels: clock_win_lost. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m8-1_trial1_step006 — play move Rh4

Rh4 revisits the board after step 4 with four fewer half-moves. Avoiding Rb7+ because of Kxb7 is correct; the future Rh7+ plan is unverified.

Observed labels: board_revisit. Uncertain interpretation: True. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m8-1_trial1_step007 — play move Rh7

Rh7 leaves a5/a6/b5 as stated; no new factual error established.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m8-1_trial1_step008 — play move Ra7

Ra7 leaves b4/b6 as stated. The broad c-file language is evaluated locally: c4/c5/c6 are covered by Kd5; no exhaustive whole-file claim is imposed.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m8-1_trial1_step009 — play move Kd4

Kd4 leaves b3/b5 as stated. Whether this is the best remaining plan is unverified; the position is already clock-lost.

Observed labels: none established. Uncertain interpretation: True. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m8-1_trial1_step010 — play move Kc3

Kc3 leaves b6/c5/c6 as stated. The phrase keeps the net tight is evaluative and not independently demonstrated.

Observed labels: none established. Uncertain interpretation: True. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m8-1_trial1_step011 — play move Rd7

Rd7 moves the rook away from the real Kxa7 threat. The reply acknowledges the short clock and lack of mate in two.

Observed labels: none established. Uncertain interpretation: False. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.

### krk-m8-1_trial1_step012 — play move Kd4

Kd4 does not mate, as acknowledged. The claim that it keeps the rook safe is false geometrically: Black could play Kxd7. Clock 100 ends the actual game first, so no rook capture occurs. The c5 parenthetical may describe pre-move alternatives; that interpretation is uncertain and is not counted as a second factual error.

Observed labels: false_attack_or_reply_claim. Uncertain interpretation: True. M2 status: unresolved; G=0.000, interval [-0.114, 0.114], Holm p=1.
