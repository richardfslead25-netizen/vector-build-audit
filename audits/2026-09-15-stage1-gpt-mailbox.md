# GPT audit mailbox — VECTOR Stage 1

**Date:** 2026-09-15 PT / 2026-09-16 UTC
**Repo:** https://github.com/richardfslead25-netizen/vector-build-audit
**Branch:** `build/stage-1-contracts`
**Base:** `main` @ `4e48067bea5a6415dc3325e698625ad9dfd23e64`
**Do not:** invent SAGE, edit SAGE, authorize paper or live orders.

## Problem solved

`main` had three missing skill references, no typed contracts, no deterministic scorer, and no tests. Stage 1 completes the reference package and lands an offline engine.

## Files added

References: process-and-gates.md, gamma-framework.md, technical-framework.md, DAILY-OPTIONS-OPPORTUNITY-BOARD.md.
Preserved: GPT-AUDIT.md, skill/SKILL.md, system-architecture.md, scoring.md, red-team.md.
New: vector/, tests/, docs/, .github/workflows/ci.yml, this mailbox.

## What works

Read-only SAGE statuses including no invented freeze count on UNAVAILABLE.
SIGIL cannot confer SAGE confirmation. Write methods raise SageWriteError.
BEHAVIOR_ONLY vs SAGE_INFORMED. GAMMA_CONFIRMED vs GAMMA_UNAVAILABLE.
No gamma points from technical substitutes. Fixed DTE bands. No reweighting.
Hard vetoes. Holiday-adjusted EOW. Absolute put delta. Grade boundaries before rounding.
High score + veto = NO_TRADE. Thesis preserved. Authority disabled on every packet.

## Tests

Local offline: `PYTHONPATH=. pytest -q` — 40 passed, 0 failed (`VECTOR_OFFLINE=1`).
Demo: `PYTHONPATH=. python -m vector.demo.run_stage1` with `FIXTURE_LABEL=SYNTHETIC`.
GitHub Actions workflow added; treat local pytest as the Stage 1 result until CI prints on the PR.

## Missing access

No confirmed OPRA entitlement. No live ESTABLISHED SAGE freeze. Moomoo GEX API not connected (prior OTP block). No historical options/GEX archive.

Proposed Stage 2 provider: Webull read-only. See `docs/MARKET-DATA-PROVIDER.md`.

## Decisions for review

1. `SUBFACTOR_SHARES` in `vector/config.py`
2. Research holiday calendar 2025-2027
3. First-order Greeks Taylor scenarios
4. Webull as Stage 2 candidate
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
