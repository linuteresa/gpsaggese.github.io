# Independent review sheet — M3 failure taxonomy

First review dated 2026-11-20, 48 decisions across 7 failed dialogues and 4 positions.

Fill in `reviewer_labels`, `reviewer_uncertain`, `reviewer_note` and `agree_with_first` in `taxonomy_review_sheet.csv`, then run `scripts/diff_taxonomy_review.py`.
Do not edit `taxonomy.json` or the `m2_*` columns: those are frozen.

## Label vocabulary

- **`false_attack_or_reply_claim`** — A specific factual statement in the public reply contradicts legal-move geometry. Not an inference about hidden reasoning.

- **`actual_rook_loss`** — The recorded Black reply captures the White rook, causing insufficient-material draw.

- **`clock_win_lost`** — This decision changes a clock-aware Syzygy winning position to a non-winning position while the rook remains; operational evidence of inadequate clock planning, not a measured intervention effect.

- **`board_revisit`** — The board, turn, castling and en-passant fields recur within a run, with a larger half-move clock. A descriptive inefficiency, not proof of causation or threefold repetition.

Leave `reviewer_labels` empty for no label. Separate several labels with `|`.
`reviewer_uncertain` is `True` or `False`: the reply's planning or wording is open to more than one reading, separately from any factual error.

## Decisions

### krk-m3-1 trial 0

#### `krk-m3-1_trial0_step001` — step 1: `play move Rb2`

- Position before: `8/8/8/8/1R1K4/8/8/3k4 w - - 87 1`
- Position after: `8/8/8/8/3K4/8/1R6/2k5 w - - 89 2`
- Tablebase: win dtz=5 clock=87 -> win dtz=11 clock=89
- M2: gain 0.03333333333333333, Holm p 1.0, keep 2/30, re-decide 3/30

> Rb2 cuts off the second rank, so Black's king on d1 can only move to c1 or e1 and is confined to the first rank. That starts the box, and I'll reassess after Black's reply.

First review: _no label_ — Rb2 confines the king to c1/e1; the stated immediate reply set is correct.

Your verdict: _______________________________________________

#### `krk-m3-1_trial0_step002` — step 2: `play move Kc3`

- Position before: `8/8/8/8/3K4/8/1R6/2k5 w - - 89 2`
- Position after: `8/8/8/8/8/2K5/1R6/3k4 w - - 91 3`
- Tablebase: win dtz=11 clock=89 -> win dtz=11 clock=91
- M2: gain 0.03333333333333333, Holm p 1.0, keep 0/30, re-decide 1/30

> Black's king on c1 attacks my rook on b2, so I must address that. Kc3 defends the rook and leaves Black only the move Kd1, while keeping the box tight.

First review: `clock_win_lost` — Kc3 protects b2 and leaves only Kd1. Locally correct reply reasoning nevertheless loses the clock-aware theoretical win.

Your verdict: _______________________________________________

#### `krk-m3-1_trial0_step003` — step 3: `play move Kd3`

- Position before: `8/8/8/8/8/2K5/1R6/3k4 w - - 91 3`
- Position after: `8/8/8/8/8/3K4/1R6/4k3 w - - 93 4`
- Tablebase: win dtz=11 clock=91 -> win dtz=9 clock=93
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Rb1+ now fails because Black escapes to e2, so I'll first play Kd3. That covers c2, d2 and e2, so Black must step to c1 or e1 and the rook can then deliver mate on the first rank.

First review: _no label_ — Kd3 leaves c1/e1 as stated. The position had already lost its clock-aware win; no additional local error established.

Your verdict: _______________________________________________

#### `krk-m3-1_trial0_step004` — step 4: `play move Ke3`

- Position before: `8/8/8/8/8/3K4/1R6/4k3 w - - 93 4`
- Position after: `8/8/8/8/8/4K3/1R6/3k4 w - - 95 5`
- Tablebase: win dtz=9 clock=93 -> win dtz=9 clock=95
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> The rook on b2 already confines Black to the first rank, and Kd3 covers c2, d2 and e2. Moving the king to e3 also covers f2, so Black's only moves are to d1 or f1 and the box stays tight for a rook check next move.

First review: _no label_ — Ke3 leaves d1/f1 as stated. No new factual error established in this reply.

Your verdict: _______________________________________________

#### `krk-m3-1_trial0_step005` — step 5: `play move Kd3`

- Position before: `8/8/8/8/8/4K3/1R6/3k4 w - - 95 5`
- Position after: `8/8/8/8/8/3K4/1R6/4k3 w - - 97 6`
- Tablebase: win dtz=9 clock=95 -> win dtz=9 clock=97
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Kd3 covers c2, d2 and e2, so Black's king on d1 can only go to c1 or e1 while the rook keeps it on the first rank. I haven't found a forced mate within the remaining moves, so this is the most restrictive move available.

