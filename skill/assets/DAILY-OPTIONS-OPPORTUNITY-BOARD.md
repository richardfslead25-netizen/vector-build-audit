# Daily Options Opportunity Board

**Strategy:** `VECTOR-AGGRESSIVE-OPTIONS-001`  
**Date:**  
**Cycle:** PREMARKET / OPEN_CONFIRMATION / MIDDAY / CLOSE / DEEP_DIVE  
**Information cutoff:**  
**Prepared by:** VECTOR Aggressive Options Trader (single agent)  
**Operating mode:** BEHAVIOR_ONLY / SAGE_INFORMED  
**Fusion:** CONSISTENT / INCONSISTENT / INSUFFICIENT  
**SAGE status:** UNAVAILABLE / INVALID / STALE / NOT_ESTABLISHED / ESTABLISHED  
**SAGE claimed / verified:** claimed_established= / verified_established=  
**Paper authority:** FALSE  
**Live authority:** OWNER ONLY / FALSE

## Data-quality header

| Input | Source | As-of | Status |
|---|---|---|---|
| SIGIL |  |  | AVAILABLE / UNAVAILABLE (does not confer SAGE) |
| SAGE |  |  | UNAVAILABLE / NOT_ESTABLISHED / INVALID / STALE / ESTABLISHED |
| SAGE verified |  |  | verified_established TRUE / FALSE |
| Operating mode |  |  | BEHAVIOR_ONLY / SAGE_INFORMED |
| Fusion |  |  | CONSISTENT / INCONSISTENT / INSUFFICIENT |
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

Do not fill unavailable values. Use `GEX_NOT_PRINTABLE`. Structure substitutes are not GEX.

## Top calls / top puts

Keep five-row tables. Unused rows: `NO QUALIFIED CANDIDATE`.

## Candidate score decomposition

Use the fixed weight column for the candidate’s DTE band. Do not interpolate. Structure substitutes score zero in the gamma column. Sage-confirmation is zero unless verified_established and SAGE_INFORMED and CONSISTENT.

## Complete packet — Candidate 1

Required fields include operating mode, fusion, SAGE status / claimed / verified, plus existing contract, GEX, technical, and red-team fields. Keep unavailable fields visible as `UNAVAILABLE`.

```text
IF
THEN
BECAUSE
INVALIDATED IF
ALTERNATE PATH
EXPECTED HORIZON
WHY THIS CONTRACT
```

## Required declaration

```text
LIVE_EXECUTION_AUTHORIZED = FALSE
OWNER_FINAL_AUTHORITY = TRUE
MISSING_DATA_WAS_NOT_INVENTED = TRUE
GEX_VENDOR_AND_AS_OF_STAMPED = TRUE
ORIGINAL_THESIS_PRESERVED = TRUE
PAPER_EXECUTION = FALSE
OPERATING_MODE = BEHAVIOR_ONLY
FUSION = INSUFFICIENT
VERIFIED_ESTABLISHED = FALSE
```
