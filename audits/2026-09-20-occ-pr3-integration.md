# OCC PR #3 ported onto accepted Stage 1 — 2026-09-20

```
STAGE_1_ARCHITECTURE = REVIEW_ACCEPTED
REVIEW_HEAD_ACCEPTED = c3acc9594003386c5334dab5f50ab8cd223d11bf
OCC_SOURCE = fix/occ-parser-validation@710369ce1d7a3f7a095a4772394a9bb8d93e6818
PR_3 = NOT_MERGED_AS_BRANCH
PR_1 = STILL_HOLD
```

PR #3 was opened against `55dff75`, not the accepted Stage 1 head. Merging that branch would rewind P0/P1 and later Stage 1 locks. The OCC rules are therefore copied forward onto `build/stage-1-contracts` instead of merging PR #3.

## Rules integrated

- ASCII space is the only compactable padding. Tab/newline stay unparseable.
- Hyphen/slash roots are not remapped. `BRK-B` ≠ `BRK.B` ≠ `BRKB`.
- OSI years 2000–2099 only. `format_occ_symbol(1999)` and `2100` return `None`.
- Exact root compare after space-compact. `SPX` ≠ `SPXW`.
- `pad_osi_symbol` refuses invalid calendar dates.

## Unchanged

Sage adapter, SAGE_INFORMED admission, scoring conjunction, nearby-quote freshness, synthetic ingestion, execution locks, no Webull, no merge to `main`.

```
SAGE_INPUT=UNAVAILABLE
SAGE_INFORMED=disabled
SAGE_POINTS=0
LIVE_DATA_INGESTION=NO_GO
LIVE_EXECUTION_AUTHORIZED=FALSE
REVIEW != APPROVAL != TRADE
```

This is not live-chain clearance.