First review: `board_revisit` **uncertain** — Kd3 returns to the earlier board with four fewer half-moves. The claim that this is most restrictive is not established by the transcript.

Your verdict: _______________________________________________

#### `krk-m3-1_trial0_step006` — step 6: `play move Rb1+`

- Position before: `8/8/8/8/8/3K4/1R6/4k3 w - - 97 6`
- Position after: `8/8/8/8/8/3K4/5k2/1R6 w - - 99 7`
- Tablebase: win dtz=9 clock=97 -> win dtz=15 clock=99
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> I don't see a forced mate in the two moves left, so I'll keep the rook's first-rank box and give check with Rb1+. Black's escape to f2 is the only way out.

First review: _no label_ — Rb1+ leaves Kf2 as stated. This correct immediate check does not restore the clock-aware win.

Your verdict: _______________________________________________

#### `krk-m3-1_trial0_step007` — step 7: `play move Rb2+`

- Position before: `8/8/8/8/8/3K4/5k2/1R6 w - - 99 7`
- Position after: `8/8/8/8/8/3K4/1R3k2/8 b - - 100 7`
- Tablebase: win dtz=15 clock=99 -> draw dtz=0 clock=100
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> With one move left, no move gives checkmate. Rb2+ checks but Black escapes to e1, f1, g1, f3, g3 or g2, so the game will end in a draw, and I'll play the check anyway.

First review: `false_attack_or_reply_claim` — Acknowledges no mate in one. Lists g2 as a possible escape although the rook on b2 attacks g2; these are hypothetical replies because the game ends at clock 100 immediately after White moves.

Your verdict: _______________________________________________

### krk-m3-1 trial 1

#### `krk-m3-1_trial1_step001` — step 1: `play move Rb2`

- Position before: `8/8/8/8/1R1K4/8/8/3k4 w - - 87 1`
- Position after: `8/8/8/8/3K4/8/1R6/2k5 w - - 89 2`
- Tablebase: win dtz=5 clock=87 -> win dtz=11 clock=89
- M2: gain 0.13333333333333333, Holm p 1.0, keep 1/30, re-decide 5/30

> Rb2 cuts off the second rank, so Black's king on d1 can only move to c1 or e1. That keeps the rook safe and confines Black while my king comes closer.

First review: _no label_ — Rb2 leaves c1/e1 as stated; no factual error established.

Your verdict: _______________________________________________

#### `krk-m3-1_trial1_step002` — step 2: `play move Kc3`

- Position before: `8/8/8/8/3K4/8/1R6/2k5 w - - 89 2`
- Position after: `8/8/8/8/8/2K5/1R6/3k4 w - - 91 3`
- Tablebase: win dtz=11 clock=89 -> win dtz=11 clock=91
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Kc3 protects the rook on b2 and covers b2, c2 and d2, so Black's king can only go to b1 or d1 and cannot take the rook.

First review: `false_attack_or_reply_claim` `clock_win_lost` — Kc3 loses the clock-aware win. The stated b1 alternative is illegal because the rook on b2 attacks b1; only Kd1 is legal.

Your verdict: _______________________________________________

#### `krk-m3-1_trial1_step003` — step 3: `play move Kd3`

- Position before: `8/8/8/8/8/2K5/1R6/3k4 w - - 91 3`
- Position after: `8/8/8/8/8/3K4/1R6/4k3 w - - 93 4`
- Tablebase: win dtz=11 clock=91 -> win dtz=9 clock=93
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Kd3 takes the d2 and e2 squares, so Black's king on d1 can only go to c1 or e1 and the rook on b2 still cuts off rank 2. From there I can look for a rook check on the back rank to finish.

First review: _no label_ — Kd3 leaves c1/e1 as stated, from an already clock-lost position.

Your verdict: _______________________________________________

#### `krk-m3-1_trial1_step004` — step 4: `play move Ke3`

- Position before: `8/8/8/8/8/3K4/1R6/4k3 w - - 93 4`
- Position after: `8/8/8/8/8/4K3/1R6/3k4 w - - 95 5`
- Tablebase: win dtz=9 clock=93 -> win dtz=9 clock=95
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Ke3 takes away d2, e2 and f2, so Black's king on e1 can only go to d1 or f1. The rook on b2 keeps rank 2 sealed while I look for a rank-1 check to finish.

First review: _no label_ — Ke3 leaves d1/f1 as stated; no new factual error established.

Your verdict: _______________________________________________

#### `krk-m3-1_trial1_step005` — step 5: `play move Kd3`

