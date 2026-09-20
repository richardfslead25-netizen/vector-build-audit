# Issue #5 offline CandidateDiscoveryRecord runtime

Start HEAD: `6738ee3078092b406cb412ca94ee458e99375681`
Accepted spec: `ae21cf3d5afbf93fab1955ed8de0aed780199ed5`

## Problem solved

Typed offline discovery record plus fail-closed promotion rules. Commentary nominates; promotion requires publication AND mechanism AND transmission flags independently.

## Changed files

- `vector/discovery/__init__.py`
- `vector/discovery/models.py`
- `vector/discovery/validate.py`
- `tests/test_candidate_discovery.py`
- `audits/2026-09-20-issue5-discovery-runtime.md`

## Unchanged

scoring engine, config, Sage adapter, OCC identity, pipeline, authority, ingestion, Webull.

## Tests

`PYTHONPATH=. VECTOR_OFFLINE=1 pytest -q tests/test_candidate_discovery.py`

## Limitations

No source fetcher. No durable store. No board wiring. Promotion here means eligibility to enter existing G1 catalyst intake later — not a score, not PROMOTE red-team, not execution.

```
CANDIDATE_DISCOVERY_RUNTIME = IMPLEMENTED_PENDING_REVIEW
EXTERNAL_NETWORK_ACCESS = NONE
SAGE_INPUT = UNAVAILABLE
SAGE_INFORMED = disabled
PR_1 = HOLD
REVIEW != APPROVAL != TRADE
```
