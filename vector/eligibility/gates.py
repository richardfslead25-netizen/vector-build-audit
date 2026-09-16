"""Hard eligibility gates. A high score cannot override a veto."""

from __future__ import annotations

from datetime import datetime, timezone

from vector.config import DEFAULT_SETTINGS, Settings
from vector.contracts.enums import QuoteQuality
from vector.contracts.options import OptionContract
from vector.features.expiration import classify_dte_band, is_end_of_week_expiration


def classify_quote(contract: OptionContract, settings: Settings) -> QuoteQuality:
    if contract.bid is None or contract.ask is None:
        return QuoteQuality.INCOMPLETE
    if not _finite(contract.bid) or not _finite(contract.ask):
        return QuoteQuality.MALFORMED
    if contract.bid == 0 and settings.universe.exclude_zero_bid:
        return QuoteQuality.ZERO_BID
    if contract.bid > contract.ask:
        return QuoteQuality.CROSSED
    mid = (contract.bid + contract.ask) / 2.0
    if mid == 0:
        return QuoteQuality.ZERO_MID
    return QuoteQuality.OK


def evaluate_eligibility(
    contract: OptionContract | None,
    *,
    now: datetime | None = None,
    listed_expirations: set | None = None,
    settings: Settings | None = None,
    premarket_without_live_chain: bool = False,
) -> list[str]:
    cfg = settings or DEFAULT_SETTINGS
    vetoes: list[str] = []
    now = now or datetime.now(timezone.utc)
    if premarket_without_live_chain:
        vetoes.append("PREMARKET_NO_LIVE_CHAIN")
    if contract is None:
        vetoes.append("MISSING_CONTRACT")
        return vetoes
    if classify_dte_band(contract.dte, cfg.universe).value == "OUT_OF_RANGE":
        vetoes.append("DTE_OUT_OF_RANGE")
    if cfg.universe.require_end_of_week and not is_end_of_week_expiration(contract.expiration):
        vetoes.append("NOT_END_OF_WEEK")
    if listed_expirations is not None and contract.expiration not in listed_expirations:
        vetoes.append("UNLISTED_EXPIRATION")
    quality = classify_quote(contract, cfg)
    contract.quote_quality = quality
    mapping = {
        QuoteQuality.INCOMPLETE: "MISSING_QUOTES",
        QuoteQuality.CROSSED: "CROSSED_QUOTES",
        QuoteQuality.ZERO_BID: "ZERO_BID",
        QuoteQuality.ZERO_MID: "ZERO_MID",
        QuoteQuality.MALFORMED: "MALFORMED_QUOTES",
    }
    if quality in mapping:
        vetoes.append(mapping[quality])
    if contract.spread_pct is not None and contract.spread_pct > cfg.universe.spread_veto_pct_of_mid:
        vetoes.append("SPREAD_GT_15PCT")
    if contract.open_interest is None:
        vetoes.append("MISSING_OPEN_INTEREST")
    elif contract.open_interest < cfg.universe.min_open_interest:
        vetoes.append("OI_BELOW_MINIMUM")
    for field in ("delta", "gamma", "theta", "vega"):
        if getattr(contract, field) is None:
            vetoes.append(f"MISSING_{field.upper()}")
    if contract.quote_time is not None:
        qt = contract.quote_time if contract.quote_time.tzinfo else contract.quote_time.replace(tzinfo=timezone.utc)
        if now - qt > cfg.freshness.chain_max_age:
            vetoes.append("STALE_CHAIN")
            contract.quote_quality = QuoteQuality.STALE
    if contract.greeks_time is not None and contract.quote_time is not None:
        gt = contract.greeks_time if contract.greeks_time.tzinfo else contract.greeks_time.replace(tzinfo=timezone.utc)
        qt = contract.quote_time if contract.quote_time.tzinfo else contract.quote_time.replace(tzinfo=timezone.utc)
        if abs((gt - qt).total_seconds()) > cfg.freshness.cross_input_tolerance.total_seconds():
            vetoes.append("TIMESTAMP_MISMATCH")
    if contract.adjusted and cfg.universe.exclude_adjusted_contracts:
        vetoes.append("ADJUSTED_CONTRACT")
    if contract.nonstandard_deliverable:
        vetoes.append("NONSTANDARD_DELIVERABLE")
    if contract.multiplier != cfg.universe.standard_multiplier:
        vetoes.append("UNSUPPORTED_MULTIPLIER")
    compact = contract.occ_symbol.replace(" ", "")
    if contract.underlying not in compact:
        vetoes.append("CONTRACT_IDENTITY_MISMATCH")
    return vetoes


def _finite(value: float) -> bool:
    return value == value and value not in (float("inf"), float("-inf"))