- Position before: `8/8/8/8/8/4K3/1R6/3k4 w - - 95 5`
- Position after: `8/8/8/8/8/3K4/1R6/4k3 w - - 97 6`
- Tablebase: win dtz=9 clock=95 -> win dtz=9 clock=97
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Kd3 covers d2 and keeps the rook on b2 sealing rank 2, so Black's king on d1 must step to c1 or e1. That leaves a rook check on the back rank as the finishing idea.

First review: `board_revisit` — Kd3 repeats the board after step 3 while consuming four half-moves; c1/e1 is the correct immediate reply set.

Your verdict: _______________________________________________

#### `krk-m3-1_trial1_step006` — step 6: `play move Ke3`

- Position before: `8/8/8/8/8/3K4/1R6/4k3 w - - 97 6`
- Position after: `8/8/8/8/8/4K3/1R6/3k4 w - - 99 7`
- Tablebase: win dtz=9 clock=97 -> win dtz=9 clock=99
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> I don't see a forced mate in two from here, so I'll play Ke3, which keeps rank 2 covered and steers the king toward the e1/f1/d1 mating net.

First review: `board_revisit` — Ke3 repeats the board after step 4. Expresses uncertainty about a forced mate in two; this is not a false completion claim.

Your verdict: _______________________________________________

#### `krk-m3-1_trial1_step007` — step 7: `play move Rb1+`

- Position before: `8/8/8/8/8/4K3/1R6/3k4 w - - 99 7`
- Position after: `8/8/8/8/8/4K3/8/1R1k4 b - - 100 7`
- Tablebase: win dtz=9 clock=99 -> draw dtz=0 clock=100
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> I checked for mate in one and there isn't one. Rb1+ checks but Black can escape to c2, and every other rook check also leaves an escape square, so I'll play the check and see what happens.

First review: _no label_ — Rb1+ does not mate, as acknowledged. The geometrical c2 escape is legal, but clock 100 terminates play before any Black reply.

Your verdict: _______________________________________________

### krk-m4-1 trial 0

#### `krk-m4-1_trial0_step001` — step 1: `play move Ke1`

- Position before: `8/8/8/8/8/3R4/4K1k1/8 w - - 85 1`
- Position after: `8/8/8/8/8/3R4/8/4K1k1 w - - 87 2`
- Tablebase: win dtz=7 clock=85 -> win dtz=7 clock=87
- M2: gain -0.3333333333333333, Holm p 0.8402265011827871, keep 21/30, re-decide 11/30

> Rg3+ would hang the rook to Kxg3, so I'll avoid it. Ke1 keeps the rook safe on d3, still cuts off the third rank, and covers f1 and f2, leaving Black only g1, h1 and h2.

First review: _no label_ — Ke1 protects the rook plan and covers f1/f2. Rejecting Rg3+ because of Kxg3 is sound. The primary corrected analysis does not resolve a helpful effect despite its negative point estimate.

Your verdict: _______________________________________________

#### `krk-m4-1_trial0_step002` — step 2: `play move Rd2`

- Position before: `8/8/8/8/8/3R4/8/4K1k1 w - - 87 2`
- Position after: `8/8/8/8/8/8/3R4/4K2k w - - 89 3`
- Tablebase: win dtz=7 clock=87 -> win dtz=5 clock=89
- M2: gain -0.3, Holm p 0.8760300453854877, keep 26/30, re-decide 17/30

> Rd2 is protected by my king on e1 and cuts off the second rank. Black's only legal reply is Kh1, which pushes the king into the corner for a later rook check on the h-file.

First review: _no label_ — Rd2 is protected by Ke1 and leaves only Kh1 as stated. No factual error established.

Your verdict: _______________________________________________

#### `krk-m4-1_trial0_step003` — step 3: `play move Ke2`

- Position before: `8/8/8/8/8/8/3R4/4K2k w - - 89 3`
- Position after: `8/8/8/8/8/8/3RK1k1/8 w - - 91 4`
- Tablebase: win dtz=5 clock=89 -> win dtz=7 clock=91
- M2: gain 0.6666666666666666, Holm p 1.7107946274196676e-05, keep 5/30, re-decide 25/30

> Ke2 is safe and leaves Black only Kg1, since g2 and h2 are covered by the rook on d2. Then Kf3 and a rook check on the first rank should lead to mate.

First review: `false_attack_or_reply_claim` — Ke2 blocks its own rook's second-rank ray. Contrary to the only-Kg1 claim, Kh2 and Kg2 are also legal. Theoretical winning status survives, but M2 resolves a harmful keep-versus-redecide effect for this entire reply.

Your verdict: _______________________________________________

#### `krk-m4-1_trial0_step004` — step 4: `play move Rd3`

