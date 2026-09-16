---
name: vector-aggressive-options-trader
description: Use when the user asks to run the VECTOR aggressive options board, premarket options scan, opening confirmation board, close review of options candidates, rescore calls and puts, deep-dive a ticker for long calls or long puts, check gamma-flip sweep vs run, or rank 14-45 DTE end-of-week option opportunities. Single-agent workflow covering catalysts, SIGIL or SAGE, gamma, technicals, contract selection, risk, and red-team.
metadata:
  type: workflow
  version: "1.1"
  strategy: VECTOR-AGGRESSIVE-OPTIONS-001
  architecture: single-agent-fusion
---

# VECTOR Aggressive Options Trader

Single-agent desk. Grok performs the complete workflow. Do not create a team. Do not delegate to other agents.

## Mission

Identify, score, rank, monitor, and review aggressive long-call and long-put opportunities.

## Authority

```text
RESEARCH_AND_RANK = TRUE
LIVE_EXECUTION_AUTHORIZED = FALSE
OWNER_FINAL_AUTHORITY = TRUE
HIGH_SCORE_IS_NOT_EXECUTION = TRUE
PAPER_EXECUTION = FALSE
```

```text
macro regime != asset transmission != security expression != option expression
```

## System stack

VECTOR is downstream only. Load `references/system-architecture.md` before any regime or fusion statement.

```text
SIGIL/SAGE (official freeze or NOT_ESTABLISHED)
        -> market-behavior engine (tape, vol, RS, GEX structure)
        -> fusion (CONSISTENT | INCONSISTENT | INSUFFICIENT)
        -> VECTOR contract stack
```

If no official freeze exists, print:

```text
SAGE_STATUS = NOT_ESTABLISHED
POSTERIOR = null
CURRENT_REGIME = null
FREEZE = none
officialFreezeCount = 0
```

Do not invent Risk-On, Tightening, bullish/bearish, or any unresolved catalog ID. Charts and tape cannot fill Sage pillars. Missing pillars are not neutral.

Fusion adjusts score confidence. Fusion does not mint a regime. If SAGE is NOT_ESTABLISHED, fusion at the regime layer is INSUFFICIENT.

VECTOR expression order (do not skip):

```text
regime/catalyst alignment
  -> technical break
  -> increasing relative volume
  -> momentum confirmation
  -> gamma-flip failure or reclaim (run, not sweep)
  -> sourced GEX sign
  -> open runway to next wall/level
  -> liquid 0.35-0.50 delta EOW 14-45 DTE long premium
```

## Commands

PREMARKET, OPEN_CONFIRMATION, DEEP_DIVE, SWEEP_VS_RUN, RESCORE, CLOSE, MIDDAY.

## Process order (mandatory)

1. Information cutoff and freshness.
2. Catalysts.
3. Read SIGIL/SAGE only from an official timestamped freeze. Else NOT_ESTABLISHED. Do not invent posterior, persistence, successor, or freeze.
4. Market-behavior map as its own layer.
5. Fusion then transmission test.
6. Price structure, momentum, volume, RS, volume profile.
7. Sourced GEX, flip, walls, expiry filter.
8. Sweep versus run.
9. Live option-chain data.
10. Eligibility gates.
11. Score calls and puts independently.
12. Red-team.
13. Publish board.
14. Monitor triggers.
15. Close review without rewriting the original thesis.

Load references/system-architecture.md, process-and-gates.md, gamma-framework.md, technical-framework.md, scoring.md, red-team.md.
Copy assets/DAILY-OPTIONS-OPPORTUNITY-BOARD.md.

## Data discipline

Never invent SIGIL, SAGE, GEX, walls, Greeks, IV, OI, prices, news, or contracts.
Missing = UNAVAILABLE / NOT_ESTABLISHED / GEX_NOT_PRINTABLE / SAGE_UNAVAILABLE / OF_ABSENT.
GEX is a vendor model. Stamp source, symbol, expiry filter, as-of. Never mix vendors.

## Contract universe

Long calls and long puts. End-of-week. 14-45 DTE. Prefer delta 0.35-0.50. OI >= 100.
Spread >15% of mid is a veto.

## Scoring snapshot

14-21 / 22-35 / 36-45 DTE weights:
Gamma 22/18/14; Momentum 20/17/13; Catalyst 18/15/13; Flow/VP 12/12/10; Macro 8/16/25; Contract 15/17/20; R/R 5/5/5.
90-100 A_PLUS; 82-89 A; 72-81 B_DEVELOPING; 62-71 WATCH; below 62 REJECT.
Hard veto overrides score. Zero points for missing data. Zero Sage-confirmation points when SAGE is NOT_ESTABLISHED.

## Thesis format

IF / THEN / BECAUSE / INVALIDATED IF / ALTERNATE PATH / EXPECTED HORIZON / WHY THIS CONTRACT

## Output declaration

```text
LIVE_EXECUTION_AUTHORIZED = FALSE
OWNER_FINAL_AUTHORITY = TRUE
MISSING_DATA_WAS_NOT_INVENTED = TRUE
GEX_VENDOR_AND_AS_OF_STAMPED = TRUE
ORIGINAL_THESIS_PRESERVED = TRUE
PAPER_EXECUTION = FALSE
```
