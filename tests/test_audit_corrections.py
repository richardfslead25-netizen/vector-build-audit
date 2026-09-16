from datetime import date, datetime, timezone

from tests.helpers import make_contract, make_gamma, make_market, make_thesis
from vector.contracts.enums import Direction, GammaVariant, OperatingMode, SageStatus
from vector.eligibility.gates import evaluate_eligibility
from vector.eligibility.identity import parse_occ_symbol
from vector.pipeline import evaluate_candidate
from vector.sage.adapter import SageReadOnlyAdapter
from vector.scoring.engine import ScoreInputs, score_candidate
from vector.scoring.scenarios import estimate_scenarios, scenarios_available

NOW = datetime(2026, 9, 15, 16, 5, tzinfo=timezone.utc)
LISTED = {date(2026, 10, 2), date(2026, 10, 9)}


def test_forged_established_is_invalid():
    ctx = SageReadOnlyAdapter().ingest({"established": True, "regime": "risk-on"}, now=NOW)
    assert ctx.status is SageStatus.INVALID
    assert ctx.operating_mode is OperatingMode.BEHAVIOR_ONLY


def test_unknown_source_is_invalid():
    ctx = SageReadOnlyAdapter().ingest({
        "established": True,
        "regime": "risk-on",
        "source_identity": "RANDOM-MODEL",
        "schema_version": "x",
        "cutoff": "2026-09-15T12:00:00+00:00",
        "receipt_time": "2026-09-15T12:05:00+00:00",
        "freeze_identity": "f",
        "posterior": {"risk-on": 1.0},
    }, now=NOW)
    assert ctx.status is SageStatus.INVALID


def test_future_cutoff_rejected():
    ctx = SageReadOnlyAdapter().ingest({
        "established": True,
        "regime": "risk-on",
        "source_identity": "SAGE",
        "schema_version": "x",
        "cutoff": "2026-09-20T12:00:00+00:00",
        "receipt_time": "2026-09-15T12:05:00+00:00",
        "freeze_identity": "f",
        "posterior": {"risk-on": 1.0},
    }, now=NOW)
    assert ctx.status is SageStatus.INVALID
    assert "future" in ctx.reason


def test_malformed_posterior_rejected():
    ctx = SageReadOnlyAdapter().ingest({
        "established": True,
        "regime": "risk-on",
        "source_identity": "SAGE",
        "schema_version": "x",
        "cutoff": "2026-09-15T12:00:00+00:00",
        "receipt_time": "2026-09-15T12:05:00+00:00",
        "freeze_identity": "f",
        "posterior": {"risk-on": 0.61},
    }, now=NOW)
    assert ctx.status is SageStatus.INVALID
    assert "posterior" in ctx.reason


def test_no_regime_name_inference():
    ctx = SageReadOnlyAdapter().ingest({
        "established": True,
        "regime": "bull-expansion",
        "source_identity": "SAGE",
        "schema_version": "x",
        "cutoff": "2026-09-15T12:00:00+00:00",
        "receipt_time": "2026-09-15T12:05:00+00:00",
        "freeze_identity": "f",
        "posterior": {"bull-expansion": 1.0},
    }, now=NOW)
    assert ctx.alignment.value == "INSUFFICIENT"
    assert ctx.operating_mode is OperatingMode.BEHAVIOR_ONLY


def test_missing_and_future_quote_times_veto():
    assert "MISSING_QUOTE_TIME" in evaluate_eligibility(
        make_contract(quote_time=None), now=NOW, listed_expirations=LISTED
    )
    future = datetime(2026, 9, 16, 16, tzinfo=timezone.utc)
    assert "FUTURE_QUOTE_TIMESTAMP" in evaluate_eligibility(
        make_contract(quote_time=future, greeks_time=future), now=NOW, listed_expirations=LISTED
    )


def test_naive_timestamp_veto():
    naive = datetime(2026, 9, 15, 16)
    vetoes = evaluate_eligibility(
        make_contract(quote_time=naive, greeks_time=naive), now=NOW, listed_expirations=LISTED
    )
    assert "NAIVE_QUOTE_TIMESTAMP" in vetoes


def test_negative_quote_and_dte_mismatch():
    assert "MALFORMED_QUOTES" in evaluate_eligibility(
        make_contract(bid=-1.0, ask=1.2), now=NOW, listed_expirations=LISTED
    )
    assert "DTE_MISMATCH" in evaluate_eligibility(
        make_contract(dte=21), now=NOW, listed_expirations=LISTED
    )


def test_occ_identity_parses_right_strike_expiry():
    parsed = parse_occ_symbol("SPY260925C00580000")
    assert parsed["underlying"] == "SPY"
    assert parsed["expiration"] == date(2026, 9, 25)
    assert parsed["strike"] == 580.0
    vetoes = evaluate_eligibility(
        make_contract(underlying="SPY", occ_symbol="SPY261002P00580000"),
        now=NOW,
        listed_expirations=LISTED,
    )
    assert "CONTRACT_RIGHT_MISMATCH" in vetoes


def test_listings_required():
    assert "LISTINGS_UNAVAILABLE" in evaluate_eligibility(make_contract(), now=NOW, listed_expirations=None)


def test_wrong_way_call_wall_gets_zero_runway():
    market = make_market(gamma=make_gamma(call_wall=560.0, put_wall=600.0))
    scored = score_candidate(ScoreInputs(
        direction=Direction.CALL, dte=18, sage=SageReadOnlyAdapter().ingest(None),
        gamma_variant=GammaVariant.GAMMA_CONFIRMED,
        market=market, contract=make_contract(), thesis=make_thesis(),
        has_nearby_strike=True, has_nearby_expiration=True, scenario_supportive=True, scenario_available=True,
    ))
    assert scored.subfactors["gamma.walls_and_runway"] == 0.0


def test_opposite_rs_gets_zero():
    features = make_market().features.model_copy(update={"relative_strength": -0.03})
    market = make_market()
    market.features = features
    scored = score_candidate(ScoreInputs(
        direction=Direction.CALL, dte=18, sage=SageReadOnlyAdapter().ingest(None),
        gamma_variant=GammaVariant.GAMMA_CONFIRMED, market=market, contract=make_contract(),
        thesis=make_thesis(), has_nearby_strike=True, has_nearby_expiration=True,
        scenario_supportive=True, scenario_available=True,
    ))
    assert scored.subfactors["flow.breadth_or_rs"] == 0.0


def test_missing_greeks_make_scenarios_unavailable():
    c = make_contract(delta=None)
    assert scenarios_available(c, 582.0) is False
    assert estimate_scenarios(c, 582.0) == []


def test_pipeline_blocks_promotion_without_geometry_and_comparisons():
    packet = evaluate_candidate(
        ticker="SPY",
        direction=Direction.CALL,
        setup="incomplete",
        market=make_market(),
        contract=make_contract(),
        alternatives=[],
        thesis=make_thesis().model_copy(update={"target_price": None, "invalidation_price": None, "horizon_sessions": None}),
        sage_payload=None,
        listed_expirations=LISTED,
        cutoff=NOW,
    )
    assert "THESIS_GEOMETRY_INCOMPLETE" in packet.vetoes
    assert "MISSING_NEARBY_STRIKE" in packet.vetoes
    assert "MISSING_NEARBY_EXPIRATION" in packet.vetoes
    assert packet.disposition.value == "NO_TRADE"
    assert "stub critique" in packet.red_team.attack
