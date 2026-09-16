# GPT audit mailbox — VECTOR Stage 1

**Date:** 2026-09-15 PT / 2026-09-16 UTC
**Repo:** https://github.com/richardfslead25-netizen/vector-build-audit
**Branch:** `build/stage-1-contracts`
**PR:** https://github.com/richardfslead25-netizen/vector-build-audit/pull/1
**Base:** `main` @ `4e48067bea5a6415dc3325e698625ad9dfd23e64`
**Do not:** invent SAGE, edit SAGE, authorize paper or live orders.

## Problem solved

`main` had three missing skill references, no typed contracts, no deterministic scorer, and no tests. An earlier push left package stubs without implementation modules, so CI failed. This completion lands the remaining modules, offline tests, board template, references, journal, and ingestion boundary.

## Files

References: `skill/references/process-and-gates.md`, `gamma-framework.md`, `technical-framework.md`, `scoring.md`, `red-team.md`, `system-architecture.md`.
Board template: `skill/assets/DAILY-OPTIONS-OPPORTUNITY-BOARD.md`.
Engine: `vector/` contracts, SAGE adapter, gates, features, scoring, scenarios, red team, board, journal, offline data boundary.
Tests: `tests/` offline suite.
Docs: architecture, conflicts, source inventory, provider note, Webull entitlement questions.

## What works

Read-only SAGE statuses including no invented freeze count on `UNAVAILABLE`.
SIGIL cannot confer SAGE confirmation. Write methods raise `SageWriteError`.
`BEHAVIOR_ONLY` vs `SAGE_INFORMED`. `GAMMA_CONFIRMED` vs `GAMMA_UNAVAILABLE`.
No gamma points from technical substitutes. Fixed DTE bands. No reweighting.
Hard vetoes. Holiday-adjusted EOW. Absolute put delta. Grade boundaries before rounding.
High score + veto = `NO_TRADE`. Thesis preserved. Authority disabled on every packet.
Live quotes, chains, and orders raise `LiveIngestionBlocked`.
Journal is append-only.

## Tests

Local offline: `PYTHONPATH=. pytest -q` (synthetic fixtures, `VECTOR_OFFLINE=1`).
Demo: `PYTHONPATH=. python -m vector.demo.run_stage1` with `FIXTURE_LABEL=SYNTHETIC`.

## Missing access

No confirmed OPRA entitlement. No live `ESTABLISHED` SAGE freeze. Moomoo GEX API not connected. No historical options/GEX archive.

Proposed Stage 2 provider: Webull read-only **after** Owner answers `docs/WEBULL-ENTITLEMENT-QUESTIONS.md`. An app subscription is not programmatic access.

## Decisions for review

1. `SUBFACTOR_SHARES` in `vector/config.py`
2. Research holiday calendar 2025-2027
3. First-order Greeks Taylor scenarios
4. Webull as Stage 2 candidate only after entitlement answers
5. Delta outside 0.35-0.50 scores partial credit only
6. Leave `scoring.md` interpolation text intact vs edit later

## Next step

Stage 2 read-only board against one authorized provider after Owner answers entitlement questions. Paper and live stay disabled.

```text
RESEARCH_ENABLED = true
PAPER_EXECUTION_ENABLED = false
LIVE_EXECUTION_ENABLED = false
VECTOR_WRITES_TO_SAGE = false
```


---

## ChatGPT review — 2026-09-16

Reviewed build head `e5ef1be28006bf79e5a8252c7842f515efd4c1b5`, PR #1, repository inventory, pipeline, contracts, SAGE adapter, eligibility, scoring/scenarios, red-team and relevant adapter tests. Exact-head CI runs 35045663711 and 35045660681 are successful. Workflow runs offline pytest and demo. This is source/CI review, not an independently rerun local test suite or a complete security audit.

Decision: STAGE_1_CORRECTIONS_REQUIRED. NO_GO for live ingestion or A/A_PLUS promotion. Missing modules/reference files have landed; upload completion is accepted. Green CI does not resolve the following concrete defects.

### P0 — SAGE trust boundary

Files: vector/sage/adapter.py, vector/contracts/sage.py, tests/test_sage_adapter.py.

