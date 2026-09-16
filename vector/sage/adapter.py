"""Read-only SAGE context adapter. VECTOR never writes to SAGE."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from vector.config import (
    DEFAULT_SETTINGS,
    SAGE_ALLOWED_SOURCES,
    SAGE_REQUIRED_ESTABLISHED_FIELDS,
    Settings,
)
from vector.contracts.enums import AlignmentState, DataStatus, OperatingMode, SageStatus
from vector.contracts.provenance import Provenance
from vector.contracts.sage import SageContext, SageUpstreamFields


class SageWriteError(RuntimeError):
    """Raised if any caller attempts a write path into SAGE."""


class SageReadOnlyAdapter:
    WRITE_FORBIDDEN = True

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or DEFAULT_SETTINGS

    def write(self, *_args: Any, **_kwargs: Any) -> None:
        raise SageWriteError("VECTOR has no write path into SAGE")

    def update_posterior(self, *_args: Any, **_kwargs: Any) -> None:
        raise SageWriteError("VECTOR cannot adjust SAGE posterior")

    def mint_regime(self, *_args: Any, **_kwargs: Any) -> None:
        raise SageWriteError("VECTOR cannot mint a SAGE regime")

    def ingest(
        self,
        payload: Mapping[str, Any] | None,
        *,
        now: datetime | None = None,
        observed_direction: str | None = None,
        transmission_observed: bool = False,
        source_claimed: str = "SAGE",
    ) -> SageContext:
        now = now or datetime.now(timezone.utc)
        if payload is None:
            return SageContext(
                status=SageStatus.UNAVAILABLE,
                alignment=AlignmentState.INSUFFICIENT,
                operating_mode=OperatingMode.BEHAVIOR_ONLY,
                reason="no usable upstream response",
                freeze_count_reported=None,
                freeze_count_invented=False,
            )

        claimed = str(payload.get("source_identity") or payload.get("source") or source_claimed)
        if claimed.upper() == "SIGIL" or payload.get("legacy_sigil") is True:
            return SageContext(
                status=SageStatus.UNAVAILABLE,
                alignment=AlignmentState.INSUFFICIENT,
                operating_mode=OperatingMode.BEHAVIOR_ONLY,
                upstream=SageUpstreamFields(
                    source_identity=claimed,
                    schema_version=payload.get("schema_version"),
                ),
                reason="SIGIL payload isolated; does not confer SAGE confirmation",
                freeze_count_reported=None,
                freeze_count_invented=False,
            )

        try:
            upstream = self._parse_upstream(payload)
        except ValueError as exc:
            return SageContext(
                status=SageStatus.INVALID,
                alignment=AlignmentState.INSUFFICIENT,
                operating_mode=OperatingMode.BEHAVIOR_ONLY,
                reason=f"invalid SAGE contract: {exc}",
                freeze_count_reported=None,
                freeze_count_invented=False,
            )

        status_text = (upstream.status_text or "").upper()
        established_flag = upstream.established

        if status_text == "UNAVAILABLE" and not established_flag:
            return SageContext(
                status=SageStatus.UNAVAILABLE,
                alignment=AlignmentState.INSUFFICIENT,
                operating_mode=OperatingMode.BEHAVIOR_ONLY,
                upstream=upstream,
                reason="upstream reports unavailable",
                freeze_count_reported=None,
                freeze_count_invented=False,
            )

        if status_text == "NOT_ESTABLISHED" or established_flag is False:
            return SageContext(
                status=SageStatus.NOT_ESTABLISHED,
                alignment=AlignmentState.INSUFFICIENT,
                operating_mode=OperatingMode.BEHAVIOR_ONLY,
                upstream=upstream,
                reason="upstream explicitly reports no established regime",
                freeze_count_reported=upstream.official_freeze_count,
                freeze_count_invented=False,
            )

        if established_flag is True:
            return self._handle_established_claim(payload, upstream, now)

        if not upstream.regime:
            return SageContext(
                status=SageStatus.INVALID,
                alignment=AlignmentState.INSUFFICIENT,
                operating_mode=OperatingMode.BEHAVIOR_ONLY,
                upstream=upstream,
                reason="no established regime field on payload",
                freeze_count_reported=upstream.official_freeze_count,
                freeze_count_invented=False,
            )

        return SageContext(
            status=SageStatus.INVALID,
            alignment=AlignmentState.INSUFFICIENT,
            operating_mode=OperatingMode.BEHAVIOR_ONLY,
            upstream=upstream,
            reason="payload failed ESTABLISHED contract",
            freeze_count_reported=upstream.official_freeze_count,
            freeze_count_invented=False,
        )

    def _handle_established_claim(
        self,
        payload: Mapping[str, Any],
        upstream: SageUpstreamFields,
        now: datetime,
    ) -> SageContext:
        missing = [name for name in SAGE_REQUIRED_ESTABLISHED_FIELDS if not getattr(upstream, name)]
        source = (upstream.source_identity or "").upper()
        if source not in {s.upper() for s in SAGE_ALLOWED_SOURCES}:
            return SageContext(
                status=SageStatus.INVALID,
                alignment=AlignmentState.INSUFFICIENT,
                operating_mode=OperatingMode.BEHAVIOR_ONLY,
                upstream=upstream,
                reason=f"unknown or disallowed SAGE source_identity={upstream.source_identity!r}",
                freeze_count_reported=upstream.official_freeze_count,
                freeze_count_invented=False,
            )
        if missing:
            return SageContext(
                status=SageStatus.INVALID,
                alignment=AlignmentState.INSUFFICIENT,
                operating_mode=OperatingMode.BEHAVIOR_ONLY,
                upstream=upstream,
                reason=f"forged or incomplete ESTABLISHED claim; missing {missing}",
                freeze_count_reported=upstream.official_freeze_count,
                freeze_count_invented=False,
            )
        time_error = _timestamp_policy(upstream.cutoff, upstream.receipt_time, now)
        if time_error:
            return SageContext(
                status=SageStatus.INVALID,
                alignment=AlignmentState.INSUFFICIENT,
                operating_mode=OperatingMode.BEHAVIOR_ONLY,
                upstream=upstream,
                reason=time_error,
                freeze_count_reported=upstream.official_freeze_count,
                freeze_count_invented=False,
            )
        posterior_error = _posterior_policy(upstream.posterior)
        if posterior_error:
            return SageContext(
                status=SageStatus.INVALID,
                alignment=AlignmentState.INSUFFICIENT,
                operating_mode=OperatingMode.BEHAVIOR_ONLY,
                upstream=upstream,
                reason=posterior_error,
                freeze_count_reported=upstream.official_freeze_count,
                freeze_count_invented=False,
            )
        cutoff = _aware(upstream.cutoff)
        if cutoff is not None and now - cutoff > self.settings.freshness.sage_max_age:
            return SageContext(
                status=SageStatus.STALE,
                alignment=AlignmentState.INSUFFICIENT,
                operating_mode=OperatingMode.BEHAVIOR_ONLY,
                upstream=upstream,
                reason=f"SAGE cutoff older than {self.settings.freshness.sage_max_age}",
                freeze_count_reported=upstream.official_freeze_count,
                freeze_count_invented=False,
            )

        synthetic = bool(payload.get("synthetic") or payload.get("allow_research_established"))
        admission = self.settings.sage_informed_admission_enabled
        if not admission:
            return SageContext(
                status=SageStatus.ESTABLISHED,
                alignment=AlignmentState.INSUFFICIENT,
                operating_mode=OperatingMode.BEHAVIOR_ONLY,
                upstream=upstream,
                provenance=Provenance(
                    provider=source,
                    dataset="sage-freeze",
                    instrument="macro-regime",
                    observation_time=upstream.cutoff,
                    retrieval_time=upstream.receipt_time or now,
                    data_status=DataStatus.SYNTHETIC if synthetic else DataStatus.UNKNOWN,
                    synthetic=synthetic,
                ),
                reason="validated fields present but SAGE_INFORMED admission disabled pending agreed contract",
                freeze_count_reported=upstream.official_freeze_count,
                freeze_count_invented=False,
            )

        supplied_alignment = str(payload.get("alignment") or "").upper()
        alignment = AlignmentState.INSUFFICIENT
        if supplied_alignment in {s.value for s in AlignmentState}:
            alignment = AlignmentState(supplied_alignment)
        return SageContext(
            status=SageStatus.ESTABLISHED,
            alignment=alignment,
            operating_mode=OperatingMode.SAGE_INFORMED,
            upstream=upstream,
            provenance=Provenance(
                provider=source,
                dataset="sage-freeze",
                instrument="macro-regime",
                observation_time=upstream.cutoff,
                retrieval_time=upstream.receipt_time or now,
                data_status=DataStatus.UNKNOWN,
            ),
            reason="admission enabled; alignment taken only from explicit upstream field",
            freeze_count_reported=upstream.official_freeze_count,
            freeze_count_invented=False,
        )

    def _parse_upstream(self, payload: Mapping[str, Any]) -> SageUpstreamFields:
        extras = {
            k: v
            for k, v in payload.items()
            if k
            not in {
                "schema_version", "source_identity", "source", "cutoff", "receipt_time",
                "regime", "posterior", "persistence", "successors", "transition_stage",
                "freeze_identity", "official_freeze_count", "officialFreezeCount",
                "established", "status_text", "status", "legacy_sigil",
                "synthetic", "allow_research_established", "alignment",
            }
        }
        return SageUpstreamFields(
            schema_version=payload.get("schema_version"),
            source_identity=payload.get("source_identity") or payload.get("source"),
            cutoff=_as_dt(payload.get("cutoff")),
            receipt_time=_as_dt(payload.get("receipt_time")),
            regime=payload.get("regime"),
            posterior=payload.get("posterior"),
            persistence=payload.get("persistence"),
            successors=payload.get("successors"),
            transition_stage=payload.get("transition_stage"),
            freeze_identity=payload.get("freeze_identity"),
            official_freeze_count=payload.get("official_freeze_count", payload.get("officialFreezeCount")),
            established=payload.get("established"),
            status_text=payload.get("status_text") or payload.get("status"),
            **extras,
        )


def _as_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    raise ValueError(f"unsupported datetime: {value!r}")


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return None
    return value


def _timestamp_policy(cutoff: datetime | None, receipt: datetime | None, now: datetime) -> str | None:
    if cutoff is None or receipt is None:
        return "missing cutoff or receipt_time"
    if cutoff.tzinfo is None or receipt.tzinfo is None:
        return "naive SAGE timestamps rejected"
    if cutoff > now or receipt > now:
        return "future SAGE timestamp rejected"
    return None


def _posterior_policy(posterior: Any) -> str | None:
    if posterior is None:
        return "missing posterior distribution"
    if isinstance(posterior, (int, float)):
        return "malformed posterior: scalar is not a distribution"
    if not isinstance(posterior, dict) or not posterior:
        return "malformed posterior distribution"
    total = 0.0
    for key, value in posterior.items():
        try:
            number = float(value)
        except (TypeError, ValueError):
            return f"malformed posterior value for {key}"
        if number != number or number < 0:
            return f"malformed posterior value for {key}"
        total += number
    if total <= 0 or abs(total - 1.0) > 0.05:
        return f"malformed posterior: masses sum to {total}"
    return None
