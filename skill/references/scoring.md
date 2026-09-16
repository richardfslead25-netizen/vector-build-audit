# Scoring, Contract Rules, and Packet Fields

## DTE-band scoring

Score every eligible candidate from 0–100. Use one fixed weight set for the candidate’s DTE band. Do not interpolate between bands.

- 14–21 DTE uses the 14–21 column only
- 22–35 DTE uses the 22–35 column only
- 36–45 DTE uses the 36–45 column only
- DTE outside 14–45 is a hard veto, not a scored band

| Factor | 14–21 DTE | 22–35 DTE | 36–45 DTE |
|---|---:|---:|---:|
| Gamma regime and location | 22 | 18 | 14 |
| Momentum and technical structure | 20 | 17 | 13 |
| Catalyst proximity and timing | 18 | 15 | 13 |
| Order flow, volume profile, and breadth | 12 | 12 | 10 |
| Macro / regime transmission | 8 | 16 | 25 |
| Contract, liquidity, and volatility economics | 15 | 17 | 20 |
| Risk/reward and invalidation quality | 5 | 5 | 5 |
| Total | 100 | 100 | 100 |

Each factor score must cite its observed inputs. Missing data receives zero for that subfactor. Never fill with a neutral estimate. Never award points for missing data.

A hard veto overrides the numeric score.

## Classifications

| Score | State | Treatment |
|---:|---|---|
| 90–100 | A_PLUS | High-conviction paper candidate if every gate passes |
| 82–89 | A | Paper candidate; Owner-review quality |
| 72–81 | B_DEVELOPING | Watch for trigger; no premature entry |
| 62–71 | WATCH | Track only |
| below 62 | REJECT | Do not present as a potential trade |

Premarket rows may be labeled `WATCH` or `B_DEVELOPING` even before a live chain. They are not trade-ready. Stage 1 still cannot promote live-data A / A_PLUS.

## Factor scoring guidance

### Gamma regime and location

Award gamma points only for sourced, timestamped vendor GEX with vendor, methodology, symbol, expiry coverage, as-of, units, sign convention, and spot reference. Stage 1 `GAMMA_UNAVAILABLE` receives zero gamma points. A technical structure substitute may locate price; it does not earn the gamma bucket. Full gamma points require regime, flip, both walls, expiry filter, and a coherent location relative to spot. Penalize near-flip with insufficient room, mixed vendor boards, or stale EOD used as live.

### Momentum and technical structure

Award for aligned 50 EMA, both MACD frames, ADX/DI, volume, relative strength, and an objective trigger. Separate momentum level from acceleration. Penalize conflicting frames or pattern-forcing.

### Catalyst timing

Award when a validated catalyst or market-structure trigger sits inside both DTE and intended holding period and is not already fully priced into IV. Unverified rumors score zero as catalyst.

### Order flow, volume profile, and breadth

Award for VAH/VAL/POC context, sweep-versus-run classification, breadth, and order-flow confirmation. `OF_ABSENT` is allowed but caps this bucket unless price/volume confirmation is strong.

### Macro transmission

Award only when expected effects are visible in rates, dollar, commodities, credit, breadth, sector, or the security itself. SIGIL/SAGE context without transmission evidence scores near zero.

Sage-confirmation points require `verified_established = True`, `OPERATING_MODE = SAGE_INFORMED`, and fusion `CONSISTENT`. A self-declared or structurally complete claim is `claimed_established` only and scores zero confirmation. `NOT_ESTABLISHED`, `UNAVAILABLE`, `INVALID`, `STALE`, or SIGIL-only payloads score zero Sage-confirmation points. Fusion `INSUFFICIENT` caps the macro bucket. Fusion `INCONSISTENT` penalizes the bucket even if the tape setup is otherwise valid. Observed transmission remains a separate subfactor.

### Contract, liquidity, and volatility economics

Award for live chain completeness, spread quality, OI/volume, delta fit, IV versus expected move, and nearby-contract comparison. Wide spreads, dark Greeks, lottery delta, or IV-crush traps score near zero and may veto.

### Risk/reward and invalidation

Award only for a specific, mutually exclusive invalidation, a defined target path, and realistic room versus premium. Vague invalidation scores near zero and can veto.

## Contract comparison rule

Before locking a strike, compare at least one nearby strike and one nearby eligible expiration on the same underlying and option right. Reject the candidate if the selected contract wins only because it is cheap.

Record why this contract beat the alternatives under `WHY THIS CONTRACT`.

## Directionally correct still losing

Do not promote a contract that can be right on direction and still lose because of premium, theta, IV crush, lottery delta, spread, priced catalyst, or DTE mismatch.

Correct direction is not a score floor.

## Required packet fields

For every serious candidate include where available:

- operating mode (`BEHAVIOR_ONLY` / `SAGE_INFORMED`)
- fusion (`CONSISTENT` / `INCONSISTENT` / `INSUFFICIENT`)
- SAGE status, claimed_established, verified_established
- rank, ticker, call or put
- score and classification
- setup type
- underlying price and as-of
- gamma regime, flip, call wall, put wall
- source, expiry filter, and as-of
- technical trigger
- catalyst and catalyst date
- target path
- invalidation
- expiration, strike, DTE
- delta, gamma, theta, vega
- bid, ask, midpoint, spread percentage
- OI and option volume
- IV, RV, expected move
- expected holding period
- factor cluster
- nearby contracts rejected
- red-team conclusion

If a field cannot be printed, keep the field and write `UNAVAILABLE`.

## Suggested paper-risk bands

Only if paper authority is active. Never live sizing. Stage 1 paper remains off.

A score alone never authorizes execution.
