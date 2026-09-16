
from datetime import datetime, timezone
import pytest
from vector.contracts.enums import AlignmentState, OperatingMode, SageStatus
from vector.sage.adapter import SageReadOnlyAdapter, SageWriteError

def test_null_sage_plus_strong_tape_is_behavior_only():
    ctx = SageReadOnlyAdapter().ingest(None)
    assert ctx.status is SageStatus.UNAVAILABLE
    assert ctx.operating_mode is OperatingMode.BEHAVIOR_ONLY
    assert ctx.alignment is AlignmentState.INSUFFICIENT
    assert ctx.as_public_dict()["officialFreezeCount"] is None

def test_unavailable_does_not_invent_freeze_count():
    ctx = SageReadOnlyAdapter().ingest({"status_text":"UNAVAILABLE","source_identity":"SAGE"})
    assert ctx.status is SageStatus.UNAVAILABLE
    assert ctx.freeze_count_invented is False
    assert ctx.as_public_dict()["officialFreezeCount"] is None

def test_not_established_preserves_supplied_count_only():
    ctx = SageReadOnlyAdapter().ingest({"status_text":"NOT_ESTABLISHED","established":False,"source_identity":"SAGE","official_freeze_count":0})
    assert ctx.status is SageStatus.NOT_ESTABLISHED
    assert ctx.as_public_dict()["officialFreezeCount"] == 0

def test_stale_established_payload_is_stale_not_informed():
    ctx = SageReadOnlyAdapter().ingest({
        "established": True,
        "regime": "risk-on",
        "source_identity": "SAGE",
        "schema_version": "sage-unagreed-placeholder",
        "cutoff": "2026-01-01T00:00:00+00:00",
        "receipt_time": "2026-01-01T00:05:00+00:00",
        "freeze_identity": "old-freeze",
        "posterior": {"risk-on": 1.0},
        "official_freeze_count": 4,
    }, now=datetime(2026, 9, 15, tzinfo=timezone.utc))
    assert ctx.status is SageStatus.STALE
    assert ctx.operating_mode is OperatingMode.BEHAVIOR_ONLY

def test_invalid_payload():
    ctx = SageReadOnlyAdapter().ingest({"cutoff":"not-a-date","established":True,"regime":"x"})
    assert ctx.status is SageStatus.INVALID

def test_sigil_does_not_confer_sage_confirmation():
    ctx = SageReadOnlyAdapter().ingest({"source_identity":"SIGIL","legacy_sigil":True,"regime":"risk-on","established":True})
    assert ctx.status is SageStatus.UNAVAILABLE
    assert "SIGIL" in ctx.reason

def test_complete_established_does_not_admit_sage_informed_in_production():
    ctx = SageReadOnlyAdapter().ingest({
        "established": True,
        "regime": "risk-on-expansion",
        "source_identity": "SAGE",
        "schema_version": "sage-unagreed-placeholder",
        "cutoff": "2026-09-15T12:00:00+00:00",
        "receipt_time": "2026-09-15T12:05:00+00:00",
        "official_freeze_count": 1,
        "posterior": {"risk-on-expansion": 1.0},
        "persistence": {"value": 0.4},
        "successors": ["tightening"],
        "transition_stage": "stable",
        "freeze_identity": "freeze-abc",
    }, now=datetime(2026, 9, 15, 16, tzinfo=timezone.utc))
    assert ctx.status is SageStatus.NOT_ESTABLISHED
    assert ctx.claimed_established is True
    assert ctx.verified_established is False
    assert ctx.operating_mode is OperatingMode.BEHAVIOR_ONLY
    assert ctx.alignment is AlignmentState.INSUFFICIENT
    assert ctx.as_public_dict()["CURRENT_REGIME"] is None
    assert ctx.as_public_dict()["POSTERIOR"] is None
    assert "unverified" in ctx.reason or "admission closed" in ctx.reason

def test_no_write_capability():
    adapter = SageReadOnlyAdapter()
    with pytest.raises(SageWriteError):
        adapter.write({"regime":"risk-on"})
    with pytest.raises(SageWriteError):
        adapter.update_posterior({})
    with pytest.raises(SageWriteError):
        adapter.mint_regime("x")
    assert adapter.WRITE_FORBIDDEN is True
