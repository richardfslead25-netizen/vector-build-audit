# OCC parser hardening — Stage 1 slice

**Date:** 2026-09-16 PT  
**Branch:** `fix/occ-parser-validation`  
**Base:** `build/stage-1-contracts`  
**Do not merge to main. Do not start Webull. Paper/live remain off.**

## Problem solved

OCC identity accepted compact and padded OSI but left four rules implicit: tab padding, hyphen/slash roots, YY century wrap, and SPX vs SPXW. Live chains would hit those first.

Chosen rules (explicit, no silent remap):

- ASCII space is the only compactable padding. Tab / newline stay unparseable.
- Hyphen and slash are not mapped to dot or stripped. `BRK-B` / `BRK/B` ≠ `BRK.B` ≠ `BRKB`.
- OSI years are 2000–2099. `format_occ_symbol` returns `None` for 1999 and 2100 instead of emitting `99` that parses as 2099.
- Root compare is exact after space-compact. `SPX` ≠ `SPXW`.
- `pad_osi_symbol` no longer emits a 21-char record for an invalid calendar date.

## Changed files

- `vector/eligibility/identity.py`
- `tests/test_occ_identity.py`
- `audits/2026-09-16-occ-parser-hardening.md`

## Tests

Local offline: `PYTHONPATH=. VECTOR_OFFLINE=1 pytest -q` → 72 passed, including new OCC cases.

## Limitations

- Still no exchange root-alias table. That is intentional until Stage 2 entitlement.
- Strike `0.001` still parses; eligibility `min_strike` remains the veto.
- Listed-expiry / EOW checks stay in `gates.py`, not the parser.

## Next concrete step

Keep this off `main`. ChatGPT can treat it as a Stage 1 correction slice. Do not open live chains on the back of these tests.
