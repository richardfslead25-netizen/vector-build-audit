"""Fail-closed discovery validation. No network. No Sage minting."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from vector.contracts.enums import AlignmentState, Grade, SageStatus
from vector.contracts.sage import SageContext
from vector.discovery.models import (
    COMMENTARY_STALE_AFTER,
    REGIME_TOKENS,
    CandidateDiscoveryRecord,
    DiscoveryDirection,
    DiscoveryStatus,
)


@dataclass(frozen=True)
class PromotionDecision:
    status: DiscoveryStatus
    vetoes: list[str]
    sage_relationship: AlignmentState
    official_freeze_ref: str | None
    promoted: bool


def derive_source_event_id(originating_note_id: str, publisher: str) -> str:
    key = f"{publisher.strip().upper()}|{originating_note_id.strip().upper()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def sage_relationship_for(sage: SageContext | None) -> AlignmentState:
    if sage is None:
        return AlignmentState.INSUFFICIENT
    verified = getattr(sage, "verified_established", False) is True
    if not verified:
        return AlignmentState.INSUFFICIENT
    if sage.status is not SageStatus.ESTABLISHED:
        return AlignmentState.INSUFFICIENT
    return sage.alignment


def _contains_regime_token(record: CandidateDiscoveryRecord) -> bool:
    blob = " ".join((record.stated_rationale, record.vector_inference, record.exposure_rationale))
    return any(re.search(rf"(?<![A-Z0-9-]){re.escape(token)}(?![A-Z0-9-])", blob.upper()) for token in REGIME_TOKENS)


def evaluate_discovery(
    record: CandidateDiscoveryRecord,
    *,
    now: datetime,
    sage: SageContext | None = None,
) -> PromotionDecision:
    vetoes: list[str] = []
    working = record.model_copy()

    if working.published_at is None:
        vetoes.append("MISSING_PUBLICATION_TIME")
    elif working.published_at.tzinfo is None:
        vetoes.append("NAIVE_PUBLICATION_TIMESTAMP")
    if working.retrieved_at is None:
        vetoes.append("MISSING_RETRIEVAL_TIME")
    elif working.retrieved_at.tzinfo is None:
        vetoes.append("NAIVE_RETRIEVAL_TIMESTAMP")
    if (
        working.published_at is not None
        and working.retrieved_at is not None
        and working.published_at.tzinfo
        and working.retrieved_at.tzinfo
        and working.retrieved_at < working.published_at
    ):
        vetoes.append("RETRIEVAL_BEFORE_PUBLICATION")

    if working.is_forecast() and not working.forecast_horizon:
        vetoes.append("MISSING_FORECAST_HORIZON")

    if working.published_at is not None and working.published_at.tzinfo:
        if now - working.published_at > COMMENTARY_STALE_AFTER:
            vetoes.append("STALE_COMMENTARY")

    if not working.exposure_supported or not working.exposure_rationale.strip():
        vetoes.append("UNSUPPORTED_EXPOSURE")

    if working.direction is DiscoveryDirection.NO_SETUP:
        vetoes.append("NO_SETUP")

    if working.status in {DiscoveryStatus.WITHDRAWN, DiscoveryStatus.SUPERSEDED}:
        vetoes.append(f"TERMINAL_{working.status.value}")

    if working.chain_available or working.gex_available:
        if working.synthetic is False:
            vetoes.append("NONSYNTHETIC_MARKET_CLAIM_FORBIDDEN")
        vetoes.append("MARKET_EVIDENCE_NOT_IN_DISCOVERY_SLICE")

    mentions = working.mentions_macro_tokens or _contains_regime_token(working)
    sage_rel = sage_relationship_for(sage)
    freeze_ref = None
    verified = bool(sage is not None and getattr(sage, "verified_established", False) is True)
    if verified and sage is not None and sage.upstream.freeze_identity:
        freeze_ref = sage.upstream.freeze_identity
    else:
        freeze_ref = None
        sage_rel = AlignmentState.INSUFFICIENT
    if mentions and sage_rel is AlignmentState.CONSISTENT:
        sage_rel = AlignmentState.INSUFFICIENT
        vetoes.append("COMMENTARY_CANNOT_MINT_SAGE")

    publication_ok = working.publication_verified and "MISSING_PUBLICATION_TIME" not in vetoes
    if not publication_ok:
        vetoes.append("PUBLICATION_UNVERIFIED")
    if not working.mechanism_verified:
        vetoes.append("MECHANISM_UNVERIFIED")
    if not working.transmission_observed:
        vetoes.append("TRANSMISSION_UNOBSERVED")

    can_promote = (
        publication_ok
        and working.mechanism_verified
        and working.transmission_observed
        and working.exposure_supported
        and working.direction is not DiscoveryDirection.NO_SETUP
        and working.status not in {DiscoveryStatus.WITHDRAWN, DiscoveryStatus.SUPERSEDED, DiscoveryStatus.REJECT}
        and not any(
            code in vetoes
            for code in {
                "MISSING_PUBLICATION_TIME",
                "NAIVE_PUBLICATION_TIMESTAMP",
                "MISSING_RETRIEVAL_TIME",
                "NAIVE_RETRIEVAL_TIMESTAMP",
                "RETRIEVAL_BEFORE_PUBLICATION",
                "MISSING_FORECAST_HORIZON",
                "STALE_COMMENTARY",
                "UNSUPPORTED_EXPOSURE",
                "MARKET_EVIDENCE_NOT_IN_DISCOVERY_SLICE",
                "COMMENTARY_CANNOT_MINT_SAGE",
                "TERMINAL_WITHDRAWN",
                "TERMINAL_SUPERSEDED",
            }
        )
    )

    if working.status is DiscoveryStatus.REJECT:
        status = DiscoveryStatus.REJECT
    elif working.status is DiscoveryStatus.WITHDRAWN:
        status = DiscoveryStatus.WITHDRAWN
    elif working.status is DiscoveryStatus.SUPERSEDED:
        status = DiscoveryStatus.SUPERSEDED
    elif working.direction is DiscoveryDirection.NO_SETUP:
        status = DiscoveryStatus.NO_SETUP
    elif can_promote:
        status = DiscoveryStatus.PROMOTED_TO_CATALYST_INTAKE
    elif "STALE_COMMENTARY" in vetoes:
        status = DiscoveryStatus.WATCH
    elif working.publication_verified and not working.mechanism_verified:
        status = DiscoveryStatus.UNVERIFIED
    elif publication_ok:
        status = DiscoveryStatus.WATCH
    else:
        status = DiscoveryStatus.CAPTURED

    return PromotionDecision(
        status=status,
        vetoes=list(dict.fromkeys(vetoes)),
        sage_relationship=sage_rel,
        official_freeze_ref=freeze_ref,
        promoted=status is DiscoveryStatus.PROMOTED_TO_CATALYST_INTAKE,
    )
