"""Fail-closed admission decision primitive.

admit(X) iff every supplied required conjunct passes.

This type records the claim, the exact failed conjuncts, and the
caller-specified closed state. It does not implement
HOW-VECTOR-MUST-CONSUME.md and has no provider or network dependency.
"""

from __future__ import annotations

from enum import Enum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EvidenceState(str, Enum):
    """Required-evidence quality. Only COMPLETE can pass."""

    COMPLETE = "COMPLETE"
    MISSING = "MISSING"
    UNVERIFIED = "UNVERIFIED"
    STALE = "STALE"
    PARTIAL = "PARTIAL"


_NON_PASSABLE = frozenset(
    {
        EvidenceState.MISSING,
        EvidenceState.UNVERIFIED,
        EvidenceState.STALE,
        EvidenceState.PARTIAL,
    }
)


class AdmissionConjunct(BaseModel):
    """One required conjunct supplied by the caller.

    expected and observed are identity strings, not provider payloads.
    """

    model_config = ConfigDict(frozen=True)

    conjunct_id: str
    expected: str
    observed: str
    evidence_state: EvidenceState = EvidenceState.COMPLETE

    @field_validator("conjunct_id")
    @classmethod
    def _id_required(cls, value: str) -> str:
        token = value.strip()
        if not token:
            raise ValueError("conjunct_id is required")
        return token


class FailedConjunct(BaseModel):
    model_config = ConfigDict(frozen=True)

    conjunct_id: str
    expected: str
    observed: str
    reason: str


class AdmissionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    claim_class: str
    admitted: bool
    failed_conjuncts: tuple[FailedConjunct, ...] = Field(default_factory=tuple)
    closed_state: str | None = None


def evaluate_conjunct(conjunct: AdmissionConjunct) -> FailedConjunct | None:
    """Return a structured failure or None if this conjunct passes.

    Each conjunct is judged only against its own fields. Another
    conjunct cannot supply a missing value or repair a failure.
    """
    if conjunct.evidence_state in _NON_PASSABLE:
        return FailedConjunct(
            conjunct_id=conjunct.conjunct_id,
            expected=conjunct.expected,
            observed=conjunct.observed,
            reason=f"required evidence is {conjunct.evidence_state.value}",
        )
    if conjunct.expected != conjunct.observed:
        return FailedConjunct(
            conjunct_id=conjunct.conjunct_id,
            expected=conjunct.expected,
            observed=conjunct.observed,
            reason="observed value does not match expected",
        )
    return None


def evaluate_admission(
    *,
    claim_class: str,
    conjuncts: Sequence[AdmissionConjunct],
    closed_state: str,
) -> AdmissionResult:
    """Evaluate required conjuncts as a single conjunction.

    Success requires every supplied required conjunct to pass.
    There is no majority, score, or cross-conjunct repair.
    """
    snapshot = tuple(conjuncts)
    failures: list[FailedConjunct] = []
    for conjunct in snapshot:
        failure = evaluate_conjunct(conjunct)
        if failure is not None:
            failures.append(failure)

    if not failures:
        return AdmissionResult(
            claim_class=claim_class,
            admitted=True,
            failed_conjuncts=(),
            closed_state=None,
        )
    return AdmissionResult(
        claim_class=claim_class,
        admitted=False,
        failed_conjuncts=tuple(failures),
        closed_state=closed_state,
    )
