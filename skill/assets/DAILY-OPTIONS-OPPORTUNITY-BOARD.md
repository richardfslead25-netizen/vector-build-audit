# Daily Options Opportunity Board

**Strategy:** `VECTOR-AGGRESSIVE-OPTIONS-001`  
**Date:**  
**Cycle:** PREMARKET / OPEN_CONFIRMATION / MIDDAY / CLOSE / DEEP_DIVE  
**Information cutoff:**  
**Prepared by:** VECTOR Aggressive Options Trader (single agent)  
**Paper authority:**  
**Live authority:** OWNER ONLY

## Data-quality header

| Input | Source | As-of | Status |
|---|---|---|---|
| SIGIL |  |  | AVAILABLE / UNAVAILABLE |
| SAGE |  |  | AVAILABLE / UNAVAILABLE |
| Underlying tape |  |  |  |
| Option chains |  |  |  |
| GEX |  |  | PRINTABLE / GEX_NOT_PRINTABLE |
| Catalysts |  |  |  |
| Volume profile / order flow |  |  | AVAILABLE / OF_ABSENT |

## Market gamma map

| Symbol | Spot | GEX regime | Gamma flip | Call wall | Put wall | Expiry filter | Source/as-of | Interpretation |
|---|---:|---|---:|---:|---:|---|---|---|
| SPX/SPY |  |  |  |  |  |  |  |  |
| QQQ |  |  |  |  |  |  |  |  |
| IWM |  |  |  |  |  |  |  |  |

Do not fill unavailable values. Use `GEX_NOT_PRINTABLE`.

## Top calls

| Rank | Ticker | Score | State | Setup | Trigger | Target | Invalidation | Expiry | Strike | DTE | Delta | Spread % | OI/Vol | IV/EM | Catalyst | GEX source/as-of |
|---:|---|---:|---|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|
| 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

## Top puts

| Rank | Ticker | Score | State | Setup | Trigger | Target | Invalidation | Expiry | Strike | DTE | Delta | Spread % | OI/Vol | IV/EM | Catalyst | GEX source/as-of |
|---:|---|---:|---|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|
| 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

If fewer than five qualify, write `NO QUALIFIED CANDIDATE` in the unused rows.

## Candidate score decomposition

| Candidate | Gamma/location | Momentum/technical | Catalyst | Flow/VP/breadth | Macro transmission | Contract/liquidity/vol | Risk/invalidation | Total | Hard veto |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
|  |  |  |  |  |  |  |  |  |  |

Use the weight set corresponding to the candidate’s DTE. Cite evidence for every nonzero component.

## Complete packet — Candidate 1

| Field | Value |
|---|---|
| Ticker/direction |  |
| Underlying/as-of |  |
| Score/state |  |
| Setup archetype |  |
| Gamma regime |  |
| Flip/call wall/put wall |  |
| Expiry filter and GEX source/as-of |  |
| VAH/VAL/POC |  |
| 50 EMA |  |
| MACD 8-17-9 |  |
| MACD 12-26-9 |  |
| ADX/+DI/−DI |  |
| RSI(34) |  |
| Fibonacci swing/level |  |
| Momentum level/acceleration |  |
| Relative strength/volume |  |
| Catalyst/date |  |
| Contract |  |
| Bid/ask/mid/spread % |  |
| OI/option volume |  |
| Delta/gamma/theta/vega |  |
| IV/RV/expected move |  |
| Expected holding period |  |
| Nearby contracts rejected |  |
| Factor cluster |  |
| Red-team verdict |  |

```text
IF
THEN
BECAUSE
INVALIDATED IF
ALTERNATE PATH
EXPECTED HORIZON
WHY THIS CONTRACT
```

## Complete packets — Candidates 2 and 3

Repeat the Candidate 1 packet without removing unavailable fields.

## Rejected high-interest names

| Ticker | Proposed direction | Raw score | Exact veto | Evidence needed to reconsider |
|---|---|---:|---|---|
|  |  |  |  |  |

## Alternate paths

### Bullish path

```text
IF
THEN
WATCH
INVALIDATED IF
```

### Bearish path

```text
IF
THEN
WATCH
INVALIDATED IF
```

## Factor-cluster exposure

| Cluster | Candidates/positions | Combined premium risk | Limit | Status |
|---|---|---:|---:|---|
| Rates/QT |  |  |  |  |
| AI/semiconductors |  |  |  |  |
| Energy/scarcity |  |  |  |  |
| Small-cap/credit |  |  |  |  |
| Volatility/gamma |  |  |  |  |

## Paper execution menu

| Candidate | Eligible? | Limit-entry plan | Paper risk % | Quantity | Pretrade path |
|---|---|---|---:|---:|---|
|  |  |  |  |  |  |

A score alone never authorizes execution. Every hard gate and current authority must pass. Live remains Owner-only.

## Midday change log

| Time | Candidate | Old state/score | New state/score | Evidence changed | Decision |
|---|---|---|---|---|---|
|  |  |  |  |  | UNCHANGED / PROMOTED / REDUCED / INVALIDATED / OPPOSITE_PATH |

Do not overwrite the original board.

## Close review

| Candidate | Triggered? | Underlying result | Option/paper result | MFE/MAE | IV/theta effect | Gamma behavior | Thesis fidelity | Lesson |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |

## Required declaration

```text
LIVE_EXECUTION_AUTHORIZED = FALSE
OWNER_FINAL_AUTHORITY = TRUE
MISSING_DATA_WAS_NOT_INVENTED = TRUE
GEX_VENDOR_AND_AS_OF_STAMPED = TRUE
ORIGINAL_THESIS_PRESERVED = TRUE
PAPER_EXECUTION = FALSE
```
