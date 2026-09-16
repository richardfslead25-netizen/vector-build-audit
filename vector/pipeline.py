from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from vector.config import DEFAULT_AUTHORITY, DEFAULT_SETTINGS, RULES_VERSION
from vector.contracts.enums import Direction, Disposition, GammaVariant
from vector.contracts.market import MarketSnapshot
from vector.contracts.packet import ResearchPacket
from vector.eligibility.gates import evaluate_eligibility
from vector.features.expiration import classify_dte_band
from vector.redteam.critique import critique
from vector.sage.adapter import SageReadOnlyAdapter
from vector.scoring.engine import ScoreInputs, score_candidate
from vector.scoring.scenarios import estimate_scenarios, scenarios_support_thesis

def gamma_variant_of(market: MarketSnapshot) -> GammaVariant:
    g = market.gamma
    required = (
        g is not None and g.printable and g.vendor and g.methodology and g.underlying
        and g.expiry_coverage and g.model_as_of is not None and g.units
        and g.sign_convention and g.spot_reference is not None
    )
    return GammaVariant.GAMMA_CONFIRMED if required else GammaVariant.GAMMA_UNAVAILABLE

def evaluate_candidate(*, ticker, direction, setup, market, contract, thesis, sage_payload,
                       alternatives=None, listed_expirations=None, cutoff=None, settings=None,
                       run_id=None, premarket_without_live_chain=False) -> ResearchPacket:
    settings = settings or DEFAULT_SETTINGS
    cutoff = cutoff or datetime.now(timezone.utc)
    sage = SageReadOnlyAdapter(settings).ingest(
        sage_payload, now=cutoff, observed_direction=direction.value,
        transmission_observed=market.transmission_observed,
    )
    variant = gamma_variant_of(market)
    alternatives = alternatives or []
    vetoes = evaluate_eligibility(contract, now=cutoff, listed_expirations=listed_expirations,
                                  settings=settings, premarket_without_live_chain=premarket_without_live_chain)
    scenarios, scenario_ok = [], None
    if contract is not None and market.spot:
        scenarios = estimate_scenarios(contract, market.spot, settings)
        scenario_ok = scenarios_support_thesis(contract, market.spot, contract.right, settings)
    dte = contract.dte if contract is not None else 0
    score = score_candidate(ScoreInputs(
        direction=direction, dte=dte, sage=sage, gamma_variant=variant, market=market,
        contract=contract, thesis=thesis, has_nearby_comparison=len(alternatives) >= 1,
        scenario_supportive=scenario_ok,
    ), settings)
    disposition = Disposition.WATCH
    if vetoes:
        disposition = Disposition.NO_TRADE
    elif score.grade.value == "REJECT":
        disposition = Disposition.REJECT
    packet = ResearchPacket(
        run_id=run_id or uuid4().hex[:12], cutoff=cutoff, generated_at=datetime.now(timezone.utc),
        rules_version=RULES_VERSION, operating_mode=sage.operating_mode, gamma_variant=variant,
        sage=sage, alignment=sage.alignment, ticker=ticker, direction=direction, setup=setup,
        thesis=thesis, contract=contract, alternatives=alternatives, scenarios=scenarios,
        score=score, vetoes=vetoes, missing_evidence=list(score.missing_subfactors),
        disposition=disposition, authority=DEFAULT_AUTHORITY.model_copy(),
        notes=[f"dte_band={classify_dte_band(dte).value}", f"mode={sage.operating_mode.value}",
               f"gamma_variant={variant.value}"],
    )
    if packet.authority.paper_execution_enabled or packet.authority.live_execution_enabled:
        packet.vetoes.append("EXECUTION_AUTHORITY_MUST_REMAIN_DISABLED")
        packet.disposition = Disposition.NO_TRADE
        packet.authority = DEFAULT_AUTHORITY.model_copy()
    return critique(packet)
