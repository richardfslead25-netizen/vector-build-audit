# Single-Agent Red Team

Before finalizing the board, temporarily argue against your own leading conclusion. Do not protect consensus. Do not soften a kill to keep five rows filled.

## Required tests

For every A or A_PLUS candidate, and for the leading DEEP_DIVE contract, test:

1. Stale or missing source timestamps
2. Fabricated or vendor-mixed GEX
3. Wall migration through spot
4. Wrong expiry filter
5. Breakout confused with a sweep
6. Positive-gamma fade attempted during negative-gamma expansion
7. Insufficient space to the target
8. Catalyst already priced into IV
9. Correct direction but losing option economics
10. DTE versus holding-period mismatch
11. Thin liquidity / wide spread / dark Greeks
12. Misleading call/put-volume interpretation
13. Macro and tape disagreement
14. Correlated positions expressing the same factor
15. Vague or non-exclusive invalidation
16. Unverified rumor as the sole catalyst
17. Horizon mismatch (0DTE scalp forced onto 14–45 DTE)
18. GEX used to rewrite SIGIL/SAGE
19. Lucky-path risk (P&L could print green for the wrong reason)

## Verdicts

Return exactly one internal verdict per leading candidate:

- `PROMOTE` — gates pass, economics work, opposite path is weaker, data is fresh
- `REDUCE` — thesis survives but size, delta, DTE, or conviction must come down
- `KILL` — hard veto or fatal hole
- `OPPOSITE_PATH` — the other direction is the cleaner expression

A `KILL` must state the exact evidence that would reverse it.

## Challenge holes that default to KILL or NO_TRADE

- +gamma fade in a confirmed −gamma expansion tape
- GEX used as SIGIL confirmation
- Walls cited with no source/as-of and no structure substitute
- Greeks or chain dark
- Dual-path erased solely because one regime label is comfortable
- Book conflict unstamped (example — energy puts against oil/XLE relative strength)
- Forced confluence to “have a play”
- High short-interest theater with no transmission path

## Output block

```text
RED_TEAM
CANDIDATE =
ATTACK =
SURVIVES =
FAILS =
VERDICT = PROMOTE | REDUCE | KILL | OPPOSITE_PATH
REVERSE_KILL_IF =
```

Do not rewrite the original thesis after the challenge. Append the verdict.