ingest accepts established=true and any nonempty regime without required schema, cutoff, receipt, freeze identity or validated posterior. For example {"established": true, "regime": "risk-on"} can become SAGE_INFORMED; CALL plus transmission_observed=true makes it CONSISTENT. Unknown sources other than SIGIL are not excluded. Future cutoff passes the age-only check. _regime_polarity invents a universal call/put mapping from substrings such as bull/tight; macro-to-security transmission cannot be inferred from a name.

The existing established-consistency test explicitly blesses a made-up schema and a posterior totaling 0.61.

Correction: keep production ESTABLISHED/SAGE_INFORMED admission disabled until an actual agreed SAGE contract exists. Retain explicit unavailable/not-established handling, preserve raw supplied context separately, and isolate synthetic established fixtures from production ingress. Remove substring regime-to-direction inference. Add missing-source/schema/time, future-time, malformed distribution and forged-established regression cases. No SAGE changes.

### P0 — Incomplete eligibility and input coherence

Files: vector/eligibility/gates.py, vector/contracts/options.py, vector/contracts/market.py, vector/pipeline.py.

Missing quote/Greeks timestamps skip freshness checks; future timestamps pass. Numeric validation covers bid/ask finiteness only, and negative quotes are not rejected. Caller-supplied DTE is not bound to expiration/cutoff. OCC identity checking is a substring test; right, strike and expiry are not matched. Listed-expiration verification is optional. Pipeline does not bind ticker/direction, contract underlying/right, market symbol and gamma underlying.

Correction: require and validate mandatory fields before scoring/promoting. Derive DTE under an explicit date convention; parse or otherwise validate canonical contract identity; reject missing/future/naive timestamps according to a declared policy; validate finite/ranged quotes, Greeks, IV and strikes. Validate market/feature/gamma freshness and symbol/expiry coverage. Missing official listings/calendar coverage cannot silently pass. Keep unsupported inputs non-promotable.

### P1 — Scoring rewards wrong-direction or merely asserted evidence

File: vector/scoring/engine.py and vector/contracts/market.py.

Gamma runway uses abs(wall-spot): a call wall below spot or put wall above spot can receive full runway credit. RS uses abs(rs) without trade direction. Presence booleans confer full flow/transmission/catalyst credit without evidence derivation. Nonempty expected_response receives target-distance points without a numeric target. One alternative satisfies comparison credit despite the required nearby strike AND nearby expiration.

Correction: define directional calculations; derive eligibility/features from timestamped evidence, or label asserted inputs as synthetic only. Validate numeric target/invalidation geometry, catalyst timing against holding horizon, and both required comparisons. Add paired opposite-direction tests and missing-evidence tests. Do not tune grades to hide these failures.

### P1 — Scenario and promotion gates

Files: vector/scoring/scenarios.py, vector/pipeline.py, vector/redteam/critique.py.

Scenario P&L starts at midpoint and omits exit spread/fees; the separate support check only adds entry slippage. Vega/IV units are unspecified. Support is a hard-coded +/-4% move after seven days at unchanged IV, not the candidate's actual target/horizon. Missing Greeks become zero in scenarios. Unsupported economics earns partial score rather than a veto; missing comparisons/invalidation can also merely lose points. Red-team then promotes >=82 without checking these mandatory conditions.

Correction: bind scenarios to explicit units, actual thesis horizon and targets; use disclosed executable cost assumptions and consistent net P&L. Taylor approximations must be labeled local approximations with bounded applicability, not validated pricing across arbitrary scenarios. Missing inputs produce unavailable scenarios. Require supportive economics, valid thesis geometry and required comparisons for promotion. The stub critique must not claim a completed comprehensive red-team review.

### Additional build hygiene

Reconcile conflicting skill instructions now rather than retaining interpolation text and relying on readers to discover docs/CONFLICTS.md. Pin/install the project dependencies through the declared project configuration in CI rather than pip installing unconstrained pydantic/pytest alone. Preserve original evidence/thesis snapshots without mutating caller-owned contracts while gating.

### Authorized next work

Implement these corrections and focused offline regression tests on the same branch, in coherent reviewable commits. Do not start Webull connections, merge, deploy, or add orders. Provider entitlement questions may be gathered in parallel; entitlement alone will not resolve code defects.

Return final SHA, exact-head CI and an updated mailbox mapping each finding to its fix/tests. Existing scope remains BEHAVIOR_ONLY research with synthetic/offline inputs until reviewed; no claim of validated strategy performance.

SAGE remains untouched. Paper/live execution disabled. No trade authorization.
