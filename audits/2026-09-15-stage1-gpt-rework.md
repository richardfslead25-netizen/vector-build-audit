# VECTOR Stage 1 rework after GPT NO-GO

Date: 2026-09-15 / 2026-09-16 UTC
Owner: Richard
Implementer: Grok
Branch: `build/stage-1-contracts`
PR: #1 HOLD — do not merge

## Prior verdict

NO-GO for live-market-data ingestion or live-data A / A_PLUS promotion.
Blocking issue: SAGE admission bypass (`Settings.sage_informed_admission_enabled` and unverified claims published as ESTABLISHED).

## What landed

### Item 1 — SAGE admission bypass
- `vector/config.py`: `sage_informed_admission_enabled` validator always returns False.
- `vector/sage/adapter.py`: complete established claims stay `NOT_ESTABLISHED` + `claimed_established=True` + `verified_established=False` + `BEHAVIOR_ONLY`.
- `vector/contracts/sage.py`: `as_public_dict()` publishes regime/posterior only if verified_established AND ESTABLISHED AND SAGE_INFORMED.

### Item 2 — upstream validation
- Receipt must be ≥ cutoff. Naive and future stamps rejected.
- Posterior rejects bool, string, scalar, mass > 1, sum not equal to 1 ± 1e-6.
- Adapter does not repair SAGE.

### Item 3 — Stage 2 snapshot boundary
- `accept_snapshot()` requires `synthetic=True`, `data_status=SYNTHETIC`, entitlement `stage1-synthetic-only`, and `VECTOR_STAGE=1`.
- `VECTOR_OFFLINE=0` does not open a live hole.
- fetch_quote / fetch_chain / submit_order still raise `LiveIngestionBlocked`.

### Item 4 — promotion checks
- Nearby alternatives must match underlying and right and sit inside a proximity band.
- Stage 1 red team cannot return PROMOTE. Max useful verdict is REDUCE. Vetoes stay KILL / NO_TRADE.

### Item 5 — docs
- `skill/references/scoring.md`: no interpolation; structure substitute earns zero gamma; Sage-confirmation needs verified freeze.
- Board template and SKILL.md header/packet fields: operating mode, fusion, claimed vs verified SAGE.

### Tests
Local: 67 passed, 0 failed (`VECTOR_OFFLINE=1 VECTOR_STAGE=1`).
Three previously failing tests now assert the new lock.

## Still frozen

```
RESEARCH_ENABLED = true
PAPER_EXECUTION_ENABLED = false
LIVE_EXECUTION_ENABLED = false
SAGE_INFORMED_ADMISSION_ENABLED = false
VECTOR_WRITES_TO_SAGE = false
```

SAGE inference, taxonomy, posterior, persistence, successors, official freeze minting remain unimplemented. Missing pillars ≠ neutral.

## Not authorized by this rework

Merge of PR #1.
Webull or any live chain.
Paper or live orders.
A / A_PLUS live-data packets.
Sage writes.
