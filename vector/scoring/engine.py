"""Deterministic scoring. Missing evidence scores zero. No reweighting."""
from __future__ import annotations
from dataclasses import dataclass
from vector.config import DTE_FACTOR_WEIGHTS, DEFAULT_SETTINGS, SUBFACTOR_SHARES, Settings
from vector.contracts.enums import AlignmentState, Direction, DteBand, GammaVariant, Grade, OperatingMode, SageStatus
from vector.contracts.market import FeaturePacket, GammaSnapshot, MarketSnapshot
from vector.contracts.options import OptionContract
from vector.contracts.packet import ScoreBreakdown, Thesis
from vector.contracts.sage import SageContext
from vector.features.expiration import classify_dte_band

@dataclass(frozen=True)
class ScoreInputs:
    direction: Direction
    dte: int
    sage: SageContext
    gamma_variant: GammaVariant
    market: MarketSnapshot
    contract: OptionContract | None
    thesis: Thesis | None
    has_nearby_comparison: bool
    scenario_supportive: bool | None

def classify_grade(score: float, settings: Settings | None = None) -> Grade:
    t = (settings or DEFAULT_SETTINGS).grades
    if score >= t.a_plus: return Grade.A_PLUS
    if score >= t.a: return Grade.A
    if score >= t.b_developing: return Grade.B_DEVELOPING
    if score >= t.watch: return Grade.WATCH
    return Grade.REJECT

def _cap(points: float, maximum: float) -> float:
    return 0.0 if points < 0 else maximum if points > maximum else points

def _sub_max(factor: str, name: str, factor_max: int) -> float:
    return factor_max * SUBFACTOR_SHARES[factor][name]

def score_candidate(inputs: ScoreInputs, settings: Settings | None = None) -> ScoreBreakdown:
    settings = settings or DEFAULT_SETTINGS
    band = classify_dte_band(inputs.dte)
    if band is DteBand.OUT_OF_RANGE:
        maxima = {k: 0 for k in DTE_FACTOR_WEIGHTS["14-21"]}
        return ScoreBreakdown(dte_band=band, factor_maxima=maxima, subfactors={},
            factor_totals={k: 0.0 for k in maxima}, missing_subfactors=["dte_out_of_range"],
            raw_score=0.0, grade=Grade.REJECT, reweighted=False)
    maxima = dict(DTE_FACTOR_WEIGHTS[band.value])
    subs, missing = {}, []
    features, gamma = inputs.market.features, inputs.market.gamma
    if inputs.gamma_variant is GammaVariant.GAMMA_UNAVAILABLE:
        for name in SUBFACTOR_SHARES["gamma"]:
            subs[f"gamma.{name}"] = 0.0
            missing.append(f"gamma.{name}")
    else:
        _score_gamma(subs, missing, maxima["gamma"], gamma, features, inputs.direction)
    _score_momentum(subs, missing, maxima["momentum"], features, inputs.direction)
    _score_catalyst(subs, missing, maxima["catalyst"], inputs.market)
    _score_flow(subs, missing, maxima["flow"], inputs.market, features)
    _score_macro(subs, missing, maxima["macro"], inputs.sage, inputs.market)
    _score_contract(subs, missing, maxima["contract"], inputs.contract, settings, inputs.has_nearby_comparison, inputs.scenario_supportive)
    _score_risk(subs, missing, maxima["risk"], inputs.thesis)
    factor_totals = {f: round(sum(v for k,v in subs.items() if k.startswith(f+".")), 10) for f in maxima}
    raw = round(sum(factor_totals.values()), 10)
    return ScoreBreakdown(dte_band=band, factor_maxima=maxima, subfactors=subs,
        factor_totals=factor_totals, missing_subfactors=missing, raw_score=raw,
        grade=classify_grade(raw, settings), reweighted=False)

