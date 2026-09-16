# Proposed Stage 2 market-data provider

Stage 1 does not connect a live provider.

Primary candidate: Webull read-only market data already connected to the Owner workspace.
Required fields: underlying last+time, OCC identity, bid/ask/mid/spread, volume, OI+report date, Greeks+time, IV, listed expirations, daily bars + benchmark.
Optional (zero points if missing): VP, breadth, order flow, vendor GEX with full stamp.

Open questions before Stage 2 code lands:
1. OPRA research-export entitlement vs in-app only
2. Delayed vs real-time
3. Historical chain availability
4. Redistribution into this repo allowed?
5. Cost of any upgrade

No secrets in this repository. No order-submission scope.
