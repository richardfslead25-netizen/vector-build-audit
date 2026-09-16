from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator, model_validator
from vector.contracts.enums import OptionRight, QuoteQuality
from vector.contracts.provenance import Provenance

class OptionContract(BaseModel):
    underlying: str
    occ_symbol: str
    right: OptionRight
    strike: float
    expiration: date
    multiplier: int = 100
    dte: int
    bid: float | None = None
    ask: float | None = None
    mid: float | None = None
    spread: float | None = None
    spread_pct: float | None = None
    volume: int | None = None
    open_interest: int | None = None
    oi_reporting_date: date | None = None
    delta: float | None = None
    gamma: float | None = None
    theta: float | None = None
    vega: float | None = None
    iv: float | None = None
    quote_time: datetime | None = None
    greeks_time: datetime | None = None
    adjusted: bool = False
    nonstandard_deliverable: bool = False
    quote_quality: QuoteQuality = QuoteQuality.INCOMPLETE
    provenance: Provenance | None = None

    @field_validator("dte")
    @classmethod
    def _dte_nonneg(cls, v: int) -> int:
        if v < 0:
            raise ValueError("DTE cannot be negative")
        return v

    @model_validator(mode="after")
    def _derive_quote_fields(self) -> "OptionContract":
        if self.bid is not None and self.ask is not None:
            mid = (self.bid + self.ask) / 2.0
            object.__setattr__(self, "mid", mid)
            object.__setattr__(self, "spread", self.ask - self.bid)
            if mid != 0:
                object.__setattr__(self, "spread_pct", (self.ask - self.bid) / mid)
        return self

    @property
    def abs_delta(self) -> float | None:
        if self.delta is None:
            return None
        return abs(self.delta)

class ScenarioResult(BaseModel):
    spot_move: float
    days_elapsed: int
    iv_move: float
    estimated_value: float | None
    pnl_per_contract: float | None
    notes: str = ""