def _score_gamma(subs, missing, factor_max, gamma, features, direction):
    if gamma is None or not gamma.printable:
        for name in SUBFACTOR_SHARES["gamma"]:
            subs[f"gamma.{name}"] = 0.0; missing.append(f"gamma.{name}")
        return
    sign_max = _sub_max("gamma", "gex_sign_and_regime", factor_max)
    flip_max = _sub_max("gamma", "flip_location", factor_max)
    wall_max = _sub_max("gamma", "walls_and_runway", factor_max)
    if gamma.regime.value in {"POSITIVE", "NEGATIVE", "NEAR_FLIP"}:
        sign_pts = sign_max * (0.7 if gamma.regime.value == "POSITIVE" else 1.0)
    else:
        sign_pts = 0.0; missing.append("gamma.gex_sign_and_regime")
    subs["gamma.gex_sign_and_regime"] = _cap(sign_pts, sign_max)
    spot = features.close if features else gamma.spot_reference
    if gamma.flip is not None and spot:
        dist = abs(spot - gamma.flip) / spot
        flip_pts = flip_max if dist >= 0.01 else flip_max * 0.5 if dist >= 0.003 else flip_max * 0.2
    else:
        flip_pts = 0.0; missing.append("gamma.flip_location")
    subs["gamma.flip_location"] = _cap(flip_pts, flip_max)
    wall = gamma.call_wall if direction is Direction.CALL else gamma.put_wall
    if wall is not None and spot:
        runway = abs(wall - spot) / spot
        wall_pts = wall_max if runway >= 0.02 else wall_max * 0.6 if runway >= 0.01 else wall_max * 0.2
    else:
        wall_pts = 0.0; missing.append("gamma.walls_and_runway")
    subs["gamma.walls_and_runway"] = _cap(wall_pts, wall_max)

def _score_momentum(subs, missing, factor_max, features, direction):
    def award(name, value, frac):
        mx = _sub_max("momentum", name, factor_max)
        if value is None:
            subs[f"momentum.{name}"] = 0.0; missing.append(f"momentum.{name}")
        else:
            subs[f"momentum.{name}"] = _cap(frac * mx, mx)
    if features is None:
        for name in SUBFACTOR_SHARES["momentum"]:
            subs[f"momentum.{name}"] = 0.0; missing.append(f"momentum.{name}")
        return
    if features.trend is None:
        award("price_structure", None, 0.0)
    elif (features.trend == "ABOVE_EMA50" and direction is Direction.CALL) or (features.trend == "BELOW_EMA50" and direction is Direction.PUT):
        award("price_structure", 1.0, 1.0)
    else:
        award("price_structure", 0.25, 0.25)
    mom = features.momentum_level
    if mom is None: award("momentum_level", None, 0.0)
    else:
        signed = mom if direction is Direction.CALL else -mom
        award("momentum_level", mom, 1.0 if signed >= 0.03 else 0.5 if signed >= 0.01 else 0.15)
    chg = features.momentum_change
    if chg is None: award("momentum_change", None, 0.0)
    else:
        signed = chg if direction is Direction.CALL else -chg
        award("momentum_change", chg, 1.0 if signed >= 0.01 else 0.4 if signed > 0 else 0.1)
    rvol = features.relative_volume
    if rvol is None: award("relative_volume", None, 0.0)
    else:
        award("relative_volume", rvol, 1.0 if rvol >= 1.5 else 0.6 if rvol >= 1.1 else 0.2)

def _score_catalyst(subs, missing, factor_max, market):
    v_max = _sub_max("catalyst", "verified_catalyst", factor_max)
    t_max = _sub_max("catalyst", "timing_fit", factor_max)
    if not market.catalyst_verified or not market.catalyst_id:
        subs["catalyst.verified_catalyst"] = 0.0; missing.append("catalyst.verified_catalyst")
    else:
        subs["catalyst.verified_catalyst"] = v_max
    if not market.catalyst_inside_horizon or not market.catalyst_verified:
        subs["catalyst.timing_fit"] = 0.0; missing.append("catalyst.timing_fit")
    else:
        subs["catalyst.timing_fit"] = t_max

def _score_flow(subs, missing, factor_max, market, features):
    vp_max = _sub_max("flow", "volume_profile", factor_max)
    rs_max = _sub_max("flow", "breadth_or_rs", factor_max)
    of_max = _sub_max("flow", "order_flow", factor_max)
    if market.volume_profile_present and features and (features.vah or features.poc):
        subs["flow.volume_profile"] = vp_max
    else:
        subs["flow.volume_profile"] = 0.0; missing.append("flow.volume_profile")
    if market.breadth_present or (features and features.relative_strength is not None):
        rs = features.relative_strength if features else None
        if rs is None:
            subs["flow.breadth_or_rs"] = rs_max * 0.4 if market.breadth_present else 0.0
        else:
            subs["flow.breadth_or_rs"] = rs_max if abs(rs) >= 0.01 else rs_max * 0.4
    else:
        subs["flow.breadth_or_rs"] = 0.0; missing.append("flow.breadth_or_rs")
    if market.order_flow_present:
        subs["flow.order_flow"] = of_max
    else:
        subs["flow.order_flow"] = 0.0; missing.append("flow.order_flow")

