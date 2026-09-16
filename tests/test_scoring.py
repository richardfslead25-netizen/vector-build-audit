
from datetime import datetime, timezone
from tests.helpers import make_contract, make_gamma, make_market, make_thesis
from vector.contracts.enums import Direction, DteBand, GammaVariant, Grade, SageStatus
from vector.contracts.sage import SageContext
from vector.sage.adapter import SageReadOnlyAdapter
from vector.scoring.engine import ScoreInputs, classify_grade, score_candidate

def _sage_none():
    return SageReadOnlyAdapter().ingest(None)

def _sage_established():
    return SageReadOnlyAdapter().ingest({
        "established": True,
        "regime": "risk-on",
        "source_identity": "SAGE",
        "schema_version": "sage-unagreed-placeholder",
        "cutoff": "2026-09-15T12:00:00+00:00",
        "receipt_time": "2026-09-15T12:05:00+00:00",
        "freeze_identity": "freeze-abc",
        "official_freeze_count": 1,
        "posterior": {"risk-on": 1.0},
    }, now=datetime(2026, 9, 15, 16, tzinfo=timezone.utc))

def _inputs(**kwargs):
    base = dict(direction=Direction.CALL, dte=18, sage=_sage_none(), gamma_variant=GammaVariant.GAMMA_CONFIRMED,
                market=make_market(), contract=make_contract(), thesis=make_thesis(),
                has_nearby_strike=True, has_nearby_expiration=True,
                scenario_supportive=True, scenario_available=True)
    base.update(kwargs)
    return ScoreInputs(**base)

def test_no_missing_data_reweighting():
    scored = score_candidate(_inputs(gamma_variant=GammaVariant.GAMMA_UNAVAILABLE))
    assert scored.reweighted is False
    assert scored.factor_totals["gamma"] == 0.0
    assert scored.factor_maxima["gamma"] == 22
    assert scored.raw_score <= 100 - 22 + 1e-9

def test_no_gamma_points_from_technical_substitute():
    scored = score_candidate(_inputs(market=make_market(gamma=None), gamma_variant=GammaVariant.GAMMA_UNAVAILABLE))
    assert all(v == 0.0 for k,v in scored.subfactors.items() if k.startswith("gamma."))

def test_mixed_vendor_missing_gamma_zero():
    g = make_gamma(printable=False, regime="GEX_NOT_PRINTABLE", flip=None, call_wall=None)
    scored = score_candidate(_inputs(market=make_market(gamma=g), gamma_variant=GammaVariant.GAMMA_CONFIRMED))
    assert scored.factor_totals["gamma"] == 0.0

def test_sage_confirmation_zero_when_unavailable():
    scored = score_candidate(_inputs(sage=_sage_none()))
    assert scored.subfactors["macro.sage_confirmation"] == 0.0
    assert scored.subfactors["macro.observed_transmission"] > 0

def test_sage_confirmation_zero_when_admission_disabled():
    none = score_candidate(_inputs(sage=_sage_none()))
    est = score_candidate(_inputs(sage=_sage_established()))
    assert none.subfactors["macro.sage_confirmation"] == 0.0
    assert est.subfactors["macro.sage_confirmation"] == 0.0

def test_fixed_dte_band_weights_not_interpolated():
    a, b = score_candidate(_inputs(dte=21)), score_candidate(_inputs(dte=22))
    assert a.dte_band is DteBand.DTE_14_21 and b.dte_band is DteBand.DTE_22_35
    assert a.factor_maxima["gamma"] == 22 and b.factor_maxima["gamma"] == 18
    assert a.factor_maxima["macro"] == 8 and b.factor_maxima["macro"] == 16

def test_score_rounding_boundaries():
    assert classify_grade(90.0) is Grade.A_PLUS
    assert classify_grade(89.999) is Grade.A
    assert classify_grade(82.0) is Grade.A
    assert classify_grade(81.999) is Grade.B_DEVELOPING
    assert classify_grade(72.0) is Grade.B_DEVELOPING
    assert classify_grade(71.999) is Grade.WATCH
    assert classify_grade(62.0) is Grade.WATCH
    assert classify_grade(61.999) is Grade.REJECT

def test_deterministic_repeated_scoring():
    a, b = score_candidate(_inputs()), score_candidate(_inputs())
    assert a.raw_score == b.raw_score and a.subfactors == b.subfactors
