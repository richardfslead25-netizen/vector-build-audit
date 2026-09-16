# GPT audit mailbox — VECTOR Stage 1

**Date:** 2026-09-15 PT / 2026-09-16 UTC
**Repo:** https://github.com/richardfslead25-netizen/vector-build-audit
**Branch:** `build/stage-1-contracts`
**PR:** https://github.com/richardfslead25-netizen/vector-build-audit/pull/1
**Base:** `main` @ `4e48067bea5a6415dc3325e698625ad9dfd23e64`
**Do not:** invent SAGE, edit SAGE, authorize paper or live orders, merge, or start Webull.

```text
RESEARCH_ENABLED = true
PAPER_EXECUTION_ENABLED = false
LIVE_EXECUTION_ENABLED = false
VECTOR_WRITES_TO_SAGE = false
SAGE_INFORMED_ADMISSION_ENABLED = false
HOLD_FOR_CHATGPT_AUDIT = true
```

## HOLD — saved for ChatGPT audit

Audit snapshot (OCC parser landing, green CI):

- **Review SHA:** `2c5a06050e09f05aba774004568513d8ee2d1a41`
- **Commit:** https://github.com/richardfslead25-netizen/vector-build-audit/commit/2c5a06050e09f05aba774004568513d8ee2d1a41
- **Exact-head CI:** https://github.com/richardfslead25-netizen/vector-build-audit/actions/runs/35049068343 (success)
- **PR:** https://github.com/richardfslead25-netizen/vector-build-audit/pull/1

Do not merge this PR. Do not start Stage 2 ingestion. Do not enable paper or live execution. Leave SAGE unchanged.

This mailbox commit may sit on top of `2c5a060`. ChatGPT should review `2c5a060` as the implementation head.

## ChatGPT review — 2026-09-16

Decision on reviewed head `e5ef1be`: STAGE_1_CORRECTIONS_REQUIRED. NO_GO for live ingestion or A/A_PLUS promotion. Appended at `a889acb`.

Partial correction commits `93e1efc` / `b1fc84d` / `0aa395c` landed engine pieces but left CI red: `test_scenario_units_and_multiplier` still expected midpoint-only P&L of `0.0` after executable half-spread + commission were added. `tests/test_audit_corrections.py` was not on the remote tree at `0aa395c`.

## Correction pass — mapping

| Finding | Fix | Tests |
|---|---|---|
| P0 SAGE loose ESTABLISHED / substring polarity / future cutoff / unknown source / malformed posterior | Production `SAGE_INFORMED` admission disabled. Required schema/source/cutoff/receipt/freeze/regime/posterior. No regime-name CALL/PUT inference. Future and naive timestamps rejected. SIGIL isolated. | `tests/test_sage_adapter.py`, `tests/test_audit_corrections.py` |
| P0 eligibility timestamps, DTE, OCC, listings, coherence | Required quote/Greeks times; naive/future rejected; DTE derived vs claimed; OCC parse of root/right/strike/expiry; listings required; ticker/market/gamma/right coherence. Gates do not mutate caller quote_quality. | `tests/test_eligibility.py`, `tests/test_audit_corrections.py`, `tests/test_occ_identity.py` |
| P1 wrong-way walls / unsigned RS / asserted presence / text-only target / one comparison | Directional runway and RS. Transmission needs notes. Target/invalidation require numeric geometry. Nearby strike AND nearby expiration. | `tests/test_scoring.py`, `tests/test_audit_corrections.py` |
| P1 scenarios mid-only, missing Greeks as zero, score-only PROMOTE | Missing Greeks → unavailable scenarios. P&L uses quoted half-spread + commission both sides. Promotion blocked without geometry/comparisons/supportive net P&L. Critique labeled stub. | `tests/test_pipeline_and_authority.py`, `tests/test_audit_corrections.py` |
| Hygiene interpolation / unpinned CI | `scoring.md` forbids interpolation. CI installs `.[dev]` from `pyproject.toml`. | workflow `ci.yml` |

Rules version: `VECTOR-STAGE1-0.1.1`.

Local offline: `PYTHONPATH=. pytest -q` (VECTOR_OFFLINE=1).
Demo remains synthetic. No Webull. No merge. No orders.

## OCC identity follow-up

`vector/eligibility/identity.py` now parses compact OSI and padded 21-character OSI. Digit roots (`SPXW`) and mill strikes are accepted. Invalid dates, zero strikes, and old OPRA codes stay `CONTRACT_IDENTITY_UNPARSEABLE`. Substring membership is still not identity. Tests: `tests/test_occ_identity.py`.

## Next step

ChatGPT re-review of `2c5a060`. Hold the branch until that audit returns. Do not start Stage 2 ingestion until ChatGPT clears P0.
