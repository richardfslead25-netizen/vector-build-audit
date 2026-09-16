# Scoring, Contract Rules, and Packet Fields

## DTE-adjusted scoring

Score every eligible candidate from 0–100. Interpolate linearly between the anchor weight sets when DTE falls between anchors.

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

Premarket rows may be labeled `WATCH` or `B_DEVELOPING` even before a live chain. They are not trade-ready.

## Factor scoring guidance

### Gamma regime and location

Award only for sourced, timestamped GEX or a clearly labeled structure substitute. Full points require regime, flip, both walls, expiry filter, and a coherent location relative to spot. Penalize near-flip with insufficient room, mixed vendor boards, or stale EOD used as live.

### Momentum and technical structure

Award for aligned 50 EMA, both MACD frames, ADX/DI, volume, relative strength, and an objective trigger. Separate momentum level from acceleration. Penalize conflicting frames or pattern-forcing.

### Catalyst timing

Award when a validated catalyst or market-structure trigger sits inside both DTE and intended holding period and is not already fully priced into IV. Unverified rumors score zero as catalyst.

### Order flow, volume profile, and breadth

Award for VAH/VAL/POC context, sweep-versus-run classification, breadth, and order-flow confirmation. `OF_ABSENT` is allowed but caps this bucket unless price/volume confirmation is strong.

### Macro transmission

Award only when expected effects are visible in rates, dollar, commodities, credit, breadth, sector, or the security itself. SIGIL/SAGE context without transmission evidence scores near zero.

If SAGE is `NOT_ESTABLISHED` or SIGIL is unavailable, award zero Sage-confirmation points. Fusion `INSUFFICIENT` caps this bucket. Fusion `INCONSISTENT` penalizes this bucket even if the tape setup is otherwise valid.

### Contract, liquidity, and volatility economics

Award for live chain completeness, spread quality, OI/volume, delta fit, IV versus expected move, and nearby-contract comparison. Wide spreads, dark Greeks, lottery delta, or IV-crush traps score near zero and may veto.

### Risk/reward and invalidation

Award only for a specific, mutually exclusive invalidation, a defined target path, and realistic room versus premium. Vague invalidation scores near zero and can veto.

## Contract comparison rule

Before locking a strike, compare at least one nearby strike and one nearby eligible expiration. Reject the candidate if the selected contract wins only because it is cheap.

Record why this contract beat the alternatives under `WHY THIS CONTRACT`.

## Directionally correct still losing

Do not promote a contract that can be right on direction and still lose because:

- the move is too small versus premium and slippage
- the move is too slow versus theta
- IV crush after the catalyst
- the strike is a lottery
- the spread consumes the edge
- the catalyst is already priced
- DTE and holding period are mismatched

Correct direction is not a score floor.

## Required packet fields

For every serious candidate include where available:

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

Only if paper authority is active. Never live sizing.

- A_PLUS — premium at risk 0.75%–1.25% of paper NAV
- A — 0.50%–0.75%
- below A — no new paper option position
- maximum aggregate premium at risk — 5% of paper NAV
- maximum one-factor cluster — 2% unless explicitly documented

A score alone never authorizes execution.
