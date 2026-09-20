# Issue #5 discovery runtime P0/P1 corrections

Parent: `dabf813e3c93909a858b63119d9b4878349e7c3f`

P0 `official_freeze_admitted()` now requires verified_established + ESTABLISHED + SAGE_INFORMED + freeze_identity. Incomplete constructed contexts stay INSUFFICIENT.

P1 Regime tokens in commentary no longer force INSUFFICIENT or block promotion when an independently admitted freeze already exists. Tokens still cannot mint a freeze.

Sage adapter, scoring, OCC, pipeline unchanged.
