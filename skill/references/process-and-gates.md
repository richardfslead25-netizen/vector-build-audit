<!-- STAGE-1 RECONCILIATION
Governing authority: approved VECTOR build instructions and Stage 1 code.
Conflicts resolved in docs/CONFLICTS.md.
Binding overrides: fixed DTE bands (no interpolation); missing evidence scores 0;
no gamma points from technical substitutes; do not invent officialFreezeCount when
SAGE is UNAVAILABLE; BEHAVIOR_ONLY vs SAGE_INFORMED; paper/live execution disabled;
grades A_PLUS>=90, A 82<=x<90, B_DEVELOPING 72<=x<82, WATCH 62<=x<72, REJECT<62.
-->

# Process, Gates, and Cycle Checklists

## Evidence hierarchy

| Evidence | Required treatment |
|---|---|
| Live underlying and option chain | Required for a trade-ready contract |
| GEX / flip / walls | Source, symbol, expiry filter, and as-of required |
| Moomoo GEX | Preferred printable desk sensor when available |
| Barchart EOD GEX | Next-day context only; never represented as live OPRA |
| Other vendor GEX | Vendor-labeled model; never merged silently |
| News or X chatter | Hypothesis only until validated |
| SIGIL / SAGE | Upstream context; never rewritten by this skill |
| Missing data | Explicitly unavailable; never estimated as observed |

## Eligibility gates

A candidate receives no actionable score until these gates are evaluated.

### G0 — Freshness

Require timestamps for underlying price, option chain, GEX/flip/walls, macro reading if used, catalyst information, and technical chart interval.

Stale inputs remain visible but cap the candidate at `WATCH`.

### G0b — Fusion (regime vs tape)

After G0, classify fusion as `CONSISTENT`, `INCONSISTENT`, or `INSUFFICIENT`.

If SAGE/SIGIL is `NOT_ESTABLISHED` or engine `ok: false`, fusion at the regime layer is `INSUFFICIENT`. Continue on catalyst and tape. Award zero Sage-confirmation points.

`INCONSISTENT` does not kill a tape-led setup automatically. It cuts macro-transmission points and requires the conflict to be stamped.

Do not use fusion to mint a regime ID.

### G1 — Thesis and catalyst

Require a bullish or bearish thesis, explicit transmission path, a catalyst or identifiable market-structure trigger, expected holding period, alternate path, and mutually exclusive confirmation and invalidation.

An unverified rumor cannot be the sole catalyst.

### G2 — Location and gamma structure

Require either:

1. sourced GEX regime, flip, walls, and expiry filter; or
2. a clearly labeled structure substitute using support/resistance, volume profile, and price action.

If GEX is missing, use `GEX_NOT_PRINTABLE`. Do not invent values. Missing GEX reduces the score ceiling but does not automatically eliminate an otherwise strong catalyst-led setup.

Stage 1 scoring rule: structure substitutes never receive gamma points. Use `GAMMA_UNAVAILABLE`.

### G3 — Contract and liquidity

Require eligible end-of-week expiration from 14–45 DTE; live bid, ask, and mid; spread percentage; open interest; option volume; delta, gamma, theta, and vega; IV and expected move when available; underlying liquidity; comparison with nearby strikes and expirations.

Default directional delta preference is 0.35–0.50. ATM or slightly ITM is allowed when the higher delta materially improves thesis fidelity.

Hard vetoes:

- no reliable live chain
- OI below 100 unless Owner explicitly changes the rule
- spread too wide for realistic entry and exit (default veto above 15% of mid)
- expiration does not cover the catalyst and expected holding period
- far-OTM lottery contract that requires an implausible move
- contract cannot be exited realistically
- DTE outside 14–45

High OI alone does not prove liquidity.

### G4 — Independent challenge

Require a red-team outcome of `PROMOTE`, `REDUCE`, `KILL`, or `OPPOSITE_PATH`.

The challenge must test data freshness, gamma interpretation, catalyst pricing, macro/tape conflict, horizon mismatch, liquidity, IV crush, factor concentration, and invalidation quality.

`PROMOTE` is research eligibility only. It is not paper or live authority.

## Cycle checklists

### Premarket

