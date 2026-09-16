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
- Report momentum level and momentum acceleration as two fields. A strong existing trend and an accelerating move are different signals.

Near 14–21 DTE, acceleration and volume outweigh a slow existing trend.
Near 36–45 DTE, durable trend and transmission outweigh a one-bar acceleration spike.

## Retracement and structure

For swing entries, identify the active swing first. If the swing is not identifiable, do not invent Fibonacci levels.

- Inspect 0.382, 0.500, and 0.618.
- Prefer 0.618 only with reversal-price confirmation.
- Require a reversal candle, failed breakdown/breakout, or other objective reclaim.
- Name support/resistance as zones with source (prior high/low, gap, MA cluster, VP node).
- Chart patterns count only when objectively present. Do not force head-and-shoulders or wedges.

## Volume profile

- Above VAH — premium location.
- Below VAL — discount location.
- Rising POC — bullish context.
- Falling POC — bearish context.
- Inside value without a catalyst or GEX interaction — lower priority.

Overnight / prior-session profile is the default context filter when printable.

## Relative strength and flow hygiene

Before promoting a name:

1. Liquidity and option-volume sort
2. Price break agrees with accumulation/distribution
3. Relative strength versus sector and index agrees with direction
4. IV context and earnings/event date versus chosen DTE
5. Expected-move awareness — the thesis must have room before theta death

Flow disagreeing with a price break is a soft veto. Document or size down. Do not treat raw call volume as bullish or raw put volume as bearish without trade-side and context evidence.

## Order flow

Last confirmation. If unavailable, write `OF_ABSENT` and require stronger price-and-volume confirmation.

Do not lead with tape. Context and location come first.

## Horizon filter

If the technical thesis only works as a 1-minute order-flow scalp, classify `HORIZON_MISMATCH` and return `NO_TRADE` for this skill.

## Stamp for packets

```text
SPOT / AS_OF =
50_EMA = ABOVE | BELOW | UNAVAILABLE
MACD_819 = EARLY_BULL | EARLY_BEAR | FLAT | UNAVAILABLE
MACD_12269 = CONFIRM_BULL | CONFIRM_BEAR | FLAT | UNAVAILABLE
ADX14 / +DI / -DI =
RSI34 =
SWING_USED_FOR_FIB = <description or NONE>
FIB_0382 / 0500 / 0618 =
VAH / VAL / POC =
POC_MIGRATION = RISING | FALLING | FLAT | UNAVAILABLE
RS_VS_SECTOR_AND_INDEX =
VOLUME / A_D =
MOMENTUM_LEVEL =
MOMENTUM_ACCELERATION =
STRUCTURE =
OF = detail | OF_ABSENT
```
