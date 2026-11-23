# M3 live pilot: Haiku 4.5 continuing Haiku 5.5 checkpoints

Technical and cost feasibility. Recovery rates are descriptive, non-confirmatory, and excluded from later confirmation labels.

## Feasibility

| Check | Result |
| :--- | :--- |
| Jobs completed | 160 / 160 |
| Paid calls settled for completed jobs | 256 |
| Dispatch success (settled / all requests that reached inference, incl. the pre-fix aborts) | 99.2% |
| Response model was `claude-haiku-4-5-20251001` on every call | yes |
| Prefix, board and counters preserved on every fork | yes |
| Keep arm forced the original reply exactly once | yes |
| Re-decide arm forced no reply | yes |
| Cost of completed jobs | $2.2465 ($0.0140 per continuation) |
| Same-usage proxy for 160 | $7.23 |
| Tokens per continuation, actual / proxy | input 0.209, output 0.278 |
| Ledger: settled | 256 requests, $2.2465 |
| Ledger: maximum retained (uncertain) | 2 requests, $0.66 |
| Ledger: rejected before inference | 6 requests, $0 |
| Ledger total against the $15 cap | $2.9065 |

## Recovery rates (descriptive)

Gain = P(win | re-decide) - P(win | keep original reply), in percentage points. Haiku 4.5 has 10 continuations per arm (Newcombe 95% interval, unadjusted). The Haiku 5.5 columns are the frozen M2 estimates at 30 per arm.

| Decision | Role | H4.5 keep | H4.5 re-decide | H4.5 gain (pp) | 95% interval (pp) | H5.5 M2 gain (pp) | H5.5 Holm p |
| :--- | :--- | ---: | ---: | ---: | :--- | ---: | ---: |
| `krk-m4-1_trial0_step003` | resolved_harmful | 0/10 | 0/10 | +0 | [-28, +28] | +67 | 1.71e-05 |
| `krk-m4-1_trial0_step005` | resolved_harmful | 0/10 | 1/10 | +10 | [-19, +40] | +37 | 0.015 |
| `krk-m4-1_trial1_step001` | resolved_harmful | 0/10 | 0/10 | +0 | [-28, +28] | +37 | 0.015 |
| `krk-m4-1_trial0_step001` | control_or_unresolved | 0/10 | 0/10 | +0 | [-28, +28] | -33 | 0.84 |
| `krk-m6-1_trial0_step001` | control_or_unresolved | 0/10 | 0/10 | +0 | [-28, +28] | -20 | 1 |
| `krk-m3-1_trial0_step001` | control_or_unresolved | 0/10 | 0/10 | +0 | [-28, +28] | +3 | 1 |
| `krk-m3-1_trial0_step003` | control_or_unresolved | 0/10 | 0/10 | +0 | [-28, +28] | +0 | 1 |
| `krk-m8-1_trial0_step003` | control_or_unresolved | 0/10 | 0/10 | +0 | [-28, +28] | +0 | 1 |

Overall wins: keep 0/80, re-decide 1/80. Game endings: checkmate 1, fifty_move_rule 2, insufficient_material 156, stalemate 1.
