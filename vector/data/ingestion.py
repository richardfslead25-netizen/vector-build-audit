"""Stage 1 market-data boundary. No live provider. No broker orders."""

from __future__ import annotations

import os
from typing import Any

from vector.config import APPROVED_ENTITLEMENT, VECTOR_STAGE
from vector.contracts.market import MarketSnapshot
from vector.contracts.options import OptionContract
from vector.contracts.provenance import Provenance


class LiveIngestionBlocked(RuntimeError):
    """Raised when Stage 1 code is asked to touch a live market-data or order API."""


class OfflineMarketSource:
    """Fixture-only source. Stage 2 may replace this after entitlement is confirmed."""

    PROVIDER_CANDIDATE = "webull"
    ORDERS_FORBIDDEN = True
    SAGE_WRITES_FORBIDDEN = True

    def __init__(self, *, entitlement: str = "unverified") -> None:
        self.entitlement = entitlement
        self.offline = os.environ.get("VECTOR_OFFLINE", "1") == "1"
        self.stage = os.environ.get("VECTOR_STAGE", VECTOR_STAGE)

    def fetch_quote(self, *_args: Any, **_kwargs: Any) -> MarketSnapshot:
        raise LiveIngestionBlocked(
            "Stage 1 has no live market-data client. App subscription is not programmatic access."
        )

    def fetch_chain(self, *_args: Any, **_kwargs: Any) -> list[OptionContract]:
        raise LiveIngestionBlocked("Stage 1 cannot pull live option chains")

    def submit_order(self, *_args: Any, **_kwargs: Any) -> None:
        raise LiveIngestionBlocked("VECTOR Stage 1 cannot submit paper or live orders")

    def accept_snapshot(
        self,
        market: MarketSnapshot,
        contracts: list[OptionContract],
        provenance: Provenance,
    ) -> tuple[MarketSnapshot, list[OptionContract]]:
        if self.stage != "1":
            raise LiveIngestionBlocked(f"VECTOR_STAGE={self.stage!r} is not an approved Stage 1 state")
        if not provenance.synthetic:
            raise LiveIngestionBlocked("Stage 1 accepts labeled synthetic snapshots only")
        if provenance.entitlement != APPROVED_ENTITLEMENT:
            raise LiveIngestionBlocked(
                f"entitlement {provenance.entitlement!r} is not {APPROVED_ENTITLEMENT}"
            )
        if provenance.data_status.value not in {"SYNTHETIC"}:
            raise LiveIngestionBlocked("non-synthetic data_status cannot enter Stage 1 scoring")
        return market, contracts
