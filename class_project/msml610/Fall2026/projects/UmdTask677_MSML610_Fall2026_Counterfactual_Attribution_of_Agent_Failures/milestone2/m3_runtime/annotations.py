"""Post-hoc transcript review, separate from the frozen M2 statistical analysis.

Notes concern public reply text, not hidden model reasoning. A second independent
human annotation and inter-rater agreement have not been performed.
"""

# Each entry is one original decision, in chronological order within a run.
NOTES = {
    (3, 0): [
        "Rb2 confines the king to c1/e1; the stated immediate reply set is correct.",
        "Kc3 protects b2 and leaves only Kd1. Locally correct reply reasoning nevertheless loses the clock-aware theoretical win.",
        "Kd3 leaves c1/e1 as stated. The position had already lost its clock-aware win; no additional local error established.",
        "Ke3 leaves d1/f1 as stated. No new factual error established in this reply.",
        "Kd3 returns to the earlier board with four fewer half-moves. The claim that this is most restrictive is not established by the transcript.",
        "Rb1+ leaves Kf2 as stated. This correct immediate check does not restore the clock-aware win.",
        "Acknowledges no mate in one. Lists g2 as a possible escape although the rook on b2 attacks g2; these are hypothetical replies because the game ends at clock 100 immediately after White moves.",
    ],
    (3, 1): [
        "Rb2 leaves c1/e1 as stated; no factual error established.",
        "Kc3 loses the clock-aware win. The stated b1 alternative is illegal because the rook on b2 attacks b1; only Kd1 is legal.",
        "Kd3 leaves c1/e1 as stated, from an already clock-lost position.",
        "Ke3 leaves d1/f1 as stated; no new factual error established.",
        "Kd3 repeats the board after step 3 while consuming four half-moves; c1/e1 is the correct immediate reply set.",
        "Ke3 repeats the board after step 4. Expresses uncertainty about a forced mate in two; this is not a false completion claim.",
        "Rb1+ does not mate, as acknowledged. The geometrical c2 escape is legal, but clock 100 terminates play before any Black reply.",
    ],
    (4, 0): [
        "Ke1 protects the rook plan and covers f1/f2. Rejecting Rg3+ because of Kxg3 is sound. The primary corrected analysis does not resolve a helpful effect despite its negative point estimate.",
        "Rd2 is protected by Ke1 and leaves only Kh1 as stated. No factual error established.",
        "Ke2 blocks its own rook's second-rank ray. Contrary to the only-Kg1 claim, Kh2 and Kg2 are also legal. Theoretical winning status survives, but M2 resolves a harmful keep-versus-redecide effect for this entire reply.",
        "Rd3 reply lists f1 among Black's choices; Ke2 attacks f1. The other listed g1/h1/h2 replies are legal. The causal effect remains unresolved.",
        "Rd1+ has the stated h2/g2 replies but loses the clock-aware theoretical win. The promise to work out mate after the reply does not establish a feasible plan; M2 resolves a harmful reply effect.",
        "Ra1 leaves g3/h3/h2 as stated; the clock-aware win had already been lost.",
        "Ra3+ is followed by Kf4. The reply acknowledges a forced mate in two is not established; its proposed future plan remains unverified.",
        "Ra4+ is not mate as acknowledged. Escape examples are non-exhaustive, not an explicit only-replies assertion; omission of Kg3 alone is not labeled a false claim.",
    ],
    (4, 1): [
        "Rh3 is claimed uncapturable with only Kg1 available. Kxh3 is legal and is actually played, losing the rook and ending in insufficient material. M2 resolves a harmful effect for this reply.",
    ],
    (6, 0): [
        "Rg6 confines Black to ranks 7/8 as stated; no factual error established.",
        "Rg7 confines Black to rank 8. General rank examples are not treated as an exhaustive immediate move list.",
        "Kd7 blocks its own rook's seventh-rank ray. The claim that Black must stay on rank 8 is false: Ka7 and Kb7 are legal. Theoretical winning status survives; Holm-corrected causal evidence is unresolved.",
        "Rg8 leaves a6/a7/b6 as stated. This boundary is still theoretically winning; the clock pivot occurs at the next decision, not here.",
        "Kd6 has the stated local replies, but changes clock/DTZ feasibility from 89+9 to 91+13 and loses the theoretical win. Statistical harmful-effect evidence is unresolved.",
        "Rb8+ forces Black off the b-file as stated; the clock-aware win is already lost.",
        "Ke5 avoids the proposed Rb4+ line that would allow Kxb4. This tactical caution is correct; no new factual error established.",
        "Rc8+ cannot be answered by Kd4 because Ke5 attacks d4, as stated. No new factual error established.",
        "Rd8+ is not immediately capturable; doubts about mate in two are not labeled a false claim.",
        "Rc8+ does not mate; the reply acknowledges the draw. Clock 100 ends play before a Black reply.",
    ],
    (8, 0): [
        "Rh3+ begins a checking/confinement plan. The generic plan is not sufficiently specified to certify or refute from prose alone.",
        "Kd4 keeps the third rank covered by Rh3 and leaves a5/b4/b5 as stated.",
        "Ra3 is claimed to leave only Kb5. Kxa3 is legal and actually occurs, losing the rook and drawing. Both M2 arms had zero wins, so a harmful intervention effect is not statistically resolved.",
    ],
    (8, 1): [
        "Rh3+ leaves a2/b2/a4/b4 as stated; no factual error established.",
        "Kd4 keeps the third rank covered as stated; no factual error established.",
        "Kd5 leaves a4/a5/b5 as stated; no factual error established.",
        "Rh4 leaves a5/a6/b6 as stated; no factual error established.",
        "Rb4+ has the stated local replies but loses the clock-aware theoretical win: 85+15 becomes 87+15. Its harmful effect is statistically unresolved.",
        "Rh4 revisits the board after step 4 with four fewer half-moves. Avoiding Rb7+ because of Kxb7 is correct; the future Rh7+ plan is unverified.",
        "Rh7 leaves a5/a6/b5 as stated; no new factual error established.",
        "Ra7 leaves b4/b6 as stated. The broad c-file language is evaluated locally: c4/c5/c6 are covered by Kd5; no exhaustive whole-file claim is imposed.",
        "Kd4 leaves b3/b5 as stated. Whether this is the best remaining plan is unverified; the position is already clock-lost.",
        "Kc3 leaves b6/c5/c6 as stated. The phrase keeps the net tight is evaluative and not independently demonstrated.",
        "Rd7 moves the rook away from the real Kxa7 threat. The reply acknowledges the short clock and lack of mate in two.",
        "Kd4 does not mate, as acknowledged. The claim that it keeps the rook safe is false geometrically: Black could play Kxd7. Clock 100 ends the actual game first, so no rook capture occurs. The c5 parenthetical may describe pre-move alternatives; that interpretation is uncertain and is not counted as a second factual error.",
    ],
}

# Machine-checkable claims extracted from the text, not an LLM classification.
# Terminal checks describe hypothetical geometry, never an actual defender turn.
CLAIMS = {
    (3, 0, 7): {"illegal_destinations_claimed_legal": ["g2"]},
    (3, 1, 2): {"exact_destinations_claimed": ["b1", "d1"]},
    (4, 0, 3): {"exact_destinations_claimed": ["g1"]},
    (4, 0, 4): {"exact_destinations_claimed": ["f1", "g1", "h1", "h2"]},
    (4, 1, 1): {"exact_destinations_claimed": ["g1"], "rook_claimed_safe": True},
    (6, 0, 3): {"all_replies_on_rank_claimed": 8},
    (8, 0, 3): {"exact_destinations_claimed": ["b5"]},
    (8, 1, 12): {"rook_claimed_safe": True},
}

# Ambiguous evaluative/future-plan statements are retained separately, not counted
# as established errors or causal mechanisms.
UNCERTAIN = {(3,0,5), (4,0,5), (4,0,7), (8,0,1), (8,1,6), (8,1,9), (8,1,10), (8,1,12)}