- Position before: `8/8/8/8/8/8/3RK1k1/8 w - - 91 4`
- Position after: `8/8/8/8/8/3R4/4K3/6k1 w - - 93 5`
- Tablebase: win dtz=7 clock=91 -> win dtz=5 clock=93
- M2: gain -0.16666666666666666, Holm p 1.0, keep 12/30, re-decide 7/30

> Rd3 is a quiet move that controls the third rank, so Black's king on g2 can only go to f1, g1, h1 or h2. Ke2 still blocks the rook's line on the second rank, so no discovered check is needed yet.

First review: `false_attack_or_reply_claim` — Rd3 reply lists f1 among Black's choices; Ke2 attacks f1. The other listed g1/h1/h2 replies are legal. The causal effect remains unresolved.

Your verdict: _______________________________________________

#### `krk-m4-1_trial0_step005` — step 5: `play move Rd1+`

- Position before: `8/8/8/8/8/3R4/4K3/6k1 w - - 93 5`
- Position after: `8/8/8/8/8/8/4K1k1/3R4 w - - 95 6`
- Tablebase: win dtz=5 clock=93 -> win dtz=7 clock=95
- M2: gain 0.36666666666666664, Holm p 0.014983846870510612, keep 0/30, re-decide 11/30

> Rd1+ checks along the first rank and forces Black's king toward h2 or g2, where my king on e2 keeps it boxed in. I'll work out the mate from the reply.

First review: `clock_win_lost` **uncertain** — Rd1+ has the stated h2/g2 replies but loses the clock-aware theoretical win. The promise to work out mate after the reply does not establish a feasible plan; M2 resolves a harmful reply effect.

Your verdict: _______________________________________________

#### `krk-m4-1_trial0_step006` — step 6: `play move Ra1`

- Position before: `8/8/8/8/8/8/4K1k1/3R4 w - - 95 6`
- Position after: `8/8/8/8/8/6k1/4K3/R7 w - - 97 7`
- Tablebase: win dtz=7 clock=95 -> win dtz=9 clock=97
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Ra1 takes the whole first rank, so Black's king on g2 can only move to g3, h3 or h2, with f1, f2 and f3 already covered by my king on e2. This keeps the net tight while I look for a mating pattern.

First review: _no label_ — Ra1 leaves g3/h3/h2 as stated; the clock-aware win had already been lost.

Your verdict: _______________________________________________

#### `krk-m4-1_trial0_step007` — step 7: `play move Ra3+`

- Position before: `8/8/8/8/8/6k1/4K3/R7 w - - 97 7`
- Position after: `8/8/8/8/5k2/R7/4K3/8 w - - 99 8`
- Tablebase: win dtz=9 clock=97 -> win dtz=23 clock=99
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Mate in two isn't forced from here, since Black's king on g3 has several escape squares whatever I do. Ra3+ is a forcing check that keeps the rook safe on the third rank, so I'll play it and look for the follow-up.

First review: **uncertain** — Ra3+ is followed by Kf4. The reply acknowledges a forced mate in two is not established; its proposed future plan remains unverified.

Your verdict: _______________________________________________

#### `krk-m4-1_trial0_step008` — step 8: `play move Ra4+`

- Position before: `8/8/8/8/5k2/R7/4K3/8 w - - 99 8`
- Position after: `8/8/8/8/R4k2/8/4K3/8 b - - 100 8`
- Tablebase: win dtz=23 clock=99 -> draw dtz=0 clock=100
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> I have one move left, and no move mates Black's king on f4. Ra4+ is the strongest check, since it covers the fourth rank, but Black can still escape to e5, f5 or g5, so this likely ends in a draw.

First review: _no label_ — Ra4+ is not mate as acknowledged. Escape examples are non-exhaustive, not an explicit only-replies assertion; omission of Kg3 alone is not labeled a false claim.

Your verdict: _______________________________________________

### krk-m4-1 trial 1

#### `krk-m4-1_trial1_step001` — step 1: `play move Rh3`

- Position before: `8/8/8/8/8/3R4/4K1k1/8 w - - 85 1`
- Position after: `8/8/8/8/8/7k/4K3/8 w - - 0 2`
- Tablebase: win dtz=7 clock=85 -> draw dtz=0 clock=0
- M2: gain 0.36666666666666664, Holm p 0.014983846870510612, keep 0/30, re-decide 11/30

> Rh3 takes away almost all of Black's squares. It covers h1, h2 and g3, and my king covers f1 and f2, so Black's only legal reply is Kg1. The rook is also out of reach of the king, so it can't be captured.

First review: `false_attack_or_reply_claim` `actual_rook_loss` — Rh3 is claimed uncapturable with only Kg1 available. Kxh3 is legal and is actually played, losing the rook and ending in insufficient material. M2 resolves a harmful effect for this reply.

