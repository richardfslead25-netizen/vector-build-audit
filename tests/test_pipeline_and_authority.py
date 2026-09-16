
import json
from datetime import date, datetime, timezone
from tests.helpers import make_contract, make_market, make_thesis
from vector.config import DEFAULT_AUTHORITY
from vector.contracts.enums import Direction, Disposition, GammaVariant, OperatingMode, RedTeamVerdict
from vector.pipeline import evaluate_candidate
from vector.scoring.scenarios import estimate_scenarios
CUTOFF = datetime(2026,9,15,16,5,tzinfo=timezone.utc)
LISTED = {date(2026,10,2), date(2026,10,9)}

def _eval(**kwargs):
    base = dict(ticker="SPY", direction=Direction.CALL, setup="expansion-call", market=make_market(),
        contract=make_contract(), alternatives=[
            make_contract(occ_symbol="SPY261002C00585000", strike=585.0, delta=0.36),
            make_contract(occ_symbol="SPY261009C00580000", strike=580.0, expiration=date(2026,10,9), dte=24, delta=0.40),
        ],
        thesis=make_thesis(), sage_payload=None, listed_expirations=LISTED, cutoff=CUTOFF, run_id="test-1")
    base.update(kwargs)
    return evaluate_candidate(**base)

def test_null_sage_strong_tape_behavior_only():
    p = _eval()
    assert p.operating_mode is OperatingMode.BEHAVIOR_ONLY
    assert p.score.subfactors["macro.sage_confirmation"] == 0.0
    assert p.authority.live_execution_enabled is False
    assert p.authority.paper_execution_enabled is False

def test_high_score_plus_hard_veto_is_no_trade():
    p = _eval(contract=make_contract(bid=1.0, ask=1.40))
    assert "SPREAD_GT_15PCT" in p.vetoes
    assert p.disposition is Disposition.NO_TRADE
    assert p.red_team.verdict in {RedTeamVerdict.KILL, RedTeamVerdict.REDUCE}

def test_saved_json_cannot_claim_execution_authority():
    blob = json.loads(_eval().model_dump_json())
    assert blob["authority"]["paper_execution_enabled"] is False
    assert blob["authority"]["live_execution_enabled"] is False
    assert DEFAULT_AUTHORITY.live_execution_enabled is False

def test_preserved_original_thesis_after_review():
    p = _eval()
    assert p.red_team.original_thesis_preserved is True
    assert p.thesis.trigger == make_thesis().trigger
    assert p.red_team.score_changed is False

def test_gamma_unavailable_variant():
    p = _eval(market=make_market(gamma=None))
    assert p.gamma_variant is GammaVariant.GAMMA_UNAVAILABLE
    assert p.score.factor_totals["gamma"] == 0.0

def test_scenario_units_and_multiplier():
    c = make_contract()
    rows = estimate_scenarios(c, spot=582.0)
    mid = c.mid
    sample = next(r for r in rows if r.spot_move == 0.0 and r.days_elapsed == 0 and r.iv_move == 0.0)
    assert sample.estimated_value == round(mid, 4)
    half = c.spread / 2.0
    expected = ((mid - half) - (mid + half + 0.65 / c.multiplier)) * c.multiplier - 0.65
    assert sample.pnl_per_contract == round(expected, 2)
    assert sample.pnl_per_contract < 0.0
    up = next(r for r in rows if r.spot_move == 0.08 and r.days_elapsed == 0 and r.iv_move == 0.0)
    assert up.pnl_per_contract is not None
    assert "first_order_greeks_taylor" in up.notes
    assert "local approximation" in up.notes

def test_put_negative_delta_pipeline():
    put = make_contract(right="P", occ_symbol="SPY261002P00580000", delta=-0.41, bid=5.8, ask=6.0)
    p = _eval(direction=Direction.PUT, contract=put)
    assert p.contract.abs_delta == 0.41
    assert "MISSING_DELTA" not in p.vetoes
