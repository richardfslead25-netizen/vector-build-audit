from datetime import datetime, timezone
from tests.helpers import make_bars
from vector.contracts.enums import SweepRun
from vector.features.technical import classify_sweep_run, compute_features

def test_compute_features_deterministic():
    bars = make_bars(60)
    a = compute_features("SYN", bars, as_of=datetime(2026,9,15,tzinfo=timezone.utc))
    b = compute_features("SYN", bars, as_of=datetime(2026,9,15,tzinfo=timezone.utc))
    assert a.momentum_level == b.momentum_level
    assert a.ema50 is not None and "ema50" in a.formulas

def test_missing_history_is_labeled_not_invented():
    pkt = compute_features("SYN", make_bars(5))
    assert "insufficient_history" in pkt.missing
    assert pkt.ema50 is None

def test_sweep_versus_run():
    bars = make_bars(10, start=100, step=0)
    for b in bars[-2:]:
        b.high, b.close, b.low = 101.0, 100.8, 100.5
    assert classify_sweep_run(bars, 100.2) is SweepRun.RUN
    bars = make_bars(10, start=100, step=0)
    bars[-2].high, bars[-2].close = 101.0, 100.8
    bars[-1].high, bars[-1].close, bars[-1].low = 100.3, 99.8, 99.5
    assert classify_sweep_run(bars, 100.2) is SweepRun.SWEEP