Your verdict: _______________________________________________

### krk-m6-1 trial 0

#### `krk-m6-1_trial0_step001` — step 1: `play move Rg6`

- Position before: `4K3/k7/8/6R1/8/8/8/8 w - - 81 1`
- Position after: `k3K3/8/6R1/8/8/8/8/8 w - - 83 2`
- Tablebase: win dtz=11 clock=81 -> win dtz=9 clock=83
- M2: gain -0.2, Holm p 1.0, keep 7/30, re-decide 1/30

> Rg6 cuts off the sixth rank, so Black's king is confined to ranks 7 and 8 on the queenside. That leaves my king free to walk toward the box and set up a rook-and-king mate.

First review: _no label_ — Rg6 confines Black to ranks 7/8 as stated; no factual error established.

Your verdict: _______________________________________________

#### `krk-m6-1_trial0_step002` — step 2: `play move Rg7`

- Position before: `k3K3/8/6R1/8/8/8/8/8 w - - 83 2`
- Position after: `1k2K3/6R1/8/8/8/8/8/8 w - - 85 3`
- Tablebase: win dtz=9 clock=83 -> win dtz=7 clock=85
- M2: gain -0.13333333333333333, Holm p 1.0, keep 10/30, re-decide 6/30

> Rg7 cuts off the seventh rank, confining Black's king to the 8th rank (a8, b8, c8). Then I can bring my king closer to set up mate.

First review: _no label_ — Rg7 confines Black to rank 8. General rank examples are not treated as an exhaustive immediate move list.

Your verdict: _______________________________________________

#### `krk-m6-1_trial0_step003` — step 3: `play move Kd7`

- Position before: `1k2K3/6R1/8/8/8/8/8/8 w - - 85 3`
- Position after: `8/1k1K2R1/8/8/8/8/8/8 w - - 87 4`
- Tablebase: win dtz=7 clock=85 -> win dtz=7 clock=87
- M2: gain 0.26666666666666666, Holm p 1.0, keep 4/30, re-decide 12/30

> Kd7 keeps Black boxed on the 8th rank (the rook covers the 7th, and the king covers c8) while my king heads toward b6, which is the square needed for a rook-on-the-8th-rank mate.

First review: `false_attack_or_reply_claim` — Kd7 blocks its own rook's seventh-rank ray. The claim that Black must stay on rank 8 is false: Ka7 and Kb7 are legal. Theoretical winning status survives; Holm-corrected causal evidence is unresolved.

Your verdict: _______________________________________________

#### `krk-m6-1_trial0_step004` — step 4: `play move Rg8`

- Position before: `8/1k1K2R1/8/8/8/8/8/8 w - - 87 4`
- Position after: `6R1/3K4/1k6/8/8/8/8/8 w - - 89 5`
- Tablebase: win dtz=7 clock=87 -> win dtz=9 clock=89
- M2: gain 0.26666666666666666, Holm p 0.20587780758113852, keep 0/30, re-decide 8/30

> Rg8 seals the 8th rank, so Black's king on b7 can only go to a6, a7 or b6, with c6, c7 and c8 covered by my king on d7. That keeps Black boxed in while I bring my king closer.

First review: _no label_ — Rg8 leaves a6/a7/b6 as stated. This boundary is still theoretically winning; the clock pivot occurs at the next decision, not here.

Your verdict: _______________________________________________

#### `krk-m6-1_trial0_step005` — step 5: `play move Kd6`

- Position before: `6R1/3K4/1k6/8/8/8/8/8 w - - 89 5`
- Position after: `6R1/8/3K4/1k6/8/8/8/8 w - - 91 6`
- Tablebase: win dtz=9 clock=89 -> win dtz=13 clock=91
- M2: gain 0.03333333333333333, Holm p 1.0, keep 0/30, re-decide 1/30

