"""Authoritative Stage 1 configuration. Weights are research parameters, not proven edges."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

from pydantic import BaseModel, Field

RULES_VERSION: Final[str] = "VECTOR-STAGE1-0.1.0"
TRANSFORMATION_VERSION: Final[str] = "vector-features-0.1.0"


class AuthorityConfig(BaseModel):
    research_enabled: bool = True
    paper_execution_enabled: bool = False
    live_execution_enabled: bool = False


DEFAULT_AUTHORITY = AuthorityConfig()


class FreshnessConfig(BaseModel):
    quote_max_age: timedelta = timedelta(minutes=15)
    greeks_max_age: timedelta = timedelta(minutes=15)
    chain_max_age: timedelta = timedelta(minutes=20)
    sage_max_age: timedelta = timedelta(hours=36)
    gex_intraday_max_age: timedelta = timedelta(hours=6)
    open_interest_report_lag_ok: timedelta = timedelta(hours=36)
    cross_input_tolerance: timedelta = timedelta(minutes=30)


class UniverseConfig(BaseModel):
    min_dte: int = 14
    max_dte: int = 45
    preferred_abs_delta_low: float = 0.35
    preferred_abs_delta_high: float = 0.50
    min_open_interest: int = 100
    spread_veto_pct_of_mid: float = 0.15
    spread_strong_pct: float = 0.05
    spread_acceptable_pct: float = 0.10
    require_end_of_week: bool = True
    standard_multiplier: int = 100
    exclude_adjusted_contracts: bool = True
    exclude_zero_bid: bool = True
    exclude_zero_mid: bool = True


class FeatureConfig(BaseModel):
    bar_interval: str = "1d"
    trend_lookback: int = 50
    momentum_lookback: int = 10
    momentum_change_lookback: int = 5
    relative_volume_lookback: int = 20
    rs_lookback: int = 20
    realized_vol_lookback: int = 20
    min_history: int = 21
    sweep_reclaim_bars: int = 2
    run_hold_bars: int = 2
    breakout_buffer_pct: float = 0.0015


class ScoringThresholds(BaseModel):
    a_plus: float = 90.0
    a: float = 82.0
    b_developing: float = 72.0
    watch: float = 62.0


class ScenarioConfig(BaseModel):
    spot_moves: tuple[float, ...] = (-0.08, -0.04, -0.02, 0.0, 0.02, 0.04, 0.08)
    days_elapsed: tuple[int, ...] = (0, 3, 7, 14)
    iv_moves: tuple[float, ...] = (-0.20, 0.0, 0.20)
    slippage_pct_of_mid: float = 0.50
    commission_per_contract: float = 0.65


class Settings(BaseModel):
    authority: AuthorityConfig = Field(default_factory=AuthorityConfig)
    freshness: FreshnessConfig = Field(default_factory=FreshnessConfig)
    universe: UniverseConfig = Field(default_factory=UniverseConfig)
    features: FeatureConfig = Field(default_factory=FeatureConfig)
    grades: ScoringThresholds = Field(default_factory=ScoringThresholds)
    scenarios: ScenarioConfig = Field(default_factory=ScenarioConfig)
    rules_version: str = RULES_VERSION
    transformation_version: str = TRANSFORMATION_VERSION


DEFAULT_SETTINGS = Settings()

DTE_FACTOR_WEIGHTS: Final[dict[str, dict[str, int]]] = {
    "14-21": {"gamma": 22, "momentum": 20, "catalyst": 18, "flow": 12, "macro": 8, "contract": 15, "risk": 5},
    "22-35": {"gamma": 18, "momentum": 17, "catalyst": 15, "flow": 12, "macro": 16, "contract": 17, "risk": 5},
    "36-45": {"gamma": 14, "momentum": 13, "catalyst": 13, "flow": 10, "macro": 25, "contract": 20, "risk": 5},
}

SUBFACTOR_SHARES: Final[dict[str, dict[str, float]]] = {
    "gamma": {"gex_sign_and_regime": 8 / 22, "flip_location": 7 / 22, "walls_and_runway": 7 / 22},
    "momentum": {"price_structure": 7 / 20, "momentum_level": 5 / 20, "momentum_change": 4 / 20, "relative_volume": 4 / 20},
    "catalyst": {"verified_catalyst": 10 / 18, "timing_fit": 8 / 18},
    "flow": {"volume_profile": 5 / 12, "breadth_or_rs": 4 / 12, "order_flow": 3 / 12},
    "macro": {"sage_confirmation": 3 / 8, "observed_transmission": 5 / 8},
    "contract": {"liquidity_spread": 5 / 15, "delta_fit": 3 / 15, "scenario_economics": 5 / 15, "nearby_comparison": 2 / 15},
    "risk": {"invalidation_quality": 3 / 5, "target_distance": 2 / 5},
}

US_EQUITY_HOLIDAYS_2025_2027: Final[frozenset[str]] = frozenset(
    {
        "2025-01-01", "2025-01-20", "2025-02-17", "2025-04-18", "2025-05-26",
        "2025-06-19", "2025-07-04", "2025-09-01", "2025-11-27", "2025-12-25",
        "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
        "2026-06-19", "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25",
        "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31",
        "2027-06-18", "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24",
    }
)
