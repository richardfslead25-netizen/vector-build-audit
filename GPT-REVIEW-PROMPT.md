# GPT review prompt — paste this to ChatGPT

You are the independent architecture auditor for VECTOR Stage 1.

Repo: https://github.com/richardfslead25-netizen/vector-build-audit
Branch to audit: `build/stage-1-contracts` (PR #1). Do not treat `main` as the implementation head.
PR: https://github.com/richardfslead25-netizen/vector-build-audit/pull/1
HOLD. Do not merge. Do not authorize Webull, paper, live, or SAGE writes.

Read in this order:

1. audits/2026-09-15-stage1-gpt-rework.md
2. skill/SKILL.md
3. skill/references/system-architecture.md
4. skill/references/scoring.md
5. skill/assets/DAILY-OPTIONS-OPPORTUNITY-BOARD.md
6. skill/references/gamma-framework.md
7. skill/references/technical-framework.md
8. skill/references/process-and-gates.md
9. skill/references/red-team.md
10. vector/config.py
11. vector/contracts/sage.py
12. vector/sage/adapter.py
13. vector/data/ingestion.py
14. vector/pipeline.py
15. vector/redteam/critique.py
16. tests/test_sage_adapter.py
17. tests/test_journal_and_ingestion.py
18. tests/test_audit_corrections.py
19. docs/CONFLICTS.md

Previous verdict was NO-GO because of a SAGE admission bypass and four other gaps. Owner asked Grok to implement items 1–5 and retarget tests.

Required findings table (PASS / FAIL / PARTIAL) with file evidence:

1. Can ordinary Settings enable production SAGE_INFORMED admission?
2. Can a structurally complete unverified claim publish as ESTABLISHED SAGE output?
3. Does as_public_dict() distinguish claimed vs verified establishment?
4. Can fusion become CONSISTENT while SAGE is null or unverified?
5. Are SAGE-confirmation points zero unless verified_established + SAGE_INFORMED + CONSISTENT?
6. Do timestamp and posterior checks validate only (receipt ≥ cutoff, no coerced bool/string, mass ≤ 1, sum ≈ 1) without repairing SAGE?
7. Does accept_snapshot() require synthetic + entitlement `stage1-synthetic-only` + Stage 1, regardless of VECTOR_OFFLINE=0?
8. Do nearby-contract checks require same underlying, same right, freshness, and actual proximity?
9. Can the red team return PROMOTE in Stage 1?
10. Did scoring.md remove interpolation and structure-as-gamma points?
11. Does the board template expose operating mode, fusion, and verified SAGE?
12. What still blocks live-data A / A_PLUS?

Rules for your review:
- Keep SAGE inference, taxonomy, posterior, persistence, successors, and official freezes frozen.
- Do not invent a freeze count.
- Do not treat green CI as merge authority.
- Quote exact functions and settings.
- End with GO / NO-GO for live-data ingestion and a numbered remaining-work list.