def _score_macro(subs, missing, factor_max, sage, market):
    sage_max = _sub_max("macro", "sage_confirmation", factor_max)
    tx_max = _sub_max("macro", "observed_transmission", factor_max)
    sage_ok = (sage.operating_mode is OperatingMode.SAGE_INFORMED and sage.status is SageStatus.ESTABLISHED and sage.alignment is AlignmentState.CONSISTENT)
    if sage_ok: subs["macro.sage_confirmation"] = sage_max
    else:
        subs["macro.sage_confirmation"] = 0.0; missing.append("macro.sage_confirmation")
    if market.transmission_observed:
        subs["macro.observed_transmission"] = tx_max * (0.4 if sage.alignment is AlignmentState.INCONSISTENT else 1.0)
    else:
        subs["macro.observed_transmission"] = 0.0; missing.append("macro.observed_transmission")

def _score_contract(subs, missing, factor_max, contract, settings, has_nearby, scenario_supportive):
    liq_max = _sub_max("contract", "liquidity_spread", factor_max)
    dlt_max = _sub_max("contract", "delta_fit", factor_max)
    scn_max = _sub_max("contract", "scenario_economics", factor_max)
    cmp_max = _sub_max("contract", "nearby_comparison", factor_max)
    if contract is None:
        for name in SUBFACTOR_SHARES["contract"]:
            subs[f"contract.{name}"] = 0.0; missing.append(f"contract.{name}")
        return
    if contract.spread_pct is None:
        subs["contract.liquidity_spread"] = 0.0; missing.append("contract.liquidity_spread")
    elif contract.spread_pct <= settings.universe.spread_strong_pct: subs["contract.liquidity_spread"] = liq_max
    elif contract.spread_pct <= settings.universe.spread_acceptable_pct: subs["contract.liquidity_spread"] = liq_max * 0.7
    elif contract.spread_pct <= settings.universe.spread_veto_pct_of_mid: subs["contract.liquidity_spread"] = liq_max * 0.3
    else: subs["contract.liquidity_spread"] = 0.0
    abs_d = contract.abs_delta
    if abs_d is None:
        subs["contract.delta_fit"] = 0.0; missing.append("contract.delta_fit")
    elif settings.universe.preferred_abs_delta_low <= abs_d <= settings.universe.preferred_abs_delta_high:
        subs["contract.delta_fit"] = dlt_max
    elif 0.25 <= abs_d <= 0.60: subs["contract.delta_fit"] = dlt_max * 0.4
    else: subs["contract.delta_fit"] = 0.0
    if scenario_supportive is None:
        subs["contract.scenario_economics"] = 0.0; missing.append("contract.scenario_economics")
    elif scenario_supportive: subs["contract.scenario_economics"] = scn_max
    else: subs["contract.scenario_economics"] = scn_max * 0.2
    if has_nearby: subs["contract.nearby_comparison"] = cmp_max
    else:
        subs["contract.nearby_comparison"] = 0.0; missing.append("contract.nearby_comparison")

def _score_risk(subs, missing, factor_max, thesis):
    inv_max = _sub_max("risk", "invalidation_quality", factor_max)
    tgt_max = _sub_max("risk", "target_distance", factor_max)
    if thesis is None or not thesis.invalidated_if or thesis.invalidated_if.upper() in {"UNAVAILABLE", "NONE", ""}:
        subs["risk.invalidation_quality"] = 0.0; missing.append("risk.invalidation_quality")
    else:
        subs["risk.invalidation_quality"] = inv_max
    if thesis is None or not thesis.expected_response:
        subs["risk.target_distance"] = 0.0; missing.append("risk.target_distance")
    else:
        subs["risk.target_distance"] = tgt_max
