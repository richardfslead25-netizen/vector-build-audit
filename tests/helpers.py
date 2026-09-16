
from __future__ import annotations
from datetime import date, datetime, timedelta, timezone
from vector.contracts.enums import DataStatus, GammaRegime, OptionRight
from vector.contracts.market import Bar, FeaturePacket, GammaSnapshot, MarketSnapshot
from vector.contracts.options import OptionContract
from vector.contracts.packet import Thesis
from vector.contracts.provenance import Provenance

def synthetic_provenance(instrument: str) -> Provenance:
    return Provenance(provider="synthetic-fixture", dataset="stage1-offline", instrument=instrument,
        data_status=DataStatus.SYNTHETIC, permitted_use="research-only", entitlement="fixture",
        transformation_version="synthetic-1", lineage="labeled-synthetic", synthetic=True)

def make_bars(n: int = 60, start: float = 100.0, step: float = 0.4):
    out, ts0, price = [], datetime(2026,6,15,20,tzinfo=timezone.utc), start
    for i in range(n):
        price = start + step * i
        out.append(Bar(timestamp=ts0+timedelta(days=i), open=price-0.2, high=price+0.5,
                       low=price-0.5, close=price, volume=1_000_000+i*1000,
                       provenance=synthetic_provenance("SYN-BARS")))
    return out

def make_contract(**kwargs):
    base = dict(underlying="SPY", occ_symbol="SPY261002C00580000", right=OptionRight.CALL,
        strike=580.0, expiration=date(2026,10,2), multiplier=100, dte=17, bid=6.10, ask=6.30,
        volume=1200, open_interest=4500, oi_reporting_date=date(2026,9,14),
        delta=0.42, gamma=0.03, theta=-0.12, vega=0.18, iv=0.22,
        quote_time=datetime(2026,9,15,16,tzinfo=timezone.utc),
        greeks_time=datetime(2026,9,15,16,tzinfo=timezone.utc),
        provenance=synthetic_provenance("SPY261002C00580000"))
    base.update(kwargs)
    return OptionContract(**base)

def make_gamma(**kwargs):
    base = dict(vendor="SYNTHETIC_VENDOR", methodology="fixture-gex-v1", underlying="SPY",
        expiry_coverage="2026-09-25", model_as_of=datetime(2026,9,15,16,tzinfo=timezone.utc),
        units="usd_gamma", sign_convention="dealer_positive_long_gamma", spot_reference=582.0,
        net_gex=-1.2e8, flip=575.0, call_wall=600.0, put_wall=560.0, regime=GammaRegime.NEGATIVE,
        printable=True, provenance=synthetic_provenance("SPY-GEX"))
    base.update(kwargs)
    return GammaSnapshot(**base)

def make_features(**kwargs):
    base = dict(symbol="SPY", as_of=datetime(2026,9,15,16,tzinfo=timezone.utc), bar_interval="1d",
        close=582.0, ema50=570.0, trend="ABOVE_EMA50", momentum_level=0.04, momentum_change=0.015,
        relative_volume=1.8, relative_strength=0.02, realized_vol=0.16, implied_vol=0.22,
        vah=584.0, val=570.0, poc=578.0)
    base.update(kwargs)
    return FeaturePacket(**base)

def make_market(**kwargs):
    base = dict(symbol="SPY", spot=582.0, spot_time=datetime(2026,9,15,16,tzinfo=timezone.utc),
        features=make_features(), gamma=make_gamma(), catalyst_id="FOMC-minutes",
        catalyst_verified=True, catalyst_time=datetime(2026,9,17,18,tzinfo=timezone.utc),
        catalyst_inside_horizon=True, transmission_observed=True, transmission_notes="SPY held overnight high after minutes",
        volume_profile_present=True,
        breadth_present=True, order_flow_present=False, provenance=synthetic_provenance("SPY"))
    base.update(kwargs)
    return MarketSnapshot(**base)

def make_thesis():
    return Thesis(
        trigger="accept above 580",
        expected_response="continuation toward 600",
        because="verified catalyst plus tape expansion",
        invalidated_if="close back below 574",
        alternate_path="failed break -> put path",
        expected_horizon="5-8 sessions",
        why_this_contract="0.42d Friday vs nearby 0.35 / next week",
        target_price=600.0,
        invalidation_price=574.0,
        horizon_sessions=7,
    )
