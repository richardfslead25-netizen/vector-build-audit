from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field
from vector.config import DEFAULT_AUTHORITY, RULES_VERSION, AuthorityConfig
from vector.contracts.enums import (
    AlignmentState, Direction, Disposition, DteBand, GammaVariant,
    Grade, OperatingMode, RedTeamVerdict,
)
from vector.contracts.options import OptionContract, ScenarioResult
from vector.contracts.sage import SageContext

class Thesis(BaseModel):
    trigger: str
    expected_response: str
    because: str
    invalidated_if: str
    alternate_path: str
    expected_horizon: str
    why_this_contract: str
    original_text: str | None = None
    target_price: float | None = None
    invalidation_price: float | None = None
    horizon_sessions: int | None = None

class ScoreBreakdown(BaseModel):
    dte_band: DteBand
    factor_maxima: dict[str, int]
    subfactors: dict[str, float]
    factor_totals: dict[str, float]
    missing_subfactors: list[str] = Field(default_factory=list)
    raw_score: float
    grade: Grade
    reweighted: bool = False

class RedTeamRecord(BaseModel):
    verdict: RedTeamVerdict
    attack: str
    survives: str
    fails: str
    reverse_kill_if: str = ""
    original_thesis_preserved: bool = True
    score_changed: bool = False

class ResearchPacket(BaseModel):
    run_id: str
    cutoff: datetime
    generated_at: datetime
    rules_version: str = RULES_VERSION
    operating_mode: OperatingMode
    gamma_variant: GammaVariant
    sage: SageContext
    alignment: AlignmentState
    ticker: str
    direction: Direction
    setup: str
    thesis: Thesis
    contract: OptionContract | None = None
    alternatives: list[OptionContract] = Field(default_factory=list)
    scenarios: list[ScenarioResult] = Field(default_factory=list)
    score: ScoreBreakdown | None = None
    vetoes: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    disposition: Disposition
    red_team: RedTeamRecord | None = None
    authority: AuthorityConfig = Field(default_factory=lambda: DEFAULT_AUTHORITY.model_copy())
    notes: list[str] = Field(default_factory=list)

    def to_board_row(self) -> dict[str, Any]:
        c = self.contract
        return {
            "ticker": self.ticker,
            "direction": self.direction.value,
            "mode": self.operating_mode.value,
            "gamma_variant": self.gamma_variant.value,
            "sage_status": self.sage.status.value,
            "score": None if self.score is None else self.score.raw_score,
            "grade": None if self.score is None else self.score.grade.value,
            "disposition": self.disposition.value,
            "vetoes": list(self.vetoes),
            "expiry": None if c is None else c.expiration.isoformat(),
            "strike": None if c is None else c.strike,
            "dte": None if c is None else c.dte,
            "delta": None if c is None else c.delta,
            "spread_pct": None if c is None else c.spread_pct,
            "execution_authority": self.authority.model_dump(),
        }
