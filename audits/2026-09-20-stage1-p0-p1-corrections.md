# Stage 1 P0/P1 contract corrections — 2026-09-20

Parent HEAD audited: `0fc175208933d92a98dfe15fb4f363b8b9472d7b`
Decision received: `STAGE_1 = CORRECTIONS_REQUIRED`. PR #1 remains HOLD.

## Changes (bounded)

P0 Sage-confirmation conjunction now requires `sage.verified_established is True` in addition to `SAGE_INFORMED` + `ESTABLISHED` + `CONSISTENT`. A deliberately constructed `SageContext` that looks admissible except `verified_established=False` scores zero confirmation points.

P1 Nearby strike/expiration alternatives must prove quote freshness at the evaluation cutoff. Missing, naive, future, or stale (`chain_max_age`) alternative quote timestamps do not earn comparison credit and cannot clear `MISSING_NEARBY_*` vetoes. Same-underlying/right and “not newer than selected” remain insufficient alone.

## Unchanged

Sage adapter admission lock, synthetic ingestion boundary, Stage 1 no-PROMOTE red team, fixed DTE bands, 14–45 EOW, execution disabled, no Webull, no Sage writes.

```
SAGE_INPUT=UNAVAILABLE
SAGE_INFORMED=disabled
SAGE_POINTS=0
LIVE_EXECUTION_AUTHORIZED=FALSE
PR_1_MERGE=HOLD
LIVE_DATA_INGESTION=NO_GO
A/A_PLUS_LIVE_PROMOTION=NO_GO
REVIEW != APPROVAL != TRADE
```

Exact-head CI must be attached by the runner; this note does not claim a green workflow.
