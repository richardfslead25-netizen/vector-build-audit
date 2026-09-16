# Proposed Stage 2 market-data provider

Stage 1 does not connect a live provider. Live fetch and order methods raise `LiveIngestionBlocked`.

Primary candidate: Webull read-only market data **if and only if** programmatic entitlement is confirmed.

Required fields:

- underlying last + observation time
- OCC / OSI identity, right, strike, listed expiration, multiplier
- bid / ask / mid / dollar spread / percent spread
- session volume
- open interest + OI reporting date
- delta, gamma, theta, vega, IV + Greeks calculation time
- daily bars + declared benchmark bars

Optional (zero points if missing): volume profile, breadth, order flow, vendor GEX with full stamp (vendor, methodology, coverage, model as-of, units, sign convention, spot reference).

See `docs/WEBULL-ENTITLEMENT-QUESTIONS.md` for the full questionnaire.

No secrets in this repository. No order-submission scope. No SAGE writes.
