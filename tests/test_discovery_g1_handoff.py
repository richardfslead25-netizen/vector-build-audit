from datetime import datetime, timezone

from vector.config import DTE_FACTOR_WEIGHTS, DEFAULT_AUTHORITY
from vector.contracts.enums import AlignmentState, OperatingMode, SageStatus
from vector.contracts.market import MarketSnapshot
from vector.contracts.sage import SageContext, SageUpstreamFields
from vector.discovery.models import (
    DiscoveryDirection,
    DiscoveryMechanism,
    DiscoverySourceClass,
    DiscoveryStatus,
    MechanismClaim,
    CandidateDiscoveryRecord,
)
from vector.discovery.validate import derive_source_event_id
from vector.discovery.handoff import G1HandoffNomination, handoff_to_g1
from vector.eligibility import identity as occ_identity


NOW = datetime(2026, 9, 20, 16, tzinfo=timezone.utc)


def _record(*, status: DiscoveryStatus, **kwargs) -> CandidateDiscoveryRecord:
    note_id = kwargs.get("originating_note_id", "NOTE-VAL-2026-09-18")
    publisher = kwargs.get("publisher", "Desk Research")
    published = datetime(2026, 9, 18, 14, tzinfo=timezone.utc)
    retrieved = datetime(2026, 9, 18, 15, tzinfo=timezone.utc)
    promoted = status is DiscoveryStatus.PROMOTED_TO_CATALYST_INTAKE
    base = dict(
        originating_note_id=note_id,
        source_event_id=derive_source_event_id(note_id, publisher),
        source_url="https://example.test/note",
        document_identity="desk-note-val-2026-09-18",
        author="Analyst A",
        publisher=publisher,
        source_class=DiscoverySourceClass.PRIMARY_RESEARCH,
        published_at=published,
        retrieved_at=retrieved,
        forecast_horizon="year-end 2026",
        prior_estimate="4800",
        new_estimate="4500",
        estimate_units="index points",
        stated_rationale="Higher yields justify a lower index multiple.",
        vector_inference="Valuation-compression hypothesis.",
        mechanisms=[MechanismClaim(mechanism=DiscoveryMechanism.VALUATION_COMPRESSION, source_stated=True)],
        candidate="NVDA",
        direction=DiscoveryDirection.BEARISH,
        exposure_rationale="Rich multiple, duration-sensitive.",
        contradiction="",
        evidence_still_needed=["independent tape confirmation"],
        suggested_trigger="accept below 170",
        suggested_invalidation="reclaim 180",
        transmission_horizon="2-8 weeks",
        status=status,
        publication_verified=promoted,
        mechanism_verified=promoted,
        transmission_observed=promoted,
        exposure_supported=promoted,
        synthetic=True,
    )
    base.update(kwargs)
    if "source_event_id" not in kwargs:
        base["source_event_id"] = derive_source_event_id(base["originating_note_id"], base["publisher"])
    return CandidateDiscoveryRecord(**base)


def test_promoted_creates_handoff():
    decision = handoff_to_g1(_record(status=DiscoveryStatus.PROMOTED_TO_CATALYST_INTAKE), now=NOW)
    assert decision.accepted is True
    assert isinstance(decision.nomination, G1HandoffNomination)


def test_captured_cannot_handoff():
    assert handoff_to_g1(_record(status=DiscoveryStatus.CAPTURED), now=NOW).accepted is False


def test_watch_cannot_handoff():
    assert handoff_to_g1(_record(status=DiscoveryStatus.WATCH), now=NOW).accepted is False


def test_unverified_cannot_handoff():
    assert handoff_to_g1(_record(status=DiscoveryStatus.UNVERIFIED), now=NOW).accepted is False


def test_reject_cannot_handoff():
    assert handoff_to_g1(_record(status=DiscoveryStatus.REJECT), now=NOW).accepted is False


def test_no_setup_cannot_handoff():
    assert handoff_to_g1(_record(status=DiscoveryStatus.NO_SETUP, direction=DiscoveryDirection.NO_SETUP), now=NOW).accepted is False


def test_superseded_cannot_handoff():
    assert handoff_to_g1(_record(status=DiscoveryStatus.SUPERSEDED), now=NOW).accepted is False


def test_withdrawn_cannot_handoff():
    assert handoff_to_g1(_record(status=DiscoveryStatus.WITHDRAWN), now=NOW).accepted is False


def test_preserves_source_event_id_and_rationales():
    record = _record(status=DiscoveryStatus.PROMOTED_TO_CATALYST_INTAKE)
    nom = handoff_to_g1(record, now=NOW).nomination
    assert nom.source_event_id == record.source_event_id
    assert nom.stated_rationale == record.stated_rationale
    assert nom.vector_inference == record.vector_inference
    assert nom.stated_rationale != nom.vector_inference


def test_promotion_does_not_set_catalyst_verified():
    nom = handoff_to_g1(_record(status=DiscoveryStatus.PROMOTED_TO_CATALYST_INTAKE), now=NOW).nomination
    assert nom.catalyst_verified is False
    snap = MarketSnapshot(symbol="NVDA", spot=None, spot_time=None, catalyst_verified=False)
    assert snap.catalyst_verified is False


def test_handoff_awards_zero_points_and_no_market_fields():
    nom = handoff_to_g1(_record(status=DiscoveryStatus.PROMOTED_TO_CATALYST_INTAKE), now=NOW).nomination
    assert nom.score_points == 0.0
    assert nom.contract is None
    assert nom.gex is None
    assert nom.strike is None
    assert nom.expiration is None
    assert nom.delta is None


def test_unavailable_sage_stays_insufficient():
    sage = SageContext(
        status=SageStatus.UNAVAILABLE,
        alignment=AlignmentState.INSUFFICIENT,
        operating_mode=OperatingMode.BEHAVIOR_ONLY,
    )
    nom = handoff_to_g1(_record(status=DiscoveryStatus.PROMOTED_TO_CATALYST_INTAKE), now=NOW, sage=sage).nomination
    assert nom.sage_relationship is AlignmentState.INSUFFICIENT
    assert nom.official_freeze_ref is None
    assert nom.sage_informed_enabled is False


def test_freeze_reference_does_not_enable_sage_informed():
    sage = SageContext(
        status=SageStatus.ESTABLISHED,
        alignment=AlignmentState.CONSISTENT,
        operating_mode=OperatingMode.SAGE_INFORMED,
        verified_established=True,
        reason="synthetic-provenance-only",
        upstream=SageUpstreamFields(freeze_identity="freeze-fixture-1"),
    )
    nom = handoff_to_g1(_record(status=DiscoveryStatus.PROMOTED_TO_CATALYST_INTAKE), now=NOW, sage=sage).nomination
    assert nom.official_freeze_ref == "freeze-fixture-1"
    assert nom.sage_informed_enabled is False


def test_weights_occ_authority_unchanged():
    assert DTE_FACTOR_WEIGHTS["14-21"]["gamma"] == 22
    assert DTE_FACTOR_WEIGHTS["36-45"]["macro"] == 25
    assert DEFAULT_AUTHORITY.paper_execution_enabled is False
    assert DEFAULT_AUTHORITY.live_execution_enabled is False
    assert occ_identity.OSI_YEAR_MIN == 2000
    assert occ_identity.OSI_YEAR_MAX == 2099


def test_handoff_module_has_no_order_path():
    import vector.discovery.handoff as module
    names = set(dir(module))
    assert not {"submit_order", "place_order", "send_order", "broker"} & names
