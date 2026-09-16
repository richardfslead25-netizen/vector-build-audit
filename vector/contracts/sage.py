from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from vector.contracts.enums import AlignmentState, OperatingMode, SageStatus
from vector.contracts.provenance import Provenance

class SageUpstreamFields(BaseModel):
    model_config = ConfigDict(extra="allow")
    schema_version: str | None = None
    source_identity: str | None = None
    cutoff: datetime | None = None
    receipt_time: datetime | None = None
    regime: str | None = None
    posterior: dict[str, float] | float | None = None
    persistence: Any = None
    successors: Any = None
    transition_stage: Any = None
    freeze_identity: str | None = None
    official_freeze_count: int | None = None
    established: bool | None = None
    status_text: str | None = None

class SageContext(BaseModel):
    status: SageStatus
    alignment: AlignmentState
    operating_mode: OperatingMode
    upstream: SageUpstreamFields = Field(default_factory=SageUpstreamFields)
    provenance: Provenance | None = None
    reason: str = ""
    freeze_count_reported: int | None = None
    freeze_count_invented: bool = False
    claimed_established: bool = False
    verified_established: bool = False

    def as_public_dict(self) -> dict[str, Any]:
        payload = {
            "SAGE_STATUS": self.status.value,
            "ALIGNMENT": self.alignment.value,
            "OPERATING_MODE": self.operating_mode.value,
            "REASON": self.reason,
            "CLAIMED_ESTABLISHED": self.claimed_established,
            "VERIFIED_ESTABLISHED": self.verified_established,
            "CURRENT_REGIME": None,
            "POSTERIOR": None,
            "PERSISTENCE": None,
            "SUCCESSORS": None,
            "TRANSITION_STAGE": None,
            "FREEZE": None,
            "officialFreezeCount": None,
        }
        publish = (
            self.verified_established
            and self.status == SageStatus.ESTABLISHED
            and self.operating_mode == OperatingMode.SAGE_INFORMED
        )
        if publish:
            payload.update({
                "CURRENT_REGIME": self.upstream.regime,
                "POSTERIOR": self.upstream.posterior,
                "PERSISTENCE": self.upstream.persistence,
                "SUCCESSORS": self.upstream.successors,
                "TRANSITION_STAGE": self.upstream.transition_stage,
                "FREEZE": self.upstream.freeze_identity,
                "officialFreezeCount": self.upstream.official_freeze_count,
            })
        elif self.status in {SageStatus.NOT_ESTABLISHED, SageStatus.STALE, SageStatus.INVALID}:
            payload["officialFreezeCount"] = self.freeze_count_reported
        return payload
