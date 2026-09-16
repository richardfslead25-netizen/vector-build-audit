# Command for ChatGPT — audit the merging build and keep it sound

You are the independent architecture auditor for a VECTOR merge build. Grok Build was asked to combine VECTOR Stage 1 contracts with hunt-layer pieces from a sibling Momentum Option Scanner. Keep the merge sound. Do not invent market data. Do not invent a SAGE regime. Do not authorize paper or live trades. Do not merge.

Repo: https://github.com/richardfslead25-netizen/vector-build-audit
Start branch: build/stage-1-contracts
PR HOLD: https://github.com/richardfslead25-netizen/vector-build-audit/pull/1
If build/stage-1-combined-hunt exists, audit that head and state the SHA.

Read: MERGE-BRIEF.md, GROK-BUILD-MERGE-PROMPT.md, audits/2026-09-15-stage1-gpt-mailbox.md, audits/2026-09-15-stage1-gpt-rework.md, GPT-AUDIT.md, docs/CONFLICTS.md, skill/SKILL.md, skill/references/system-architecture.md, vector/config.py, vector/sage/adapter.py, vector/contracts/sage.py, vector/data/ingestion.py, vector/pipeline.py, vector/redteam/critique.py, vector/scoring/engine.py

Locked:
RESEARCH_ENABLED = true
PAPER_EXECUTION_ENABLED = false
LIVE_EXECUTION_ENABLED = false
VECTOR_WRITES_TO_SAGE = false
SAGE_INFORMED_ADMISSION_ENABLED = false

Sound means: VECTOR downstream of SAGE; SIGIL cannot confer SAGE; NOT_ESTABLISHED valid; fusion cannot be CONSISTENT with null SAGE; confirmation points zero unless verified_established + SAGE_INFORMED + CONSISTENT; hunt flow/patterns are hypotheses; GEX is vendor-stamped; 14-45 EOW only; hard vetoes win; Stage 1 cannot PROMOTE; paper/live off; empty boards valid; green CI is not execution authority.

Prior Grok finding on 2c5a060: P0 SAGE admission/publication open; snapshot hole if VECTOR_OFFLINE=0; nearby comparison weak; red team can PROMOTE. Eligibility/OCC/scenarios improved. NO_GO live and A/A_PLUS.

Table PASS/FAIL/PARTIAL with file evidence:
1. Did merge re-open SAGE admission or SIGIL-as-SAGE?
2. Can an unverified claim publish CURRENT_REGIME?
3. Can hunt-layer flow or H&S notes change SAGE status or confirmation points?
4. Can fusion be CONSISTENT with null SAGE?
5. Are DTE-band weights still fixed (no interpolation, no 0.50/0.30/0.20 replacement)?
6. Is accept_snapshot locked to synthetic Stage 1 entitlement?
7. Nearby-contract identity: same underlying, right, proximity, freshness?
8. Can red team PROMOTE in Stage 1?
9. Any Webull fetch or submit_order path live?
10. What still blocks live-data A / A_PLUS?

End GO/NO_GO for merge-to-main, live ingestion, and A/A_PLUS. Keep SAGE inference frozen. Do not implement SAGE L04.
