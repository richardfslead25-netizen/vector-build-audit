from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from vector.config import DEFAULT_AUTHORITY, DEFAULT_SETTINGS, RULES_VERSION, Settings
from vector.contracts.enums import Direction, Disposition, GammaVariant
from vector.contracts.market import MarketSnapshot
from vector.contracts.options import OptionContract
from vector.contracts.packet import ResearchPacket, Thesis
from vector.eligibility.gates import coherence_vetoes, evaluate_eligibility
from vector.features.expiration import calendar_dte, classify_dte_band
from vector.redteam.critique import critique
from vector.sage.adapter import SageReadOnlyAdapter
from vector.scoring.engine import ScoreInputs, score_candidate
from vector.scoring.scenarios import estimate_scenarios, scenarios_available, scenarios_support_thesis

NEARBY_STRIKE_PCT = 0.03


def gamma_variant_of(market: MarketSnapshot) -> GammaVariant:
    g = market.gamma
    required = (
        g is not None and g.printable and g.vendor and g.methodology and g.underlying
        and g.expiry_coverage and g.model_as_of is not None and g.units
        and g.sign_convention and g.spot_reference is not None
    )
    return GammaVariant.GAMMA_CONFIRMED if required else GammaVariant.GAMMA_UNAVAILABLE


def _alternative_fresh_at_cutoff(
    alt: OptionContract,
    *,
    cutoff,
    settings: Settings | None = None,
) -> bool:
    """Nearby comparisons require a usable quote time at the evaluation cutoff."""
    cfg = settings or DEFAULT_SETTINGS
    stamp = alt.quote_time
    if stamp is None:
        return False
    if cfg.universe.reject_naive_timestamps and stamp.tzinfo is None:
        return False
    aware = stamp if stamp.tzinfo is not None else stamp.replace(tzinfo=timezone.utc)
    if cfg.universe.reject_future_timestamps and aware > cutoff:
        return False
    if cutoff - aware > cfg.freshness.chain_max_age:
        return False
    return True


def _eligible_alternative(
    contract: OptionContract,
    alt: OptionContract,
    *,
    cutoff,
    settings: Settings | None = None,
) -> bool:
    if alt.underlying != contract.underlying:
        return False
    if alt.right != contract.right:
        return False
    if alt.adjusted or alt.nonstandard_deliverable:
        return False
    if not _alternative_fresh_at_cutoff(alt, cutoff=cutoff, settings=settings):
        return False
    if contract.quote_time and alt.quote_time and alt.quote_time.tzinfo and contract.quote_time.tzinfo:
        if alt.quote_time > contract.quote_time:
            return False
    return True


def _comparison_flags(
    contract: OptionContract | None,
    alternatives: list[OptionContract],
    spot: float | None = None,
    *,
    cutoff=None,
    settings: Settings | None = None,
) -> tuple[bool, bool]:
    if contract is None:
        return False, False
    nearby_strike = False
    nearby_expiry = False
    band = max(1.0, (spot or contract.strike) * NEARBY_STRIKE_PCT)
    for alt in alternatives:
        if not _eligible_alternative(contract, alt, cutoff=cutoff, settings=settings):
            continue
        strike_gap = abs(alt.strike - contract.strike)
        if alt.expiration == contract.expiration and strike_gap > 1e-9 and strike_gap <= band:
            nearby_strike = True
        if alt.expiration != contract.expiration and strike_gap <= band:
            nearby_expiry = True
    return nearby_strike, nearby_expiry


def evaluate_candidate(
    *,
    ticker,
    direction,
    setup,
    market,
    contract,
    thesis,
    sage_payload,
    alternatives=None,
    listed_expirations=None,
    cutoff=None,
    settings=None,
    run_id=None,
    premarket_without_live_chain=False,
) -> ResearchPacket:
    settings = settings or DEFAULT_SETTINGS
    cutoff = cutoff or datetime.now(timezone.utc)
    sage = SageReadOnlyAdapter(settings).ingest(
        sage_payload,
        now=cutoff,
        observed_direction=direction.value,
        transmission_observed=market.transmission_observed,
    )
    variant = gamma_variant_of(market)
    alternatives = list(alternatives or [])
    working = contract.model_copy() if contract is not None else None
    vetoes = evaluate_eligibility(
        working,
        now=cutoff,
        listed_expirations=listed_expirations,
        settings=settings,
        premarket_without_live_chain=premarket_without_live_chain,
        as_of_date=cutoff.date(),
    )
    vetoes.extend(coherence_vetoes(ticker=ticker, direction=direction, market=market, contract=working))
    nearby_strike, nearby_expiry = _comparison_flags(
        working,
        alternatives,
        getattr(market, "spot", None),
        cutoff=cutoff,
        settings=settings,
    )
    if working is not None and not nearby_strike:
        vetoes.append("MISSING_NEARBY_STRIKE")
    if working is not None and not nearby_expiry:
        vetoes.append("MISSING_NEARBY_EXPIRATION")
    if thesis.target_price is None or thesis.invalidation_price is None or thesis.horizon_sessions is None:
        vetoes.append("THESIS_GEOMETRY_INCOMPLETE")
    scenarios, scenario_ok, scenario_avail = [], None, False
    if working is not None and market.spot:
        scenario_avail = scenarios_available(working, market.spot)
        if scenario_avail:
            scenarios = estimate_scenarios(working, market.spot, settings)
            scenario_ok = scenarios_support_thesis(working, market.spot, working.right, settings, thesis)
        else:
            vetoes.append("SCENARIOS_UNAVAILABLE")
    if scenario_avail and scenario_ok is False:
        vetoes.append("SCENARIO_ECONOMICS_FAIL")
    dte = calendar_dte(cutoff.date(), working.expiration) if working is not None else 0
    score = score_candidate(ScoreInputs(
        direction=direction,
        dte=dte,
        sage=sage,
        gamma_variant=variant,
        market=market,
        contract=working,
        thesis=thesis,
        has_nearby_strike=nearby_strike,
        has_nearby_expiration=nearby_expiry,
        scenario_supportive=scenario_ok,
        scenario_available=scenario_avail,
    ), settings)
    disposition = Disposition.WATCH
    if vetoes:
        disposition = Disposition.NO_TRADE
    elif score.grade.value == "REJECT":
        disposition = Disposition.REJECT
    packet = ResearchPacket(
        run_id=run_id or uuid4().hex[:12],
        cutoff=cutoff,
        generated_at=datetime.now(timezone.utc),
        rules_version=RULES_VERSION,
        operating_mode=sage.operating_mode,
        gamma_variant=variant,
        sage=sage,
        alignment=sage.alignment,
        ticker=ticker,
        direction=direction,
        setup=setup,
        thesis=thesis.model_copy(),
        contract=working,
        alternatives=alternatives,
        scenarios=scenarios,
        score=score,
        vetoes=list(dict.fromkeys(vetoes)),
        missing_evidence=list(score.missing_subfactors),
        disposition=disposition,
        authority=DEFAULT_AUTHORITY.model_copy(),
        notes=[
            f"dte_band={classify_dte_band(dte).value}",
            f"mode={sage.operating_mode.value}",
            f"gamma_variant={variant.value}",
            "red_team=stage1-no-promote",
        ],
    )
    if packet.authority.paper_execution_enabled or packet.authority.live_execution_enabled:
        packet.vetoes.append("EXECUTION_AUTHORITY_MUST_REMAIN_DISABLED")
        packet.disposition = Disposition.NO_TRADE
        packet.authority = DEFAULT_AUTHORITY.model_copy()
    return critique(packet)
