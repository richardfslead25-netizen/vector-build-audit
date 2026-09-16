"""Hard eligibility gates. A high score cannot override a veto."""

from __future__ import annotations

from datetime import date, datetime, timezone

from vector.config import DEFAULT_SETTINGS, Settings
from vector.contracts.enums import QuoteQuality
from vector.contracts.options import OptionContract
from vector.eligibility.identity import contract_matches_occ
from vector.features.expiration import calendar_dte, classify_dte_band, is_end_of_week_expiration


def classify_quote(contract: OptionContract, settings: Settings) -> QuoteQuality:
    if contract.bid is None or contract.ask is None:
        return QuoteQuality.INCOMPLETE
    if not _finite(contract.bid) or not _finite(contract.ask):
        return QuoteQuality.MALFORMED
    if contract.bid < 0 or contract.ask < 0:
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
    as_of_date: date | None = None,
) -> list[str]:
    cfg = settings or DEFAULT_SETTINGS
    vetoes: list[str] = []
    now = now or datetime.now(timezone.utc)
    session = as_of_date or now.date()
    if premarket_without_live_chain:
        vetoes.append("PREMARKET_NO_LIVE_CHAIN")
    if contract is None:
        vetoes.append("MISSING_CONTRACT")
        return vetoes
    if cfg.universe.require_listed_expirations and listed_expirations is None:
        vetoes.append("LISTINGS_UNAVAILABLE")
    derived_dte = calendar_dte(session, contract.expiration)
    if derived_dte != contract.dte:
        vetoes.append("DTE_MISMATCH")
    if classify_dte_band(derived_dte, cfg.universe).value == "OUT_OF_RANGE":
        vetoes.append("DTE_OUT_OF_RANGE")
    if cfg.universe.require_end_of_week and not is_end_of_week_expiration(contract.expiration):
        vetoes.append("NOT_END_OF_WEEK")
    if listed_expirations is not None and contract.expiration not in listed_expirations:
        vetoes.append("UNLISTED_EXPIRATION")
    quality = classify_quote(contract, cfg)
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
    for field in ("delta", "gamma", "theta", "vega", "iv"):
        value = getattr(contract, field)
        if value is None:
            vetoes.append(f"MISSING_{field.upper()}")
        elif not _finite(value):
            vetoes.append(f"NONFINITE_{field.upper()}")
    if contract.delta is not None and abs(contract.delta) > cfg.universe.max_abs_delta:
        vetoes.append("DELTA_OUT_OF_RANGE")
    if contract.iv is not None and (contract.iv <= 0 or contract.iv > cfg.universe.max_iv):
        vetoes.append("IV_OUT_OF_RANGE")
    if contract.strike <= cfg.universe.min_strike:
        vetoes.append("INVALID_STRIKE")
    if cfg.universe.require_quote_and_greeks_time:
        if contract.quote_time is None:
            vetoes.append("MISSING_QUOTE_TIME")
        if contract.greeks_time is None:
            vetoes.append("MISSING_GREEKS_TIME")
    for label, stamp in (("QUOTE", contract.quote_time), ("GREEKS", contract.greeks_time)):
        if stamp is None:
            continue
        if cfg.universe.reject_naive_timestamps and stamp.tzinfo is None:
            vetoes.append(f"NAIVE_{label}_TIMESTAMP")
            continue
        aware = stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)
        if cfg.universe.reject_future_timestamps and aware > now:
            vetoes.append(f"FUTURE_{label}_TIMESTAMP")
        max_age = cfg.freshness.chain_max_age if label == "QUOTE" else cfg.freshness.greeks_max_age
        if now - aware > max_age:
            vetoes.append("STALE_CHAIN" if label == "QUOTE" else "STALE_GREEKS")
    if contract.quote_time is not None and contract.greeks_time is not None:
        if contract.quote_time.tzinfo and contract.greeks_time.tzinfo:
            delta = abs((contract.greeks_time - contract.quote_time).total_seconds())
            if delta > cfg.freshness.cross_input_tolerance.total_seconds():
                vetoes.append("TIMESTAMP_MISMATCH")
    if contract.adjusted and cfg.universe.exclude_adjusted_contracts:
        vetoes.append("ADJUSTED_CONTRACT")
    if contract.nonstandard_deliverable:
        vetoes.append("NONSTANDARD_DELIVERABLE")
    if contract.multiplier != cfg.universe.standard_multiplier:
        vetoes.append("UNSUPPORTED_MULTIPLIER")
    vetoes.extend(contract_matches_occ(contract))
    return list(dict.fromkeys(vetoes))


def coherence_vetoes(*, ticker: str, direction, market, contract: OptionContract | None) -> list[str]:
    vetoes: list[str] = []
    if contract is None:
        return vetoes
    if ticker.upper() != contract.underlying.upper():
        vetoes.append("TICKER_CONTRACT_MISMATCH")
    if market is not None and market.symbol.upper() != contract.underlying.upper():
        vetoes.append("MARKET_CONTRACT_MISMATCH")
    if direction.value == "CALL" and contract.right.value != "C":
        vetoes.append("DIRECTION_RIGHT_MISMATCH")
    if direction.value == "PUT" and contract.right.value != "P":
        vetoes.append("DIRECTION_RIGHT_MISMATCH")
    if market is not None and market.gamma is not None and market.gamma.underlying.upper() != market.symbol.upper():
        vetoes.append("GAMMA_UNDERLYING_MISMATCH")
    if market is not None and market.features is not None and market.features.symbol.upper() != market.symbol.upper():
        vetoes.append("FEATURE_SYMBOL_MISMATCH")
    return vetoes


def _finite(value: float) -> bool:
    return value == value and value not in (float("inf"), float("-inf"))
