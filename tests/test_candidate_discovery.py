from datetime import datetime, timedelta, timezone

from tests.helpers import make_contract, make_market, make_thesis
from vector.config import DTE_FACTOR_WEIGHTS, DEFAULT_AUTHORITY, DEFAULT_SETTINGS
from vector.contracts.enums import AlignmentState, Direction, GammaVariant, Grade, OperatingMode, SageStatus
from vector.contracts.sage import SageContext, SageUpstreamFields
from vector.discovery.models import (
    CandidateDiscoveryRecord,
    DiscoveryDirection,
    DiscoveryMechanism,
    DiscoverySourceClass,
    DiscoveryStatus,
    MechanismClaim,
)
from vector.discovery.validate import (
    derive_source_event_id,
    evaluate_discovery,
    official_freeze_admitted,
    sage_relationship_for,
)
from vector.scoring.engine import ScoreInputs, score_candidate


NOW = datetime(2026, 9, 20, 16, tzinfo=timezone.utc)


def _record(**kwargs) -> CandidateDiscoveryRecord:
    published = datetime(2026, 9, 18, 14, tzinfo=timezone.utc)
    retrieved = datetime(2026, 9, 18, 15, tzinfo=timezone.utc)
    note_id = kwargs.get("originating_note_id", "NOTE-VAL-2026-09-18")
    publisher = kwargs.get("publisher", "Desk Research")
    base = dict(
        originating_note_id=note_id,
        source_event_id=derive_source_event_id(note_id, publisher),
        source_url="https://example.test/reprint-a",
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
        vector_inference="Valuation-compression hypothesis on duration-sensitive growth.",
        mechanisms=[
            MechanismClaim(mechanism=DiscoveryMechanism.VALUATION_COMPRESSION, source_stated=True)
        ],
        candidate="NVDA",
        direction=DiscoveryDirection.BEARISH,
        exposure_rationale="Rich multiple and rate-sensitive duration, not merely 'tech'.",
        sage_relationship=AlignmentState.INSUFFICIENT,
        official_freeze_ref=None,
        evidence_still_needed=["independent tape confirmation"],
        suggested_trigger="accept below 170",
        suggested_invalidation="reclaim 180",
        transmission_horizon="2-8 weeks",
        publication_verified=True,
        mechanism_verified=False,
        transmission_observed=False,
        exposure_supported=True,
        synthetic=True,
    )
    base.update(kwargs)
    if "source_event_id" not in kwargs:
        base["source_event_id"] = derive_source_event_id(base["originating_note_id"], base["publisher"])
    return CandidateDiscoveryRecord(**base)


def _admitted_freeze(*, alignment=AlignmentState.CONSISTENT) -> SageContext:
    return SageContext(
        status=SageStatus.ESTABLISHED,
        alignment=alignment,
        operating_mode=OperatingMode.SAGE_INFORMED,
        verified_established=True,
        claimed_established=True,
        reason="synthetic-trust-boundary-fixture",
        upstream=SageUpstreamFields(freeze_identity="freeze-fixture-1"),
    )


def test_verified_publication_unverified_mechanism_not_promoted():
    decision = evaluate_discovery(_record(publication_verified=True, mechanism_verified=False), now=NOW)
    assert decision.promoted is False
    assert decision.status is DiscoveryStatus.UNVERIFIED
    assert "MECHANISM_UNVERIFIED" in decision.vetoes


def test_verified_mechanism_without_transmission_not_promoted():
    decision = evaluate_discovery(
        _record(publication_verified=True, mechanism_verified=True, transmission_observed=False),
        now=NOW,
    )
    assert decision.promoted is False
    assert "TRANSMISSION_UNOBSERVED" in decision.vetoes
    assert decision.status is not DiscoveryStatus.PROMOTED_TO_CATALYST_INTAKE


def test_missing_publication_timestamp_fail_closed():
    decision = evaluate_discovery(_record(published_at=None), now=NOW)
    assert "MISSING_PUBLICATION_TIME" in decision.vetoes
    assert decision.promoted is False


