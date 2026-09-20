# Issue #5 documentation slice — External Commentary → Candidate Discovery

Date: 2026-09-20
Assignment: explicit docs-only open of Issue #5.
Parent HEAD: `b0999882391a72e19f178f88a2940751f7f65833`
Branch: `build/stage-1-contracts`

## Problem solved

Issue #5 was queued as a candidate-discovery specification. This slice writes that specification and nothing else.

## Changed files

- `skill/references/external-commentary-discovery.md` (new)
- `audits/2026-09-20-issue5-commentary-discovery-spec.md` (this note)

## Byte-unchanged

Scoring engine, DTE bands, Sage adapter, OCC identity, pipeline comparison freshness, authority defaults, Webull modules, ingestion.

## Tests

None added. Issue #5 listed future acceptance cases; they are documentation only.

## Limitations

No runtime watchlist, no source fetcher, no schema code. Discovery rows cannot appear on the Stage 1 board from this commit.

## Next concrete step

ChatGPT reviews this specification. Runtime code is not authorized by this commit.

```
ISSUE_5_SPEC = DOCS_LANDED_PENDING_REVIEW
PR_1 = HOLD
WEBULL = HOLD
SAGE_INPUT = UNAVAILABLE
SAGE_INFORMED = disabled
SAGE_POINTS = 0
LIVE_DATA_INGESTION = NO_GO
PAPER_EXECUTION_ENABLED = FALSE
LIVE_EXECUTION_AUTHORIZED = FALSE
0DTE = PROHIBITED
REVIEW != APPROVAL != TRADE
```
