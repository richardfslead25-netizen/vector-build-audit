"""Typed discovery record. Commentary nominates; VECTOR validates."""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum

from pydantic import BaseModel, Field

from vector.contracts.enums import AlignmentState, Grade


class DiscoverySourceClass(str, Enum):
    PRIMARY_RESEARCH = "PRIMARY_RESEARCH"
    COMPANY_GUIDANCE = "COMPANY_GUIDANCE"
    PRIMARY_NEWS = "PRIMARY_NEWS"
    SECONDARY_REPORTING = "SECONDARY_REPORTING"
    UNVERIFIED_CLAIM = "UNVERIFIED_CLAIM"


class DiscoveryDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NO_SETUP = "NO_SETUP"


class DiscoveryMechanism(str, Enum):
    VALUATION_COMPRESSION = "VALUATION_COMPRESSION"
    VALUATION_EXPANSION = "VALUATION_EXPANSION"
    EARNINGS_REVISION = "EARNINGS_REVISION"
    CREDIT_REFINANCING = "CREDIT_REFINANCING"
    DEMAND_CHANGE = "DEMAND_CHANGE"
    INPUT_COST_SUPPLY = "INPUT_COST_SUPPLY"
    POLICY_CATALYST = "POLICY_CATALYST"
    COMPANY_SPECIFIC = "COMPANY_SPECIFIC"


class DiscoveryStatus(str, Enum):
    CAPTURED = "CAPTURED"
    WATCH = "WATCH"
    UNVERIFIED = "UNVERIFIED"
    PROMOTED_TO_CATALYST_INTAKE = "PROMOTED_TO_CATALYST_INTAKE"
    REJECT = "REJECT"
    NO_SETUP = "NO_SETUP"
    SUPERSEDED = "SUPERSEDED"
    WITHDRAWN = "WITHDRAWN"


class MechanismClaim(BaseModel):
    mechanism: DiscoveryMechanism
    source_stated: bool = False
    vector_inferred: bool = False


class CandidateDiscoveryRecord(BaseModel):
    source_event_id: str
    originating_note_id: str
    source_url: str
    document_identity: str
    author: str
    publisher: str
    source_class: DiscoverySourceClass
    published_at: datetime | None = None
    retrieved_at: datetime | None = None
    forecast_horizon: str | None = None
    prior_estimate: str | None = None
    new_estimate: str | None = None
    estimate_units: str | None = None
    stated_rationale: str
    vector_inference: str = ""
    mechanisms: list[MechanismClaim] = Field(default_factory=list)
    candidate: str
    direction: DiscoveryDirection
    exposure_rationale: str
    contradiction: str = ""
    sage_relationship: AlignmentState = AlignmentState.INSUFFICIENT
    official_freeze_ref: str | None = None
    evidence_still_needed: list[str] = Field(default_factory=list)
    suggested_trigger: str = ""
    suggested_invalidation: str = ""
    transmission_horizon: str | None = None
    holding_horizon: str | None = None
    contract_expiry: str | None = None
    dte: int | None = None
    status: DiscoveryStatus = DiscoveryStatus.CAPTURED
    supersedes: str | None = None
    correction_of: str | None = None
    publication_verified: bool = False
    mechanism_verified: bool = False
    transmission_observed: bool = False
    exposure_supported: bool = False
    chain_available: bool = False
    gex_available: bool = False
    mentions_macro_tokens: bool = False
    synthetic: bool = True

    def is_forecast(self) -> bool:
        return any(
            value not in (None, "", "UNAVAILABLE")
            for value in (self.prior_estimate, self.new_estimate, self.forecast_horizon)
        ) or self.source_class in {
            DiscoverySourceClass.PRIMARY_RESEARCH,
            DiscoverySourceClass.COMPANY_GUIDANCE,
        }


SCORING_WATCH_GRADE = Grade.WATCH
COMMENTARY_STALE_AFTER = timedelta(days=14)
REGIME_TOKENS = ("OS-H", "QT-T", "CR-D", "OS-L", "RF-L", "FS-D1", "AI-I")
