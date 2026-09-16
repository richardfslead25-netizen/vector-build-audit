"""Deterministic market-behavior features."""
from __future__ import annotations
import math
from datetime import datetime
from vector.config import DEFAULT_SETTINGS, FeatureConfig
from vector.contracts.enums import SweepRun
from vector.contracts.market import Bar, FeaturePacket

def _closes(bars: list[Bar]) -> list[float]:
    return [b.close for b in bars]

def _ema(values: list[float], span: int) -> float | None:
    if len(values) < span:
        return None
    alpha = 2.0 / (span + 1.0)
    ema = values[0]
    for v in values[1:]:
        ema = alpha * v + (1.0 - alpha) * ema
    return ema

def _stdev(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(var)

def compute_features(symbol, bars, *, benchmark_bars=None, implied_vol=None, as_of=None,
                     config=None, vah=None, val=None, poc=None, level=None) -> FeaturePacket:
    cfg = config or DEFAULT_SETTINGS.features
    missing = []
    formulas = {
        "ema50": f"EMA(close, span={cfg.trend_lookback})",
        "momentum_level": f"close / close[-{cfg.momentum_lookback}] - 1",
        "momentum_change": f"short_ret[{cfg.momentum_change_lookback}] - long_ret[{cfg.momentum_lookback}]",
        "relative_volume": f"last_volume / mean(volume[-{cfg.relative_volume_lookback}:-1])",
        "relative_strength": f"symbol_ret[{cfg.rs_lookback}] - benchmark_ret[{cfg.rs_lookback}]",
        "realized_vol": f"stdev(log_return[-{cfg.realized_vol_lookback}:]) * sqrt(252)",
        "sweep_vs_run": "SWEEP if pierce then reclaim; RUN if closes hold beyond level",
    }
    if len(bars) < cfg.min_history:
        missing.append("insufficient_history")
    closes = _closes(bars)
    last = closes[-1] if closes else None
    ema50 = _ema(closes, cfg.trend_lookback) if closes else None
    trend = None
    if last is not None and ema50 is not None:
        trend = "ABOVE_EMA50" if last >= ema50 else "BELOW_EMA50"
    elif last is not None:
        missing.append("ema50")
    mom = None
    if len(closes) > cfg.momentum_lookback and closes[-1 - cfg.momentum_lookback] != 0:
        mom = closes[-1] / closes[-1 - cfg.momentum_lookback] - 1.0
    else:
        missing.append("momentum_level")
    mom_chg = None
    if len(closes) > cfg.momentum_lookback:
        short_n = cfg.momentum_change_lookback
        if len(closes) > short_n and closes[-1 - short_n] != 0 and closes[-1 - cfg.momentum_lookback] != 0:
            mom_chg = (closes[-1] / closes[-1 - short_n] - 1.0) - (closes[-1] / closes[-1 - cfg.momentum_lookback] - 1.0)
    else:
        missing.append("momentum_change")
    rvol = None
    if len(bars) > cfg.relative_volume_lookback:
        hist = [b.volume for b in bars[-cfg.relative_volume_lookback - 1:-1]]
        mean_v = sum(hist) / len(hist) if hist else 0.0
        if mean_v > 0:
            rvol = bars[-1].volume / mean_v
        else:
            missing.append("relative_volume")
    else:
        missing.append("relative_volume")
    rs = None
    if benchmark_bars and len(benchmark_bars) > cfg.rs_lookback and len(closes) > cfg.rs_lookback:
        b_closes = _closes(benchmark_bars)
        if b_closes[-1 - cfg.rs_lookback] != 0 and closes[-1 - cfg.rs_lookback] != 0:
            rs = (closes[-1] / closes[-1 - cfg.rs_lookback] - 1.0) - (b_closes[-1] / b_closes[-1 - cfg.rs_lookback] - 1.0)
    else:
        missing.append("relative_strength")
    rv = None
    if len(closes) > cfg.realized_vol_lookback:
        window = closes[-(cfg.realized_vol_lookback + 1):]
        log_rets = [math.log(b / a) for a, b in zip(window, window[1:]) if a > 0 and b > 0]
        sd = _stdev(log_rets)
        if sd is not None:
            rv = sd * math.sqrt(252.0)
    else:
        missing.append("realized_vol")
    sweep = classify_sweep_run(bars, level, cfg) if level is not None else SweepRun.UNCLASSIFIED
    structure = None
    if last is not None and level is not None:
        if last > level * (1.0 + cfg.breakout_buffer_pct):
            structure = "BREAKOUT"
        elif last < level * (1.0 - cfg.breakout_buffer_pct):
            structure = "BREAKDOWN"
        else:
            structure = "AT_LEVEL"
    return FeaturePacket(
        symbol=symbol, as_of=as_of or (bars[-1].timestamp if bars else None),
        bar_interval=cfg.bar_interval,
        lookbacks={"trend": cfg.trend_lookback, "momentum": cfg.momentum_lookback,
                   "momentum_change": cfg.momentum_change_lookback,
                   "relative_volume": cfg.relative_volume_lookback, "rs": cfg.rs_lookback,
                   "realized_vol": cfg.realized_vol_lookback, "min_history": cfg.min_history},
        close=last, ema50=ema50, trend=trend, momentum_level=mom, momentum_change=mom_chg,
        relative_volume=rvol, relative_strength=rs, realized_vol=rv, implied_vol=implied_vol,
        vah=vah, val=val, poc=poc, sweep_or_run=sweep, structure=structure,
        missing=missing, formulas=formulas,
    )

def classify_sweep_run(bars, level, config=None) -> SweepRun:
    cfg = config or DEFAULT_SETTINGS.features
    if level is None or len(bars) < max(cfg.sweep_reclaim_bars, cfg.run_hold_bars) + 1:
        return SweepRun.UNCLASSIFIED
    last_n = bars[-(cfg.run_hold_bars + cfg.sweep_reclaim_bars):]
    pierced_up = any(b.high > level for b in last_n)
    pierced_down = any(b.low < level for b in last_n)
    hold_up = all(b.close > level for b in bars[-cfg.run_hold_bars:])
    hold_down = all(b.close < level for b in bars[-cfg.run_hold_bars:])
    reclaim_down = pierced_up and bars[-1].close < level
    reclaim_up = pierced_down and bars[-1].close > level
    if hold_up or hold_down:
        return SweepRun.RUN
    if reclaim_down or reclaim_up:
        return SweepRun.SWEEP
    return SweepRun.UNCLASSIFIED