> Kd6 is legal (not adjacent to Black's king on b6) and covers c5, c6 and c7, so Black's king can only go to a5, a6, a7, b5 or b7. That tightens the box before I bring the rook in for mate.

First review: `clock_win_lost` — Kd6 has the stated local replies, but changes clock/DTZ feasibility from 89+9 to 91+13 and loses the theoretical win. Statistical harmful-effect evidence is unresolved.

Your verdict: _______________________________________________

#### `krk-m6-1_trial0_step006` — step 6: `play move Rb8+`

- Position before: `6R1/8/3K4/1k6/8/8/8/8 w - - 91 6`
- Position after: `1R6/8/3K4/8/2k5/8/8/8 w - - 93 7`
- Tablebase: win dtz=13 clock=91 -> win dtz=23 clock=93
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Rb8+ checks along the b-file, so Black's king must leave the b-file. That pushes it toward the a-file or the 4th rank, where my king can help build a box for mate.

First review: _no label_ — Rb8+ forces Black off the b-file as stated; the clock-aware win is already lost.

Your verdict: _______________________________________________

#### `krk-m6-1_trial0_step007` — step 7: `play move Ke5`

- Position before: `1R6/8/3K4/8/2k5/8/8/8 w - - 93 7`
- Position after: `1R6/8/8/4K3/8/2k5/8/8 w - - 95 8`
- Tablebase: win dtz=23 clock=93 -> win dtz=21 clock=95
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Rb4+ would just lose the rook to Kxb4, and checks on the c-file give Black too much room. Ke5 brings my king closer to the centre while keeping the rook safe, so I can start boxing Black's king in.

First review: _no label_ — Ke5 avoids the proposed Rb4+ line that would allow Kxb4. This tactical caution is correct; no new factual error established.

Your verdict: _______________________________________________

#### `krk-m6-1_trial0_step008` — step 8: `play move Rc8+`

- Position before: `1R6/8/8/4K3/8/2k5/8/8 w - - 95 8`
- Position after: `2R5/8/8/4K3/8/3k4/8/8 w - - 97 9`
- Tablebase: win dtz=21 clock=95 -> win dtz=23 clock=97
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Rc8+ checks along the c-file and pushes Black's king off it. Black cannot go to d4, which my king covers, so the king is still confined to the lower-left area.

First review: _no label_ — Rc8+ cannot be answered by Kd4 because Ke5 attacks d4, as stated. No new factual error established.

Your verdict: _______________________________________________

#### `krk-m6-1_trial0_step009` — step 9: `play move Rd8+`

- Position before: `2R5/8/8/4K3/8/3k4/8/8 w - - 97 9`
- Position after: `3R4/8/8/4K3/2k5/8/8/8 w - - 99 10`
- Tablebase: win dtz=23 clock=97 -> win dtz=21 clock=99
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Mate in two looks unlikely here, so I'll play the forcing check Rd8+ along the d-file to restrict Black's king and keep the rook safe. Black's king is not adjacent to the rook on d8, so it cannot capture.

First review: _no label_ — Rd8+ is not immediately capturable; doubts about mate in two are not labeled a false claim.

Your verdict: _______________________________________________

#### `krk-m6-1_trial0_step010` — step 10: `play move Rc8+`

- Position before: `3R4/8/8/4K3/2k5/8/8/8 w - - 99 10`
- Position after: `2R5/8/8/4K3/2k5/8/8/8 b - - 100 10`
- Tablebase: win dtz=21 clock=99 -> draw dtz=0 clock=100
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> I have one move left, and no move mates from here. Black's king on c4 always has an escape square after either checking move. I'll play Rc8+ to keep the pressure on, though the game will likely end in a draw.

First review: _no label_ — Rc8+ does not mate; the reply acknowledges the draw. Clock 100 ends play before a Black reply.

Your verdict: _______________________________________________

### krk-m8-1 trial 0

#### `krk-m8-1_trial0_step001` — step 1: `play move Rh3+`

- Position before: `8/8/8/8/4K3/k7/8/7R w - - 77 1`
- Position after: `8/8/8/8/k3K3/7R/8/8 w - - 79 2`
- Tablebase: win dtz=15 clock=77 -> win dtz=17 clock=79
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Rh3+ checks along the third rank and takes away several squares from the Black king, starting to confine it. I'll then bring my king in to finish the box.

First review: **uncertain** — Rh3+ begins a checking/confinement plan. The generic plan is not sufficiently specified to certify or refute from prose alone.

Your verdict: _______________________________________________

#### `krk-m8-1_trial0_step002` — step 2: `play move Kd4`

- Position before: `8/8/8/8/k3K3/7R/8/8 w - - 79 2`
- Position after: `8/8/8/8/1k1K4/7R/8/8 w - - 81 3`
- Tablebase: win dtz=17 clock=79 -> win dtz=15 clock=81
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> The rook on h3 already covers a3 and b3, so Black's king is limited to a5, b4 and b5. Moving my king to d4 brings it toward the queenside to help confine and mate.

First review: _no label_ — Kd4 keeps the third rank covered by Rh3 and leaves a5/b4/b5 as stated.

Your verdict: _______________________________________________

#### `krk-m8-1_trial0_step003` — step 3: `play move Ra3`

- Position before: `8/8/8/8/1k1K4/7R/8/8 w - - 81 3`
- Position after: `8/8/8/8/3K4/k7/8/8 w - - 0 4`
- Tablebase: win dtz=15 clock=81 -> draw dtz=0 clock=0
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Rb3+ would just lose the rook to Kxb3, since my king on d4 doesn't guard b3. Ra3 instead covers the a-file and the third rank, leaving Black only b5 as a legal king move.

First review: `false_attack_or_reply_claim` `actual_rook_loss` — Ra3 is claimed to leave only Kb5. Kxa3 is legal and actually occurs, losing the rook and drawing. Both M2 arms had zero wins, so a harmful intervention effect is not statistically resolved.

Your verdict: _______________________________________________

### krk-m8-1 trial 1

#### `krk-m8-1_trial1_step001` — step 1: `play move Rh3+`

- Position before: `8/8/8/8/4K3/k7/8/7R w - - 77 1`
- Position after: `8/8/8/8/k3K3/7R/8/8 w - - 79 2`
- Tablebase: win dtz=15 clock=77 -> win dtz=17 clock=79
- M2: gain 0.03333333333333333, Holm p 1.0, keep 0/30, re-decide 1/30

> Rh3+ checks along the third rank and cuts off b3, leaving Black only a2, b2, a4 or b4. That restricts the king while my king comes closer.

First review: _no label_ — Rh3+ leaves a2/b2/a4/b4 as stated; no factual error established.

Your verdict: _______________________________________________

#### `krk-m8-1_trial1_step002` — step 2: `play move Kd4`

- Position before: `8/8/8/8/k3K3/7R/8/8 w - - 79 2`
- Position after: `8/8/8/8/1k1K4/7R/8/8 w - - 81 3`
- Tablebase: win dtz=17 clock=79 -> win dtz=15 clock=81
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> The rook on the third rank keeps a3 and b3 covered, so I'll bring my king toward the queenside with Kd4. That keeps the box intact while Black's king stays on the edge.

First review: _no label_ — Kd4 keeps the third rank covered as stated; no factual error established.

Your verdict: _______________________________________________

#### `krk-m8-1_trial1_step003` — step 3: `play move Kd5`

- Position before: `8/8/8/8/1k1K4/7R/8/8 w - - 81 3`
- Position after: `8/8/8/1k1K4/8/7R/8/8 w - - 83 4`
- Tablebase: win dtz=15 clock=81 -> win dtz=13 clock=83
- M2: gain 0.06666666666666667, Holm p 1.0, keep 0/30, re-decide 2/30

> Rb3+ would just hang the rook to Kxb3, so I'll avoid it. Kd5 keeps the third rank sealed and covers c4 and c5, leaving Black only a4, a5 and b5.

First review: _no label_ — Kd5 leaves a4/a5/b5 as stated; no factual error established.

Your verdict: _______________________________________________

#### `krk-m8-1_trial1_step004` — step 4: `play move Rh4`

- Position before: `8/8/8/1k1K4/8/7R/8/8 w - - 83 4`
- Position after: `8/8/1k6/3K4/7R/8/8/8 w - - 85 5`
- Tablebase: win dtz=13 clock=83 -> win dtz=15 clock=85
- M2: gain 0.0, Holm p 1.0, keep 1/30, re-decide 1/30

> Rh4 cuts off the fourth rank, so Black's king can't reach a4 or b4, and Kd5 already covers c4, c5 and c6. That leaves Black only a5, a6 and b6, which keeps the king boxed toward the edge.

First review: _no label_ — Rh4 leaves a5/a6/b6 as stated; no factual error established.

Your verdict: _______________________________________________

#### `krk-m8-1_trial1_step005` — step 5: `play move Rb4+`

- Position before: `8/8/1k6/3K4/7R/8/8/8 w - - 85 5`
- Position after: `8/2k5/8/3K4/1R6/8/8/8 w - - 87 6`
- Tablebase: win dtz=15 clock=85 -> win dtz=15 clock=87
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Rb4+ checks along the b-file and takes away b5, b7 and the fourth rank. With my king on d5 already covering c5 and c6, Black can only go to a5, a6, a7 or c7, which pushes the king toward the edge.

First review: `clock_win_lost` — Rb4+ has the stated local replies but loses the clock-aware theoretical win: 85+15 becomes 87+15. Its harmful effect is statistically unresolved.

Your verdict: _______________________________________________

#### `krk-m8-1_trial1_step006` — step 6: `play move Rh4`

- Position before: `8/2k5/8/3K4/1R6/8/8/8 w - - 87 6`
- Position after: `8/8/1k6/3K4/7R/8/8/8 w - - 89 7`
- Tablebase: win dtz=15 clock=87 -> win dtz=15 clock=89
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Rb7+ would hang the rook to Kxb7, so I'll reposition along the fourth rank first. Rh4 keeps Black's king away from the fourth rank and prepares Rh7+ to confine it to the eighth rank.

First review: `board_revisit` **uncertain** — Rh4 revisits the board after step 4 with four fewer half-moves. Avoiding Rb7+ because of Kxb7 is correct; the future Rh7+ plan is unverified.

Your verdict: _______________________________________________

#### `krk-m8-1_trial1_step007` — step 7: `play move Rh7`

- Position before: `8/8/1k6/3K4/7R/8/8/8 w - - 89 7`
- Position after: `8/7R/8/1k1K4/8/8/8/8 w - - 91 8`
- Tablebase: win dtz=15 clock=89 -> win dtz=13 clock=91
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Rh7 cuts off the seventh rank. With my king on d5 covering c4, c5 and c6, Black can only move to a5, a6 or b5, which keeps the box tight while I bring the king closer.

First review: _no label_ — Rh7 leaves a5/a6/b5 as stated; no new factual error established.

Your verdict: _______________________________________________

#### `krk-m8-1_trial1_step008` — step 8: `play move Ra7`

- Position before: `8/7R/8/1k1K4/8/8/8/8 w - - 91 8`
- Position after: `8/R7/8/3K4/1k6/8/8/8 w - - 93 9`
- Tablebase: win dtz=13 clock=91 -> win dtz=17 clock=93
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Ra7 takes the a-file, and Kd5 already covers the c-file, so Black's king on b5 can only go to b4 or b6. That keeps the net tight while I bring my king closer.

First review: _no label_ — Ra7 leaves b4/b6 as stated. The broad c-file language is evaluated locally: c4/c5/c6 are covered by Kd5; no exhaustive whole-file claim is imposed.

Your verdict: _______________________________________________

#### `krk-m8-1_trial1_step009` — step 9: `play move Kd4`

- Position before: `8/R7/8/3K4/1k6/8/8/8 w - - 93 9`
- Position after: `8/R7/8/1k6/3K4/8/8/8 w - - 95 10`
- Tablebase: win dtz=17 clock=93 -> win dtz=17 clock=95
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Ra4+ would just hang the rook to Kxa4, so I'll avoid it. Kd4 takes c3, c4 and c5 away from Black's king, leaving only b3 and b5 as escape squares, and it brings my king closer to the mating net.

First review: **uncertain** — Kd4 leaves b3/b5 as stated. Whether this is the best remaining plan is unverified; the position is already clock-lost.

Your verdict: _______________________________________________

#### `krk-m8-1_trial1_step010` — step 10: `play move Kc3`

- Position before: `8/R7/8/1k6/3K4/8/8/8 w - - 95 10`
- Position after: `8/R7/1k6/8/8/2K5/8/8 w - - 97 11`
- Tablebase: win dtz=17 clock=95 -> win dtz=21 clock=97
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Kc3 takes away b4 and c4, leaving Black only b6, c5 and c6. Kd4 is the only square covering c5, so this keeps the net tight while I look for mate within the remaining moves.

First review: **uncertain** — Kc3 leaves b6/c5/c6 as stated. The phrase keeps the net tight is evaluative and not independently demonstrated.

Your verdict: _______________________________________________

#### `krk-m8-1_trial1_step011` — step 11: `play move Rd7`

- Position before: `8/R7/1k6/8/8/2K5/8/8 w - - 97 11`
- Position after: `8/3R4/2k5/8/8/2K5/8/8 w - - 99 12`
- Tablebase: win dtz=21 clock=97 -> win dtz=19 clock=99
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Black's king on b6 attacks my rook on a7, so the rook has to move. With only three half-moves left before the fifty-move draw, I can't force mate in two. Rd7 keeps the rook safe and covers the whole seventh rank, which keeps Black boxed in.

First review: _no label_ — Rd7 moves the rook away from the real Kxa7 threat. The reply acknowledges the short clock and lack of mate in two.

Your verdict: _______________________________________________

#### `krk-m8-1_trial1_step012` — step 12: `play move Kd4`

- Position before: `8/3R4/2k5/8/8/2K5/8/8 w - - 99 12`
- Position after: `8/3R4/2k5/8/3K4/8/8/8 b - - 100 12`
- Tablebase: win dtz=19 clock=99 -> draw dtz=0 clock=100
- M2: gain 0.0, Holm p 1.0, keep 0/30, re-decide 0/30

> Only one move remains before the fifty-move limit, and no move mates Black's king on c6 (b5, b6 and c5 stay open). I'll play the quiet Kd4, which keeps my rook safe.

First review: `false_attack_or_reply_claim` **uncertain** — Kd4 does not mate, as acknowledged. The claim that it keeps the rook safe is false geometrically: Black could play Kxd7. Clock 100 ends the actual game first, so no rook capture occurs. The c5 parenthetical may describe pre-move alternatives; that interpretation is uncertain and is not counted as a second factual error.

Your verdict: _______________________________________________
