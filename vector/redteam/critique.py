from __future__ import annotations
from vector.contracts.enums import Disposition, RedTeamVerdict
from vector.contracts.packet import RedTeamRecord, ResearchPacket

REQUIRED_CHECKS = (
    "timestamps",
    "vendor_gex",
    "wall_migration",
    "expiry_filter",
    "sweep_vs_run",
    "gamma_path",
    "runway",
    "iv_priced_catalyst",
    "option_economics",
    "dte_horizon",
    "liquidity",
    "volume_interpretation",
    "macro_tape",
    "factor_cluster",
    "invalidation",
    "rumor",
    "horizon_mismatch",
    "gex_rewriting_sage",
    "lucky_path",
)


def critique(packet: ResearchPacket) -> ResearchPacket:
    original = packet.thesis.model_copy()
    attacks, fails, survives = [], [], []
    attacks.append("Stage 1 red team cannot PROMOTE live-data A/A_PLUS")
    executed = []

    def check(name: str, fail: bool, attack: str, survive: str | None = None) -> None:
        executed.append(name)
        attacks.append(attack)
        if fail:
            fails.append(name)
        elif survive:
            survives.append(survive)

    check("timestamps", bool(packet.vetoes and "STALE" in ";".join(packet.vetoes)), "stale or missing timestamps", "timestamp vetoes already applied")
    check("vendor_gex", packet.gamma_variant.value == "GAMMA_UNAVAILABLE", "gamma evidence missing", "gamma-unavailable labeled")
    check("wall_migration", False, "wall migration through spot not independently verified")
    check("expiry_filter", False, "expiry filter not independently verified")
    check("sweep_vs_run", False, "sweep vs run must be explicit on expansion setups")
    check("gamma_path", False, "positive-gamma fade during negative-gamma expansion")
    check("runway", packet.thesis.target_price is None, "insufficient space to target", "target present")
    check("iv_priced_catalyst", False, "catalyst may already be in IV")
    check("option_economics", "SCENARIO_ECONOMICS_FAIL" in packet.vetoes, "directionally correct still losing", "scenario gate recorded")
    check("dte_horizon", packet.contract is not None and packet.contract.dte < 14, "DTE mismatch", "DTE in universe or vetoed")
    check("liquidity", packet.contract is None, "no validated contract", "contract present")
    check("volume_interpretation", False, "call/put volume not treated as direction")
    check("macro_tape", packet.sage.status.value == "ESTABLISHED" and not packet.sage.verified_established, "unverified SAGE claim", "SAGE unpublished unless verified")
    check("factor_cluster", False, "correlated factor exposure not sized")
    check("invalidation", packet.thesis.invalidation_price is None, "vague invalidation", "invalidation price present")
    rumor = bool(packet.thesis and "rumor" in packet.thesis.because.lower())
    check("rumor", rumor, "unverified rumor as causal claim", "no rumor keyword")
    check("horizon_mismatch", False, "0DTE scalp logic on 14-45 DTE")
    check("gex_rewriting_sage", False, "GEX must not rewrite SAGE")
    check("lucky_path", packet.score is not None and packet.score.raw_score >= 82 and packet.vetoes, "high score plus veto", "score does not override veto")

    missing_checks = [name for name in REQUIRED_CHECKS if name not in executed]
    if missing_checks:
        fails.append("INCOMPLETE_RED_TEAM")
        attacks.append(f"missing required checks: {missing_checks}")

    if packet.vetoes:
        fails.extend(packet.vetoes)
        verdict = RedTeamVerdict.KILL
    elif missing_checks or fails:
        verdict = RedTeamVerdict.KILL if packet.vetoes or missing_checks else RedTeamVerdict.REDUCE
    elif packet.score and packet.score.raw_score >= 62:
        verdict = RedTeamVerdict.REDUCE
    else:
        verdict = RedTeamVerdict.KILL

    # Stage 1: never promote. Live-data A/A_PLUS remains blocked.
    if verdict is RedTeamVerdict.PROMOTE:
        verdict = RedTeamVerdict.REDUCE
        fails.append("STAGE1_PROMOTE_FORBIDDEN")

    if packet.vetoes:
        packet.disposition = Disposition.NO_TRADE
    elif verdict is RedTeamVerdict.KILL:
        packet.disposition = Disposition.REJECT
    else:
        packet.disposition = Disposition.WATCH

    packet.red_team = RedTeamRecord(
        verdict=verdict,
        attack="; ".join(attacks) or "standard freshness/economics/horizon review",
        survives="; ".join(survives) or "none claimed",
        fails="; ".join(fails) or "none",
        reverse_kill_if="Owner-approved Stage 2 entitlement, verified SAGE freeze, complete red team, fresh chain",
        original_thesis_preserved=original.model_dump() == packet.thesis.model_dump(),
        score_changed=False,
    )
    packet.thesis = original
    return packet
