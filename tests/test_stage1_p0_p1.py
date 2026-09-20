from datetime import date, datetime, timezone

from tests.helpers import make_contract, make_market, make_thesis
from vector.contracts.enums import AlignmentState, Direction, GammaVariant, OperatingMode, SageStatus
from vector.contracts.sage import SageContext
from vector.pipeline import evaluate_candidate
from vector.scoring.engine import ScoreInputs, score_candidate


NOW = datetime(2026, 9, 15, 16, 5, tzinfo=timezone.utc)
LISTED = {date(2026, 10, 2), date(2026, 10, 9)}


def _score(sage: SageContext):
    return score_candidate(ScoreInputs(
        direction=Direction.CALL,
        dte=18,
        sage=sage,
        gamma_variant=GammaVariant.GAMMA_CONFIRMED,
        market=make_market(),
        contract=make_contract(),
        thesis=make_thesis(),
        has_nearby_strike=True,
        has_nearby_expiration=True,
        scenario_supportive=True,
        scenario_available=True,
    ))


def test_unverified_established_scores_zero_sage_confirmation():
    """P0: admissible-looking SageContext still scores 0 without verified_established."""
    forged = SageContext(
        status=SageStatus.ESTABLISHED,
        alignment=AlignmentState.CONSISTENT,
        operating_mode=OperatingMode.SAGE_INFORMED,
        claimed_established=True,
        verified_established=False,
        reason="deliberate-unverified-conjunction",
    )
    scored = _score(forged)
    assert scored.subfactors["macro.sage_confirmation"] == 0.0
    assert "macro.sage_confirmation" in scored.missing_subfactors


def _eval_alts(alternatives):
    return evaluate_candidate(
        ticker="SPY",
        direction=Direction.CALL,
        setup="expansion-call",
        market=make_market(),
        contract=make_contract(),
        alternatives=alternatives,
        thesis=make_thesis(),
        sage_payload=None,
        listed_expirations=LISTED,
        cutoff=NOW,
        run_id="p1-nearby",
    )


def test_missing_alternative_quote_time_no_nearby_credit():
    alts = [
        make_contract(occ_symbol="SPY261002C00585000", strike=585.0, delta=0.36, quote_time=None),
        make_contract(
            occ_symbol="SPY261009C00580000",
            strike=580.0,
            expiration=date(2026, 10, 9),
            dte=24,
            delta=0.40,
            quote_time=None,
        ),
    ]
    packet = _eval_alts(alts)
    assert "MISSING_NEARBY_STRIKE" in packet.vetoes
    assert "MISSING_NEARBY_EXPIRATION" in packet.vetoes
    assert packet.score.subfactors["contract.nearby_comparison"] == 0.0


def test_naive_alternative_quote_time_no_nearby_credit():
    naive = datetime(2026, 9, 15, 16, 0, 0)
    alts = [
        make_contract(occ_symbol="SPY261002C00585000", strike=585.0, delta=0.36, quote_time=naive, greeks_time=naive),
        make_contract(
            occ_symbol="SPY261009C00580000",
            strike=580.0,
            expiration=date(2026, 10, 9),
            dte=24,
            delta=0.40,
            quote_time=naive,
            greeks_time=naive,
        ),
    ]
    packet = _eval_alts(alts)
    assert "MISSING_NEARBY_STRIKE" in packet.vetoes
    assert "MISSING_NEARBY_EXPIRATION" in packet.vetoes
    assert packet.score.subfactors["contract.nearby_comparison"] == 0.0


def test_future_alternative_quote_time_no_nearby_credit():
    future = datetime(2026, 9, 16, 16, tzinfo=timezone.utc)
    alts = [
        make_contract(occ_symbol="SPY261002C00585000", strike=585.0, delta=0.36, quote_time=future, greeks_time=future),
        make_contract(
            occ_symbol="SPY261009C00580000",
            strike=580.0,
            expiration=date(2026, 10, 9),
            dte=24,
            delta=0.40,
            quote_time=future,
            greeks_time=future,
        ),
    ]
    packet = _eval_alts(alts)
    assert "MISSING_NEARBY_STRIKE" in packet.vetoes
    assert "MISSING_NEARBY_EXPIRATION" in packet.vetoes
    assert packet.score.subfactors["contract.nearby_comparison"] == 0.0


def test_stale_alternative_quote_time_no_nearby_credit():
    stale = datetime(2026, 9, 15, 12, tzinfo=timezone.utc)
    alts = [
        make_contract(occ_symbol="SPY261002C00585000", strike=585.0, delta=0.36, quote_time=stale, greeks_time=stale),
        make_contract(
            occ_symbol="SPY261009C00580000",
            strike=580.0,
            expiration=date(2026, 10, 9),
            dte=24,
            delta=0.40,
            quote_time=stale,
            greeks_time=stale,
        ),
    ]
    packet = _eval_alts(alts)
    assert "MISSING_NEARBY_STRIKE" in packet.vetoes
    assert "MISSING_NEARBY_EXPIRATION" in packet.vetoes
    assert packet.score.subfactors["contract.nearby_comparison"] == 0.0
