<!-- STAGE-1 RECONCILIATION
Governing authority: approved VECTOR build instructions and Stage 1 code.
Conflicts resolved in docs/CONFLICTS.md.
Binding overrides: fixed DTE bands (no interpolation); missing evidence scores 0;
no gamma points from technical substitutes; do not invent officialFreezeCount when
SAGE is UNAVAILABLE; BEHAVIOR_ONLY vs SAGE_INFORMED; paper/live execution disabled;
grades A_PLUS>=90, A 82<=x<90, B_DEVELOPING 72<=x<82, WATCH 62<=x<72, REJECT<62.
-->

# Gamma Framework

Treat GEX as a vendor model, not verified dealer inventory.

Always record:

- vendor and methodology
- symbol
- as-of time
- expiration or expiry coverage
- units and sign convention
- spot reference
- gamma regime
- gamma flip
- call wall
- put wall

Never mix conflicting vendor models into one undocumented number. Never use a wall from one expiry filter as if it describes the entire chain.

Walls are zones, not exact ticks. They migrate and can be overwhelmed by major news or scheduled events. Recalculate the thesis if a wall or flip migrates through spot.

0DTE / futures scalp logic is not the 14–45 DTE default. Intraday or 0DTE positioning may be contextual evidence but cannot automatically justify a 14–45 DTE holding thesis.

## Required GEX stamp

```text
SOURCE =
SYMBOL =
AS_OF =
EXPIRY_FILTER =
UNITS =
SIGN_CONVENTION =
SPOT_REFERENCE =
REGIME = POSITIVE | NEGATIVE | NEAR_FLIP | GEX_NOT_PRINTABLE
FLIP =
CALL_WALL =
PUT_WALL =
HVL_OR_AG_PEAK = <value or NOT_MARKED>
```

If GEX cannot be printed, write `GEX_NOT_PRINTABLE` and use a labeled structure substitute. Do not invent MenthorQ, Quantpower, Geeks of Finance, or SpotGamma walls.

Stage 1 variants:

- `GAMMA_CONFIRMED` — required gamma evidence is available and valid.
- `GAMMA_UNAVAILABLE` — gamma subfactors receive zero; technical levels remain technical levels.

Never award gamma points for a technical substitute.

## Positive gamma

Expect more pinning, containment, and mean reversion. Dealer hedging tends to sell strength and buy weakness. This is a vendor-model interpretation, not observed inventory.

Preferred long-premium setups:

- long puts after confirmed rejection at a call wall, VAH, or premium extreme
- long calls after confirmed defense at a put wall, VAL, or discount extreme
- reduced size or `NO_TRADE` inside value with no edge
- avoid paying rich IV for a deep directional move when the map supports containment

Do not import credit-spread or iron-condor logic into this skill. Long premium only.

## Negative gamma

Expect greater volatility and directional amplification. Dealer hedging can chase.

Preferred setups:

- long calls after an upside run and successful retest
- long puts after a downside run and failed reclaim
- prioritize momentum acceleration, relative strength/weakness, and volume
- manage aggressively because a return to positive gamma can erase profits

Do not buy the first breakout wick.

## Near the gamma flip

Do not assume calm or neutrality. Volatility is often highest near zero.

Require price acceptance, momentum, volume, room to the next wall, and a supportive GEX path beyond the flip. Reject the trade if the next wall is too close to justify the premium.

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

## Order flow

Order flow is the final confirmation, not the original thesis.

If order flow is unavailable, write `OF_ABSENT` and require stronger price-and-volume confirmation.

## Guardrails

- GEX never rewrites SIGIL or SAGE.
- GEX never selects a strike by itself.
- High open interest is not bullish or bearish positioning.
- Vendor P&L or accuracy claims are not desk statistics.
- Earnings, FOMC, CPI, and major geopolitics can overwhelm walls.
- Pair GEX with price action, expected move, and IV. Never use it alone.
