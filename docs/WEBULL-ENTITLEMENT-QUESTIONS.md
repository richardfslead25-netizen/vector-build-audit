# Webull entitlement questions — Stage 2 gate

Stage 1 does **not** connect Webull. Stage 2 may not connect Webull until the Owner answers these questions in writing.

An app subscription, SuperGrok connection badge, or logged-in mobile session is **not** programmatic access. Do not assume OPRA research-export rights from a retail quote screen.

Proposed use if authorized later:

```text
provider: Webull
access_method: existing Owner workspace connector, read-only market-data tools
scope: quotes, bars, snapshots, option chains, Greeks if entitled, OI if entitled
not in scope: order placement, account trading, SAGE writes
storage: research snapshots with provenance; no restricted redistribution into git
```

## 1. Intended access method

- [ ] Which exact path is authorized?
  - Webull public OpenAPI / broker API
  - Webull in-app market-data only (no API)
  - Owner workspace connector tools already attached to Grok (quotes, bars, snapshots)
  - Manual export / CSV / screenshot
- [ ] What is the legal account holder and the application name on any developer registration?
- [ ] Is a separate market-data agreement required beyond the brokerage customer agreement?
- [ ] What is the documented base URL / tool surface, rate limit, and authentication type (OAuth, token, session cookie — describe type only, never paste secrets)?

## 2. Permitted API access

- [ ] Does the current plan allow **programmatic** retrieval of:
  - underlying last, bid/ask, timestamp
  - listed expirations
  - option contract identity (OCC / OSI)
  - option bid / ask / last / volume
- [ ] Which symbols are covered (US listed equities / ETFs only)?
- [ ] Are index options, weeklies, and holiday-adjusted Friday substitutes included?
- [ ] Are adjusted / nonstandard deliverables identifiable so VECTOR can exclude them?
- [ ] What happens on 401 / 403 / 429 — explicit error vs empty chain?
- [ ] May VECTOR call the connector from an offline-first research process that records provenance?

## 3. Real-time versus delayed options quotes

- [ ] Are option NBBO quotes real-time OPRA, 15-minute delayed, snapshot-on-request, or unknown?
- [ ] Is underlying equity last real-time while options are delayed (mixed freshness)?
- [ ] What timezone and clock source is stamped on quote_time?
- [ ] What is the maximum acceptable quote age for a trade-ready row (Stage 1 default: 15 minutes; premarket without live chain stays WATCH)?
- [ ] Can VECTOR distinguish REAL_TIME / DELAYED / HISTORICAL / UNKNOWN without guessing?

## 4. Greeks

- [ ] Are delta, gamma, theta, vega, and IV supplied by Webull, computed locally, or unavailable?
- [ ] If supplied: model name, dividend / rate assumptions, American vs European, as-of timestamp separate from quote_time?
- [ ] Put delta sign convention (negative vs absolute)? VECTOR already uses abs(delta) for the 0.35–0.50 band.
- [ ] Are Greeks available for 14–45 DTE weeklies on liquid underlyings?
- [ ] If Greeks are missing, Stage 2 must veto promotion (`MISSING_DELTA` / `MISSING_GAMMA` / `MISSING_THETA` / `MISSING_VEGA`). Confirm that is acceptable.

## 5. Open-interest reporting date

- [ ] Does the payload include open interest **and** the OI reporting date (usually prior session)?
- [ ] Is volume session volume or cumulative?
- [ ] Can VECTOR store OI as of the reporting date without treating it as live positioning?
- [ ] Minimum OI gate remains 100. Confirm the field is contract-level, not underlying-level.

## 6. Storage and redistribution permissions

- [ ] May VECTOR persist snapshots locally for the evaluation journal (append-only research log)?
- [ ] May VECTOR write **derived** research packets (scores, vetoes, scenarios) to this private GitHub repo?
- [ ] May VECTOR commit raw Webull / OPRA quotes, chains, or Greeks into git? Default answer required: **no**.
- [ ] Retention period and deletion duty?
- [ ] Are hashes allowed as content identity without storing the quote body?

## 7. Cost and entitlement upgrade

- [ ] Current plan name and whether options Level 1 / Level 2 / OPRA is included.
- [ ] Incremental cost to obtain real-time options quotes + Greeks + OI if not already entitled.
- [ ] Any prohibition on using the data for an automated research board (even with execution disabled)?

## Binding Stage 1 / Stage 2 rules

```text
RESEARCH_ENABLED = true
PAPER_EXECUTION_ENABLED = false
LIVE_EXECUTION_ENABLED = false
VECTOR_WRITES_TO_SAGE = false
APP_SUBSCRIPTION_IS_NOT_API_ACCESS = true
```

Until every mandatory question above is answered and the entitlement is `authorized-research-readonly`, the Webull client stays a stub that raises `LiveIngestionBlocked`.
