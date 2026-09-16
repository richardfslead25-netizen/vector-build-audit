from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from vector.contracts.enums import DataStatus

class Provenance(BaseModel):
    provider: str
    dataset: str
    instrument: str
    units: str = "1"
    observation_time: datetime | None = None
    retrieval_time: datetime | None = None
    timezone: str = "America/New_York"
    data_status: DataStatus = DataStatus.UNKNOWN
    permitted_use: str = "research-only"
    entitlement: str = "unverified"
    transformation_version: str = "raw"
    lineage: str = ""
    notes: str = ""
    synthetic: bool = Field(default=False)

    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)
