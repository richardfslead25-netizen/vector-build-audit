# Sage adapter integration review

Date: 2026-09-20
Head at review: `f56df270eeab32aefff6a007a4216cd343cef275`
Functional accepted runtime: G1 handoff `5a463bd`

This is a review note. No adapter, scoring, or admission change.

## Surfaces read

- `vector/sage/adapter.py`
- `vector/contracts/sage.py`
- `vector/scoring/engine.py` `_score_macro`
- `vector/pipeline.py` `evaluate_candidate` ingest call
- `vector/discovery/validate.py` `official_freeze_admitted`
- `vector/discovery/handoff.py`
- `tests/test_sage_adapter.py`

## Production path

`evaluate_candidate` always runs `SageReadOnlyAdapter.ingest(sage_payload)`.

Current adapter outcomes that can reach scoring:

- `None` → `UNAVAILABLE`, freeze count not invented
- SIGIL / `legacy_sigil` → isolated `UNAVAILABLE`, no SAGE confirmation
- explicit `NOT_ESTABLISHED` → `NOT_ESTABLISHED`, supplied freeze count preserved only
- complete ESTABLISHED-shaped claim → `NOT_ESTABLISHED`, `claimed_established=True`, `verified_established=False`, `BEHAVIOR_ONLY`, `INSUFFICIENT`
- stale complete claim → `STALE`, still `BEHAVIOR_ONLY`
- malformed claim → `INVALID`

The adapter never returns `ESTABLISHED` + `SAGE_INFORMED` + `verified_established=True` while admission is closed. A complete-looking payload is not a verified official freeze.

Write methods raise `SageWriteError`. `WRITE_FORBIDDEN = True`.

## Consumer conjunctions

Scoring Sage-confirmation (`_score_macro`):

`verified_established` AND `SAGE_INFORMED` AND `ESTABLISHED` AND `CONSISTENT`

Discovery / G1 freeze comparison (`official_freeze_admitted`):

`verified_established` AND `ESTABLISHED` AND `SAGE_INFORMED` AND `freeze_identity`

Discovery is stricter (requires freeze identity). Scoring still cannot award Sage-confirmation points from adapter output today because the adapter cannot satisfy `verified_established`.

G1 handoff may carry an admitted freeze reference as provenance only. `sage_informed_enabled` remains False. Discovery promotion does not set `catalyst_verified`.

## Unused ingest kwargs

`ingest(..., observed_direction=, transmission_observed=)` are accepted by `pipeline.py` and ignored by the adapter. Tape does not become fusion `CONSISTENT` inside the adapter. Leave unused; do not wire tape into Sage alignment.

## Admission flag

`SAGE_INFORMED_ADMISSION_ENABLED` remains False in config. The adapter does not have a live branch that honors flipping that flag. Admission stays closed even if Settings are edited, because complete claims still resolve to unverified `NOT_ESTABLISHED`.

## Verdict

```
SAGE_ADAPTER_INTEGRATION = REVIEWED_LOCKED
SAGE_INPUT = UNAVAILABLE
SAGE_INFORMED = disabled
SAGE_POINTS = 0
VECTOR_WRITES_TO_SAGE = false
OFFICIAL_FREEZE_COUNT = 0
ADAPTER_CAN_MINT_ESTABLISHED = NO
CONSULT_IS_NOT_FREEZE = YES
PR_1 = HOLD
WEBULL = HOLD
REVIEW != APPROVAL != TRADE
```

No implementation slice opened.
