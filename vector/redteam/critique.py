from __future__ import annotations
from vector.contracts.enums import Disposition, RedTeamVerdict
from vector.contracts.packet import RedTeamRecord, ResearchPacket, Thesis

def critique(packet: ResearchPacket) -> ResearchPacket:
    original = packet.thesis.model_copy()
    attacks, fails, survives = [], [], []
    if packet.vetoes:
        attacks.append("hard veto already active"); fails.extend(packet.vetoes)
    if packet.contract is None:
        attacks.append("no validated contract"); fails.append("MISSING_CONTRACT")
    if packet.gamma_variant.value == "GAMMA_UNAVAILABLE":
        attacks.append("gamma evidence missing; technical levels are not a substitute")
        survives.append("gamma-unavailable variant is valid if labeled")
    if packet.sage.status.value != "ESTABLISHED":
        attacks.append("SAGE not established; confirmation points must be zero")
        survives.append("BEHAVIOR_ONLY is allowed")
    if packet.score and packet.score.raw_score >= 82 and packet.vetoes:
        attacks.append("high score cannot override veto"); fails.append("HIGH_SCORE_PLUS_VETO")
    if packet.thesis and "rumor" in packet.thesis.because.lower():
        attacks.append("unverified rumor as causal claim"); fails.append("RUMOR_CATALYST")
    if packet.contract and packet.contract.dte <= 21:
        attacks.append("14-21 DTE requires 2-3 session reassessment if move has not printed")
        survives.append("reassessment rule recorded; not execution authority")
    if fails and packet.vetoes:
        verdict = RedTeamVerdict.KILL
    elif fails:
        verdict = RedTeamVerdict.REDUCE
    elif packet.score and packet.score.raw_score >= 82 and not packet.vetoes:
        verdict = RedTeamVerdict.PROMOTE
    elif packet.score and packet.score.raw_score >= 62:
        verdict = RedTeamVerdict.REDUCE
    else:
        verdict = RedTeamVerdict.KILL
    if packet.vetoes:
        packet.disposition = Disposition.NO_TRADE
        if verdict is RedTeamVerdict.PROMOTE:
            verdict = RedTeamVerdict.KILL
    elif verdict is RedTeamVerdict.PROMOTE and packet.score and packet.score.grade.value in {"A", "A_PLUS"}:
        packet.disposition = Disposition.RESEARCH_ELIGIBLE
    elif verdict in {RedTeamVerdict.REDUCE, RedTeamVerdict.OPPOSITE_PATH}:
        packet.disposition = Disposition.WATCH
    else:
        packet.disposition = Disposition.REJECT
    packet.red_team = RedTeamRecord(
        verdict=verdict,
        attack="; ".join(attacks) or "standard freshness/economics/horizon review",
        survives="; ".join(survives) or "none claimed",
        fails="; ".join(fails) or "none",
        reverse_kill_if="fresh chain, sourced GEX, explicit invalidation, supportive scenarios",
        original_thesis_preserved=original.model_dump() == packet.thesis.model_dump(),
        score_changed=False,
    )
    packet.thesis = original
    return packet
