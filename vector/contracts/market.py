from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field
from vector.contracts.enums import GammaRegime, SweepRun
from vector.contracts.provenance import Provenance

class Bar(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    provenance: Provenance

class GammaSnapshot(BaseModel):
    vendor: str
    methodology: str
    underlying: str
    expiry_coverage: str
    model_as_of: datetime | None
    units: str
    sign_convention: str
    spot_reference: float | None
    net_gex: float | None = None
    flip: float | None = None
    call_wall: float | None = None
    put_wall: float | None = None
    hvl: float | None = None
    regime: GammaRegime = GammaRegime.GEX_NOT_PRINTABLE
    printable: bool = False
    provenance: Provenance | None = None
    notes: str = ""

class FeaturePacket(BaseModel):
    symbol: str
    as_of: datetime | None
    bar_interval: str
    lookbacks: dict[str, int] = Field(default_factory=dict)
    close: float | None = None
    ema50: float | None = None
    trend: str | None = None
    momentum_level: float | None = None
    momentum_change: float | None = None
    relative_volume: float | None = None
    relative_strength: float | None = None
    realized_vol: float | None = None
    implied_vol: float | None = None
    vah: float | None = None
    val: float | None = None
    poc: float | None = None
    sweep_or_run: SweepRun = SweepRun.UNCLASSIFIED
    structure: str | None = None
    missing: list[str] = Field(default_factory=list)
    formulas: dict[str, str] = Field(default_factory=dict)

class MarketSnapshot(BaseModel):
    symbol: str
    spot: float | None
    spot_time: datetime | None
    bars: list[Bar] = Field(default_factory=list)
    benchmark_bars: list[Bar] = Field(default_factory=list)
    features: FeaturePacket | None = None
    gamma: GammaSnapshot | None = None
    catalyst_id: str | None = None
    catalyst_verified: bool = False
    catalyst_time: datetime | None = None
    catalyst_inside_horizon: bool = False
    transmission_observed: bool = False
    transmission_notes: str = ""
    order_flow_present: bool = False
    volume_profile_present: bool = False
    breadth_present: bool = False
    provenance: Provenance | None = None
