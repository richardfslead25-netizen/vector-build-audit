"""Append-only evaluation journal. Entries are not rewritten after outcomes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from vector.contracts.packet import ResearchPacket


class JournalEntry(BaseModel):
    seq: int
    recorded_at: datetime
    run_id: str
    ticker: str
    setup: str
    operating_mode: str
    gamma_variant: str
    sage_status: str
    score: float | None
    grade: str | None
    disposition: str
    red_team: str | None
    thesis_trigger: str
    thesis_invalidated_if: str
    original_thesis_preserved: bool | None
    authority: dict[str, Any]
    outcome: str | None = None
    outcome_notes: str | None = None


class EvaluationJournal:
    """In-memory append-only store. Persistence backends are Stage 5 work."""

    def __init__(self) -> None:
        self._entries: list[JournalEntry] = []

    def append_packet(self, packet: ResearchPacket) -> JournalEntry:
        entry = JournalEntry(
            seq=len(self._entries) + 1,
            recorded_at=datetime.now(timezone.utc),
            run_id=packet.run_id,
            ticker=packet.ticker,
            setup=packet.setup,
            operating_mode=packet.operating_mode.value,
            gamma_variant=packet.gamma_variant.value,
            sage_status=packet.sage.status.value,
            score=None if packet.score is None else packet.score.raw_score,
            grade=None if packet.score is None else packet.score.grade.value,
            disposition=packet.disposition.value,
            red_team=None if packet.red_team is None else packet.red_team.verdict.value,
            thesis_trigger=packet.thesis.trigger,
            thesis_invalidated_if=packet.thesis.invalidated_if,
            original_thesis_preserved=None if packet.red_team is None else packet.red_team.original_thesis_preserved,
            authority=packet.authority.model_dump(),
        )
        self._entries.append(entry)
        return entry

    def rewrite(self, *_args: Any, **_kwargs: Any) -> None:
        raise PermissionError("evaluation journal is append-only")

    @property
    def entries(self) -> tuple[JournalEntry, ...]:
        return tuple(self._entries)
