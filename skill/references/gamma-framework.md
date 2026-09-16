# Gamma Framework

Treat GEX as a vendor model, not verified dealer inventory.

Always record:

- source
- symbol
- as-of time
- expiration or expiry filter
- gamma regime
- gamma flip
- call wall
- put wall

Never mix conflicting vendor models into one undocumented number. Never use a wall from one expiry filter as if it describes the entire chain.

Walls are zones, not exact ticks. They migrate and can be overwhelmed by major news or scheduled events. Recalculate the thesis if a wall or flip migrates through spot.

0DTE / futures scalp logic is not the 14–45 DTE default. Use GEX, overnight volume profile, and order flow for bias filter, location/invalidation, and entry-window timing. Express with long calls or long puts.

## Required GEX stamp

```text
SOURCE =
SYMBOL =
AS_OF =
EXPIRY_FILTER =
REGIME = POSITIVE | NEGATIVE | NEAR_FLIP | GEX_NOT_PRINTABLE
FLIP =
CALL_WALL =
PUT_WALL =
HVL_OR_AG_PEAK = <value or NOT_MARKED>
```

If GEX cannot be printed, write `GEX_NOT_PRINTABLE` and use a labeled structure substitute. Do not invent MenthorQ, Quantpower, Geeks of Finance, or SpotGamma walls.

## Positive gamma

Expect more pinning, containment, and mean reversion. Dealer hedging tends to sell strength and buy weakness.

Preferred long-premium setups:

- long puts after confirmed rejection at a call wall, VAH, or premium extreme
- long calls after confirmed defense at a put wall, VAL, or discount extreme
- reduced size or `NO_TRADE` inside value with no edge
- avoid paying rich IV for a deep directional move when the map supports containment

Confirmation should include rejection/absorption, reversal structure, volume response, or reclaim failure.

Require a clear target and reasonable IV because positive gamma can suppress realized movement.

Do not import credit-spread or iron-condor logic into this skill. Long premium only.

## Negative gamma

Expect greater volatility and directional amplification. Dealer hedging can chase.

Preferred setups:

- long calls after an upside run and successful retest
- long puts after a downside run and failed reclaim
- prioritize momentum acceleration, relative strength/weakness, and volume
- manage aggressively because a return to positive gamma can erase profits

Require momentum, acceleration, volume, and adequate distance to the next wall.

Do not buy the first breakout wick.

## Near the gamma flip

Do not assume calm or neutrality. Volatility is often highest near zero.

Require:

- price acceptance
- momentum
- volume
- room to the next wall
- supportive GEX path beyond the flip

A flip reclaim may support a call toward the call wall.
A flip loss may support a put toward the put wall.
Reject the trade if the next wall is too close to justify the premium.

If GEX decays beyond the broken level, treat false-break risk as elevated.

## Wall and magnet rules

- Call wall — potential resistance, magnet, or breakout trigger depending on gamma regime.
- Put wall — potential support, magnet, or breakdown trigger depending on gamma regime.
- High-volume / high-absolute-gamma nodes — stronger magnets than thin bars.
- Thin gamma bars matter less.
- Positive-gamma read — call resistance is a fade magnet; put support is a buy magnet.
- Negative-gamma read — the same walls become breakout fuel after accept/retest.
- Price above a high-volume gamma node can act as a local containment window; below it can act as a local expansion window. Stamp the source before using that mapping.

## Sweep versus run

| Classification | Tape | Option expression |
|---|---|---|
| Sweep | Level taken and reclaimed | Fade / mean-revert after confirmation |
| Run | Price accepts beyond the level and holds or retests | Continuation after retest hold |

Wrong call = structure fail. Document it. Do not average.

## Volume-profile overlay

- Above VAH — premium location.
- Below VAL — discount location.
- Rising POC — bullish context.
- Falling POC — bearish context.
- Inside value without a catalyst or GEX interaction — lower priority.

Overnight / prior-session VAH–VAL–POC is the default context filter when printable.

Time-liquidity pools (PMH/PML, PWH/PWL, PDH/PDL, swing pools) inform the sweep-versus-run decision for swing options.

## Order flow

Order flow is the final confirmation, not the original thesis.

Stack order — Context → Location → Net premium (if printable) → Order flow last.

If order flow is unavailable, write `OF_ABSENT` and require stronger price-and-volume confirmation.

## Setup archetypes

### Expansion call

Negative gamma or confirmed flip reclaim; upside run and retest; call wall / next positive-gamma node leaves adequate room; MACD frames aligned; ADX/+DI and volume support; liquid 14–45 DTE call with manageable IV.

### Expansion put

Negative gamma or confirmed flip loss; downside run and failed reclaim; put wall / next node leaves adequate room; MACD, ADX/−DI, volume, and relative weakness align; liquid 14–45 DTE put.

### Positive-gamma fade call

Price below value or at put support; seller absorption or bullish reversal; defined target toward POC / HVL / call-side magnet; IV not too expensive for a contained move.

### Positive-gamma fade put

Price above value or at call resistance; buyer exhaustion or bearish reversal; defined target toward POC / HVL / put-side magnet; avoid when price accepts above the wall with expanding volume.

### Catalyst dislocation

Validated new information; market has not fully repriced the security; transmission visible in price, volume, or sector relatives; option IV / expected move still offers asymmetric room; gamma structure provides location and invalidation, not the thesis by itself.

## Predictive templates

### +gamma fade → long put

```text
IF sourced_gamma_regime = POSITIVE
AND underlying is above overnight or prior VAH
AND price taps a sourced call-wall / GX zone
AND (order-flow buyer absorption then seller follow-through OR OF_ABSENT plus bearish structure confirm)
THEN long puts 14–45 DTE toward value or the next support zone
BECAUSE positive-gamma hedging fades strength outside value
INVALIDATED IF hold/reclaim above the wall on rising volume and bullish net premium
OR sourced GEX flips NEGATIVE with continuation
EXPECTED HORIZON = 2–10 sessions (must fit DTE)
```

### −gamma run → long put

```text
IF sourced_gamma_regime = NEGATIVE OR a structure breakdown is confirmed
AND price RUNS (not merely sweeps) a prior swing / weekly pool / neckline
AND chain liquidity and Greeks are printable
THEN long puts 14–45 DTE
BECAUSE negative gamma can amplify continuation after a stop-run
INVALIDATED IF reclaim and hold above the broken pool on rising buy volume
EXPECTED HORIZON = multi-session; NO_TRADE if only a wick sweep
```

### −gamma run → long call

Mirror the expansion-put template with upside acceptance, successful retest, and room to the next call-side wall.

## Guardrails

- GEX never rewrites SIGIL or SAGE.
- GEX never selects a strike by itself.
- Vendor P&L or “accuracy” claims are not desk statistics.
- Earnings, FOMC, CPI, and major geopolitics can overwhelm walls.
- Pair GEX with price action, expected move, and IV. Never use it alone.