def test_naive_timestamps_fail_closed():
    naive = datetime(2026, 9, 18, 14)
    decision = evaluate_discovery(_record(published_at=naive, retrieved_at=naive), now=NOW)
    assert "NAIVE_PUBLICATION_TIMESTAMP" in decision.vetoes
    assert "NAIVE_RETRIEVAL_TIMESTAMP" in decision.vetoes
    assert decision.promoted is False


def test_retrieval_before_publication_fail_closed():
    published = datetime(2026, 9, 18, 16, tzinfo=timezone.utc)
    retrieved = datetime(2026, 9, 18, 15, tzinfo=timezone.utc)
    decision = evaluate_discovery(_record(published_at=published, retrieved_at=retrieved), now=NOW)
    assert "RETRIEVAL_BEFORE_PUBLICATION" in decision.vetoes
    assert decision.promoted is False


def test_missing_forecast_horizon_unpromoted():
    decision = evaluate_discovery(_record(forecast_horizon=None, new_estimate="4500"), now=NOW)
    assert "MISSING_FORECAST_HORIZON" in decision.vetoes
    assert decision.promoted is False


def test_unsupported_exposure_unpromoted():
    decision = evaluate_discovery(_record(exposure_supported=False, exposure_rationale=""), now=NOW)
    assert "UNSUPPORTED_EXPOSURE" in decision.vetoes
    assert decision.promoted is False


def test_stale_commentary_unpromoted():
    old = datetime(2026, 8, 1, 14, tzinfo=timezone.utc)
    decision = evaluate_discovery(_record(published_at=old, retrieved_at=old + timedelta(hours=1)), now=NOW)
    assert "STALE_COMMENTARY" in decision.vetoes
    assert decision.promoted is False
    assert decision.status is DiscoveryStatus.WATCH


def test_withdrawn_retains_original_and_points_to_correction():
    original = _record(status=DiscoveryStatus.WITHDRAWN)
    correction = _record(
        originating_note_id="NOTE-VAL-2026-09-19-CORRECTION",
        correction_of=original.source_event_id,
        status=DiscoveryStatus.CAPTURED,
        stated_rationale="Prior target cut withdrawn.",
    )
    original_decision = evaluate_discovery(original, now=NOW)
    assert original.status is DiscoveryStatus.WITHDRAWN
    assert original_decision.status is DiscoveryStatus.WITHDRAWN
    assert original_decision.promoted is False
    assert correction.correction_of == original.source_event_id
    assert correction.source_event_id != original.source_event_id


def test_three_syndicated_copies_share_source_event_id():
    note = "GS-TARGET-CUT-2026-09-18"
    publisher = "Goldman Strategist"
    copies = [
        _record(originating_note_id=note, publisher=publisher, source_url=f"https://wire.test/{i}")
        for i in ("bloomberg", "reuters", "cnbc")
    ]
    ids = {row.source_event_id for row in copies}
    assert len(ids) == 1
    assert copies[0].source_event_id == derive_source_event_id(note, publisher)


def test_no_sage_freeze_relationship_insufficient():
    none = SageContext(
        status=SageStatus.UNAVAILABLE,
        alignment=AlignmentState.INSUFFICIENT,
        operating_mode=OperatingMode.BEHAVIOR_ONLY,
    )
    decision = evaluate_discovery(_record(), now=NOW, sage=none)
    assert sage_relationship_for(none) is AlignmentState.INSUFFICIENT
    assert decision.sage_relationship is AlignmentState.INSUFFICIENT
    assert decision.official_freeze_ref is None


def test_incomplete_established_claim_without_freeze_is_insufficient():
    forged = SageContext(
        status=SageStatus.ESTABLISHED,
        alignment=AlignmentState.CONSISTENT,
        operating_mode=OperatingMode.SAGE_INFORMED,
        verified_established=True,
        claimed_established=True,
        reason="missing-freeze-identity",
        upstream=SageUpstreamFields(freeze_identity=None),
    )
    assert official_freeze_admitted(forged) is False
    assert sage_relationship_for(forged) is AlignmentState.INSUFFICIENT
    decision = evaluate_discovery(_record(), now=NOW, sage=forged)
    assert decision.sage_relationship is AlignmentState.INSUFFICIENT
    assert decision.official_freeze_ref is None


