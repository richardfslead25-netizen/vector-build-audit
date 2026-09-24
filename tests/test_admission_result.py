"""Structured admission primitive. Synthetic values only. No network."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from vector.admission import (
    AdmissionConjunct,
    AdmissionResult,
    EvidenceState,
    evaluate_admission,
)
from vector.admission.result import evaluate_conjunct


def _c(
    conjunct_id: str,
    expected: str = "ok",
    observed: str = "ok",
    state: EvidenceState = EvidenceState.COMPLETE,
) -> AdmissionConjunct:
    return AdmissionConjunct(
        conjunct_id=conjunct_id,
        expected=expected,
        observed=observed,
        evidence_state=state,
    )


def test_all_conjuncts_true_is_admitted():
    result = evaluate_admission(
        claim_class="SYNTHETIC_CLAIM",
        conjuncts=(_c("C1"), _c("C2"), _c("C3")),
        closed_state="CLOSED",
    )
    assert result.admitted is True
    assert result.failed_conjuncts == ()
    assert result.closed_state is None
    assert result.claim_class == "SYNTHETIC_CLAIM"


def test_one_false_retains_exact_failed_conjunct():
    result = evaluate_admission(
        claim_class="SYNTHETIC_CLAIM",
        conjuncts=(_c("C1"), _c("C2", expected="need", observed="have"), _c("C3")),
        closed_state="REJECTED",
    )
    assert result.admitted is False
    assert len(result.failed_conjuncts) == 1
    failed = result.failed_conjuncts[0]
    assert failed.conjunct_id == "C2"
    assert failed.expected == "need"
    assert failed.observed == "have"
    assert failed.reason == "observed value does not match expected"


def test_multiple_failures_all_retained():
    result = evaluate_admission(
        claim_class="SYNTHETIC_CLAIM",
        conjuncts=(
            _c("C1", expected="a", observed="b"),
            _c("C2"),
            _c("C3", expected="x", observed="y"),
        ),
        closed_state="REJECTED",
    )
    assert result.admitted is False
    ids = [item.conjunct_id for item in result.failed_conjuncts]
    assert ids == ["C1", "C3"]


def test_missing_or_unverified_required_evidence_cannot_pass():
    for state in (
        EvidenceState.MISSING,
        EvidenceState.UNVERIFIED,
        EvidenceState.STALE,
        EvidenceState.PARTIAL,
    ):
        sneaky = _c("Cx", expected="same", observed="same", state=state)
        result = evaluate_admission(
            claim_class="SYNTHETIC_CLAIM",
            conjuncts=(sneaky,),
            closed_state="UNAVAILABLE",
        )
        assert result.admitted is False, state
        assert result.failed_conjuncts[0].conjunct_id == "Cx"
        assert result.failed_conjuncts[0].reason == f"required evidence is {state.value}"


def test_rejection_returns_specified_closed_state():
    result = evaluate_admission(
        claim_class="DEMO_CLASS",
        conjuncts=(_c("C1", expected="1", observed="0"),),
        closed_state="CLAIM_UNAVAILABLE",
    )
    assert result.admitted is False
    assert result.closed_state == "CLAIM_UNAVAILABLE"


def test_evaluation_does_not_mutate_supplied_evidence():
    original = [
        _c("C1"),
        _c("C2", expected="keep", observed="changed"),
    ]
    before = [item.model_dump() for item in original]
    result = evaluate_admission(
        claim_class="SYNTHETIC_CLAIM",
        conjuncts=original,
        closed_state="REJECTED",
    )
    assert result.admitted is False
    assert [item.model_dump() for item in original] == before
    original.append(_c("C3"))
    assert [item.conjunct_id for item in result.failed_conjuncts] == ["C2"]


def test_eight_of_nine_still_rejected():
    conjuncts = [_c(f"C{i}") for i in range(1, 9)]
    conjuncts.append(_c("C9", expected="pass", observed="fail"))
    result = evaluate_admission(
        claim_class="NINE_CONJUNCT_SHAPE_ONLY",
        conjuncts=conjuncts,
        closed_state="UNAVAILABLE",
    )
    assert result.admitted is False
    assert len(result.failed_conjuncts) == 1
    assert result.failed_conjuncts[0].conjunct_id == "C9"
    assert result.closed_state == "UNAVAILABLE"


def test_failed_conjunct_is_not_repaired_from_another_conjunct():
    missing = _c(
        "FREEZE_ID",
        expected="freeze-1",
        observed="",
        state=EvidenceState.MISSING,
    )
    sibling = _c(
        "OTHER_FIELD",
        expected="freeze-1",
        observed="freeze-1",
        state=EvidenceState.COMPLETE,
    )
    result = evaluate_admission(
        claim_class="SYNTHETIC_CLAIM",
        conjuncts=(missing, sibling),
        closed_state="UNAVAILABLE",
    )
    assert result.admitted is False
    assert [item.conjunct_id for item in result.failed_conjuncts] == ["FREEZE_ID"]
    solo = evaluate_conjunct(missing)
    assert solo is not None
    assert solo.observed == ""
    assert sibling.observed == "freeze-1"


def test_result_is_frozen():
    result = evaluate_admission(
        claim_class="SYNTHETIC_CLAIM",
        conjuncts=(_c("C1"),),
        closed_state="UNUSED_ON_SUCCESS",
    )
    assert isinstance(result, AdmissionResult)
    with pytest.raises(ValidationError):
        result.admitted = False
    assert result.admitted is True
    assert result.closed_state is None
