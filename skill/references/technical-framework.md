<!-- STAGE-1 RECONCILIATION
Governing authority: approved VECTOR build instructions and Stage 1 code.
Conflicts resolved in docs/CONFLICTS.md.
Binding overrides: fixed DTE bands (no interpolation); missing evidence scores 0;
no gamma points from technical substitutes; do not invent officialFreezeCount when
SAGE is UNAVAILABLE; BEHAVIOR_ONLY vs SAGE_INFORMED; paper/live execution disabled;
grades A_PLUS>=90, A 82<=x<90, B_DEVELOPING 72<=x<82, WATCH 62<=x<72, REJECT<62.
-->

# Technical Framework

Use technical evidence as confirmation and timing, not as a standalone contract generator.

## Required stack

Evaluate and stamp as-of for:

- Price relative to the 50 EMA
- MACD 8-17-9 as early warning
- MACD 12-26-9 as confirmation
- ADX(14), +DI, and −DI
- RSI(34)
- Support and resistance
- Relative strength against sector and index
- Volume and accumulation/distribution
- Momentum level versus momentum acceleration
- Breakouts, breakdowns, failed breaks, wedges, triangles, rectangles, and head-and-shoulders patterns when objectively present
- Fibonacci 0.382, 0.500, and 0.618 retracements based on a clearly identified swing
- VAH, VAL, and POC
- Order flow as the final confirmation, not the original thesis

If a study cannot be printed, write the study name plus `UNAVAILABLE`. Do not fabricate oscillator values.

## Trend and momentum

- Price above the 50 EMA is bullish context; below is bearish context. Context is not an entry.
- MACD 8-17-9 turning is early warning only. Do not promote on early MACD alone.
- MACD 12-26-9 alignment is confirmation.
- ADX(14) rising with +DI > −DI supports a long-call expansion path.
- ADX(14) rising with −DI > +DI supports a long-put expansion path.
- Low ADX inside value with no catalyst is usually `NO_TRADE` or `WATCH`.
- RSI(34) is swing condition, not a standalone trigger.
- Report momentum level and momentum acceleration as two fields.

Near 14–21 DTE, acceleration and volume outweigh a slow existing trend.
Near 36–45 DTE, durable trend and transmission outweigh a one-bar acceleration spike.

## Retracement and structure

Identify the active swing first. If the swing is not identifiable, do not invent Fibonacci levels.

- Inspect 0.382, 0.500, and 0.618.
- Prefer 0.618 only with reversal-price confirmation.
- Require a reversal candle, failed breakdown/breakout, or other objective reclaim.
- Name support/resistance as zones with source.
- Chart patterns count only when objectively present.

## Volume profile

- Above VAH — premium location.
- Below VAL — discount location.
- Rising POC — bullish context.
- Falling POC — bearish context.
- Inside value without a catalyst or GEX interaction — lower priority.

## Horizon filter

If the technical thesis only works as a 1-minute order-flow scalp, classify `HORIZON_MISMATCH` and return `NO_TRADE`.
