"""Discovery → G1 catalyst-intake handoff. Nomination only. Zero points."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from vector.config import DEFAULT_AUTHORITY
from vector.contracts.enums import AlignmentState
from vector.discovery.models import (
    CandidateDiscoveryRecord,
    DiscoveryDirection,
    DiscoverySourceClass,
    DiscoveryStatus,
    MechanismClaim,
)
from vector.discovery.validate import evaluate_discovery, official_freeze_admitted


class G1HandoffNomination(BaseModel):
    """Read-only nomination into existing G1. Not a score. Not a contract."""

    model_config = ConfigDict(frozen=True)

    source_event_id: str
    originating_note_id: str
    source_url: str
    document_identity: str
    author: str
    publisher: str
    source_class: DiscoverySourceClass
    published_at: datetime | None
    retrieved_at: datetime | None
    forecast_horizon: str | None
    stated_rationale: str
    vector_inference: str
    mechanisms: tuple[MechanismClaim, ...]
    candidate: str
    direction: DiscoveryDirection
    exposure_rationale: str
    contradiction: str
    evidence_still_needed: tuple[str, ...]
    suggested_trigger: str
    suggested_invalidation: str
    transmission_horizon: str | None
    sage_relationship: AlignmentState
    official_freeze_ref: str | None
    discovery_status: DiscoveryStatus
    catalyst_verified: bool = False
    score_points: float = 0.0
    contract: None = None
    gex: None = None
    strike: None = None
    expiration: None = None
    delta: None = None
    sage_informed_enabled: bool = False
    paper_execution_enabled: bool = False
    live_execution_enabled: bool = False
    notes: tuple[str, ...] = Field(default_factory=tuple)


@dataclass(frozen=True)
class HandoffDecision:
    accepted: bool
    vetoes: tuple[str, ...]
    nomination: G1HandoffNomination | None


_BLOCKED_STATUSES = frozenset(
    {
        DiscoveryStatus.CAPTURED,
        DiscoveryStatus.WATCH,
        DiscoveryStatus.UNVERIFIED,
        DiscoveryStatus.REJECT,
        DiscoveryStatus.NO_SETUP,
        DiscoveryStatus.SUPERSEDED,
        DiscoveryStatus.WITHDRAWN,
    }
)


def handoff_to_g1(
    record: CandidateDiscoveryRecord,
    *,
    now: datetime,
    sage=None,
) -> HandoffDecision:
    """Permit G1 investigation only after independent discovery promotion."""
    vetoes: list[str] = []
    if record.status in _BLOCKED_STATUSES:
        vetoes.append(f"STATUS_{record.status.value}")

    decision = evaluate_discovery(record, now=now, sage=sage)
    if not decision.promoted:
        vetoes.append("DISCOVERY_NOT_INDEPENDENTLY_PROMOTED")
    if decision.status is not DiscoveryStatus.PROMOTED_TO_CATALYST_INTAKE:
        vetoes.append(f"EVALUATED_STATUS_{decision.status.value}")

    if vetoes:
        return HandoffDecision(accepted=False, vetoes=tuple(dict.fromkeys(vetoes)), nomination=None)

    sage_rel = decision.sage_relationship
    freeze_ref = decision.official_freeze_ref if official_freeze_admitted(sage) else None

    nomination = G1HandoffNomination(
        source_event_id=record.source_event_id,
        originating_note_id=record.originating_note_id,
        source_url=record.source_url,
        document_identity=record.document_identity,
        author=record.author,
        publisher=record.publisher,
        source_class=record.source_class,
        published_at=record.published_at,
        retrieved_at=record.retrieved_at,
        forecast_horizon=record.forecast_horizon,
        stated_rationale=record.stated_rationale,
        vector_inference=record.vector_inference,
        mechanisms=tuple(record.mechanisms),
        candidate=record.candidate,
        direction=record.direction,
        exposure_rationale=record.exposure_rationale,
        contradiction=record.contradiction,
        evidence_still_needed=tuple(record.evidence_still_needed),
        suggested_trigger=record.suggested_trigger,
        suggested_invalidation=record.suggested_invalidation,
        transmission_horizon=record.transmission_horizon,
        sage_relationship=sage_rel,
        official_freeze_ref=freeze_ref,
        discovery_status=DiscoveryStatus.PROMOTED_TO_CATALYST_INTAKE,
        catalyst_verified=False,
        score_points=0.0,
        contract=None,
        gex=None,
        strike=None,
        expiration=None,
        delta=None,
        sage_informed_enabled=False,
        paper_execution_enabled=DEFAULT_AUTHORITY.paper_execution_enabled,
        live_execution_enabled=DEFAULT_AUTHORITY.live_execution_enabled,
        notes=(
            "discovery promoted ≠ catalyst verified",
            "handoff awards 0 points",
            "no contract or GEX fabricated",
        ),
    )
    return HandoffDecision(accepted=True, vetoes=(), nomination=nomination)