1. Validate overnight macro, economic, company, and geopolitical catalysts from primary sources where possible.
2. Read SIGIL/SAGE only if timestamped; otherwise mark unavailable.
3. Examine rates, DXY, oil, gold, BTC, volatility, credit, breadth, futures, sectors, and leading securities.
4. Create bullish and bearish transmission lists.
5. Stamp printable GEX/flip/walls for SPX/SPY, QQQ, IWM, and shortlisted names.
6. Mark VAH/VAL/POC, major levels, 50 EMA, both MACDs, ADX/DI, RSI(34), relative strength, and volume context.
7. Publish a preliminary board. Do not call any contract trade-ready before a live chain and opening confirmation.
8. State the exact opening triggers required for promotion or kill.

### Opening confirmation

After enough opening data exists:

1. Refresh price, volume, breadth, and relative strength.
2. Classify sweep versus run.
3. Refresh GEX if the source is genuinely intraday; otherwise retain the EOD stamp.
4. Pull live option chains.
5. Apply every gate and compute DTE-adjusted scores.
6. Publish qualifying calls and puts. Empty boards are valid.
7. Execute only if paper authority is active, every gate passes, and the candidate is `A` or `A_PLUS`. Write a pretrade record first. Real-money execution is never permitted. Stage 1 paper and live remain disabled.

### Midday

Update only when a trigger fires, gamma flip or walls materially migrate, a catalyst changes, a candidate is invalidated, or a previously blocked candidate clears a gate.

Do not rescore unchanged evidence. Preserve the original score and append the revised score.

For each changed candidate return `UNCHANGED`, `PROMOTED`, `REDUCED`, `INVALIDATED`, or `OPPOSITE_PATH`.

### Close

Record original score and state; trigger and paper fill if any; underlying and option result; MFE and MAE; IV, theta, and spread effects; whether GEX behavior matched the sourced model; whether catalyst and transmission worked as predicted; thesis fidelity; what evidence was early, late, wrong, or missing; whether the contract, strike, and DTE were appropriate; one proposed improvement.

Do not change scoring weights from one outcome. Place changes into a validation queue requiring a meaningful sample and Owner approval.

### Deep dive (single ticker)

Do not accept a proposed direction as correct.

1. Establish bullish, bearish, and no-trade paths.
2. Test macro/sector/security transmission.
3. Inspect gamma sign, flip, call wall, put wall, and room to target.
4. Determine sweep or run.
5. Evaluate the technical stack.
6. Compare eligible end-of-week contracts 14–45 DTE.
7. Score the best call and best put independently.
8. Reject contracts that fail liquidity, IV/expected-move, catalyst-clock, or exit-realism gates.
9. Red-team the leading contract.
10. Return `PROMOTE`, `REDUCE`, `KILL`, or `OPPOSITE_PATH` with the complete packet.

### Sweep vs run

- Sweep — level is briefly taken and reclaimed; favors reversal after confirmation.
- Run — price accepts beyond the level and holds/retests; favors continuation.

Do not buy the first breakout wick. Wrong classification is a structure failure, not a reason to average.

## When NO_TRADE is required

`NO_TRADE` is valid and preferred when:

- liquidity or spread vetoes the contract
- available expiration misaligns with thesis timing
- IV is too rich versus expected move / RV
- macro and tape conflict materially
- catalyst is misaligned or already priced
- signal is weak or data is stale or incomplete
- risk/reward is poor after slippage
- the only workable idea is a 0DTE or 1-minute order-flow scalp (`HORIZON_MISMATCH`)
- GEX, SIGIL, short-interest, or a single wick is the sole input
- the desk is forcing a candidate to have something

## Failure modes to refuse

1. Cheap-option first — skip regime → transmission → security chain.
2. Liquidity blindness — high OI or pretty thesis with untradeable spreads.
3. Macro-as-contract — treat SIGIL as strike selection.
4. DTE/holding conflation — force weeklies or ignore IV crush into a catalyst.
5. Horizon mismatch — 0DTE scalp logic forced onto 14–45 DTE.
6. +gamma fade attempted during a true −gamma expansion.
7. Silent weight edits — change production scores without Owner change-control.
8. Lucky-path theater — P&L green with a false thesis.

## Paper vs live

Stage 1 paper and live execution are disabled. A score or `PROMOTE` verdict is research ranking only.
