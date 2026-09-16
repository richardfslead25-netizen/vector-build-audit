"""Read-only SAGE context adapter. VECTOR never writes to SAGE."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from vector.config import DEFAULT_SETTINGS, Settings
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
        has_regime = bool(upstream.regime)

        if status_text == "UNAVAILABLE" and not has_regime:
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

        if not has_regime and established_flag is not True:
            return SageContext(
                status=SageStatus.INVALID,
                alignment=AlignmentState.INSUFFICIENT,
                operating_mode=OperatingMode.BEHAVIOR_ONLY,
                upstream=upstream,
                reason="no established regime field on payload",
                freeze_count_reported=upstream.official_freeze_count,
                freeze_count_invented=False,
            )

        if upstream.cutoff is not None:
            cutoff = upstream.cutoff
            if cutoff.tzinfo is None:
                cutoff = cutoff.replace(tzinfo=timezone.utc)
            if now - cutoff > self.settings.freshness.sage_max_age:
                return SageContext(
                    status=SageStatus.STALE,
                    alignment=AlignmentState.INSUFFICIENT,
                    operating_mode=OperatingMode.BEHAVIOR_ONLY,
                    upstream=upstream,
                    reason=f"SAGE cutoff older than {self.settings.freshness.sage_max_age}",
                    freeze_count_reported=upstream.official_freeze_count,
                    freeze_count_invented=False,
                )

        if established_flag is True and has_regime:
            alignment = self._align(upstream.regime, observed_direction, transmission_observed)
            return SageContext(
                status=SageStatus.ESTABLISHED,
                alignment=alignment,
                operating_mode=OperatingMode.SAGE_INFORMED,
                upstream=upstream,
                provenance=Provenance(
                    provider=claimed,
                    dataset="sage-freeze",
                    instrument="macro-regime",
                    observation_time=upstream.cutoff,
                    retrieval_time=upstream.receipt_time or now,
                    data_status=DataStatus.UNKNOWN,
                ),
                reason="validated established SAGE context",
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

    def _align(self, regime, observed_direction, transmission_observed) -> AlignmentState:
        if not regime or not observed_direction:
            return AlignmentState.INSUFFICIENT
        polarity = _regime_polarity(regime)
        if polarity is None or not transmission_observed:
            return AlignmentState.INSUFFICIENT
        if polarity == observed_direction:
            return AlignmentState.CONSISTENT
        return AlignmentState.INCONSISTENT


def _as_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    raise ValueError(f"unsupported datetime: {value!r}")


def _regime_polarity(regime: str) -> str | None:
    text = regime.lower()
    if any(t in text for t in ("risk-on", "risk_on", "ease", "easing", "expansion", "bull")):
        return "CALL"
    if any(t in text for t in ("risk-off", "risk_off", "tight", "tightening", "contraction", "bear")):
        return "PUT"
    return None
