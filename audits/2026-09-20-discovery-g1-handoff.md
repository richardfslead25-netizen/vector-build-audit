# Discovery → G1 catalyst-intake handoff

Start HEAD: `98533d0e754255b718dc5827521bf0cd63e64b11`
Accepted discovery runtime: `d75cf264d16530d23a6a4f8bc6e815cb6f92f72c`

## Problem solved

Offline nomination object from independently promoted discovery records into existing G1. Promotion is permission to investigate, not to score or verify a catalyst.

## Changed files

- `vector/discovery/handoff.py`
- `vector/discovery/__init__.py`
- `tests/test_discovery_g1_handoff.py`
- `audits/2026-09-20-discovery-g1-handoff.md`

## Unchanged

scoring engine, config, Sage adapter, OCC identity, pipeline, ingestion, authority.

```
DISCOVERY_PROMOTION_EQUALS_CATALYST_VERIFIED = FALSE
HANDOFF_SCORE_POINTS = 0
CONTRACT_FIELDS_FABRICATED = NO
GEX_FIELDS_FABRICATED = NO
DISCOVERY_TO_G1_HANDOFF = IMPLEMENTED_PENDING_REVIEW
PR_1 = HOLD
REVIEW != APPROVAL != TRADE
```
