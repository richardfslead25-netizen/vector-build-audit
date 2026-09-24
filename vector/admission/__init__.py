"""Provider-independent structured admission result.

This module does not implement official Sage freeze admission.
"""

from vector.admission.result import (
    AdmissionConjunct,
    AdmissionResult,
    EvidenceState,
    FailedConjunct,
    evaluate_admission,
)

__all__ = [
    "AdmissionConjunct",
    "AdmissionResult",
    "EvidenceState",
    "FailedConjunct",
    "evaluate_admission",
]