def test_established_without_sage_informed_is_insufficient():
    forged = SageContext(
        status=SageStatus.ESTABLISHED,
        alignment=AlignmentState.CONSISTENT,
        operating_mode=OperatingMode.BEHAVIOR_ONLY,
        verified_established=True,
        upstream=SageUpstreamFields(freeze_identity="freeze-fixture-1"),
    )
    assert official_freeze_admitted(forged) is False
    assert sage_relationship_for(forged) is AlignmentState.INSUFFICIENT


def test_no_sage_freeze_confirmation_points_zero():
    scored = score_candidate(ScoreInputs(
        direction=Direction.CALL,
        dte=18,
        sage=SageContext(
            status=SageStatus.UNAVAILABLE,
            alignment=AlignmentState.INSUFFICIENT,
            operating_mode=OperatingMode.BEHAVIOR_ONLY,
        ),
        gamma_variant=GammaVariant.GAMMA_UNAVAILABLE,
        market=make_market(),
        contract=make_contract(),
        thesis=make_thesis(),
        has_nearby_strike=True,
        has_nearby_expiration=True,
        scenario_supportive=True,
        scenario_available=True,
    ))
    assert scored.subfactors["macro.sage_confirmation"] == 0.0


def test_commentary_macro_tokens_cannot_mint_regime():
    record = _record(
        stated_rationale="This looks consistent with QT-T valuation compression.",
        mentions_macro_tokens=True,
        official_freeze_ref="invented-freeze",
    )
    decision = evaluate_discovery(record, now=NOW, sage=None)
    assert decision.sage_relationship is AlignmentState.INSUFFICIENT
    assert decision.official_freeze_ref is None
    assert decision.promoted is False


def test_macro_token_does_not_block_comparison_to_admitted_freeze():
    record = _record(
        stated_rationale="This looks consistent with QT-T valuation compression.",
        mentions_macro_tokens=True,
        publication_verified=True,
        mechanism_verified=True,
        transmission_observed=True,
        exposure_supported=True,
    )
    freeze = _admitted_freeze(alignment=AlignmentState.CONSISTENT)
    decision = evaluate_discovery(record, now=NOW, sage=freeze)
    assert official_freeze_admitted(freeze) is True
    assert decision.sage_relationship is AlignmentState.CONSISTENT
    assert decision.official_freeze_ref == "freeze-fixture-1"
    assert "COMMENTARY_CANNOT_MINT_SAGE" not in decision.vetoes


def test_discovery_watch_is_not_scoring_grade_watch():
    decision = evaluate_discovery(
        _record(publication_verified=True, mechanism_verified=True, transmission_observed=False),
        now=NOW,
    )
    assert decision.status is DiscoveryStatus.WATCH
    assert decision.status is not Grade.WATCH
    assert not isinstance(decision.status, type(Grade.WATCH))


def test_chain_or_gex_flags_do_not_fabricate_market_evidence():
    decision = evaluate_discovery(_record(chain_available=True, gex_available=True), now=NOW)
    assert "MARKET_EVIDENCE_NOT_IN_DISCOVERY_SLICE" in decision.vetoes
    assert decision.promoted is False


def test_scoring_weights_unchanged():
    assert DTE_FACTOR_WEIGHTS["14-21"]["gamma"] == 22
    assert DTE_FACTOR_WEIGHTS["22-35"]["macro"] == 16
    assert DTE_FACTOR_WEIGHTS["36-45"]["contract"] == 20
    assert DEFAULT_SETTINGS.grades.watch == 62.0
    assert DEFAULT_AUTHORITY.live_execution_enabled is False
    assert DEFAULT_AUTHORITY.paper_execution_enabled is False


def test_full_independent_validation_can_promote():
    decision = evaluate_discovery(
        _record(
            publication_verified=True,
            mechanism_verified=True,
            transmission_observed=True,
            exposure_supported=True,
        ),
        now=NOW,
    )
    assert decision.promoted is True
    assert decision.status is DiscoveryStatus.PROMOTED_TO_CATALYST_INTAKE
