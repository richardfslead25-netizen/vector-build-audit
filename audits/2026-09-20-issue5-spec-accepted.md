# Issue #5 specification REVIEW_ACCEPTED

Date: 2026-09-20
Reviewed commit: `ae21cf3d5afbf93fab1955ed8de0aed780199ed5`
Parent: `b0999882391a72e19f178f88a2940751f7f65833`
Functional OCC base: `6c9a79c4302cf834285f5ee0eb415f3275d10170`

```
ISSUE_5_SPEC = REVIEW_ACCEPTED
ISSUE_5_RUNTIME = QUEUED_NOT_OPENED
PR_1 = HOLD
```

ChatGPT accepted the spec. Diff was two documentation files only.

## Invariant to preserve when a runtime slice is later opened

`publication verified ≠ mechanism verified ≠ transmission observed`

CAPTURED or discovery WATCH must not auto-promote to `PROMOTED_TO_CATALYST_INTAKE` merely because the source quotation is verified.

## Proposed next slice (not opened by this note)

Offline `CandidateDiscoveryRecord` contract plus validation/lifecycle tests on synthetic fixtures.
No news API, Webull, scraper, scheduler, or provider.

A review plus “what I would build next” is not an implementation assignment.

```
STAGE_1_ARCHITECTURE = REVIEW_ACCEPTED
OCC_IDENTITY_HARDENING = ACCEPTED
SAGE_INPUT = UNAVAILABLE
SAGE_INFORMED = disabled
SAGE_POINTS = 0
WEBULL = HOLD
LIVE_DATA_INGESTION = NO_GO
PAPER_EXECUTION_ENABLED = FALSE
LIVE_EXECUTION_AUTHORIZED = FALSE
0DTE = PROHIBITED
REVIEW != APPROVAL != TRADE
```
