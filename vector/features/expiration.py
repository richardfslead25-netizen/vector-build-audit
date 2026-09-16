"""Holiday-adjusted end-of-week expiration rules."""
from __future__ import annotations
from datetime import date, timedelta
from vector.config import US_EQUITY_HOLIDAYS_2025_2027, UniverseConfig
from vector.contracts.enums import DteBand

def _is_holiday(d: date) -> bool:
    return d.isoformat() in US_EQUITY_HOLIDAYS_2025_2027

def is_business_day(d: date) -> bool:
    return d.weekday() < 5 and not _is_holiday(d)

def prior_business_day(d: date) -> date:
    cursor = d
    while not is_business_day(cursor):
        cursor -= timedelta(days=1)
    return cursor

def expected_eow_date(session: date) -> date:
    friday = session + timedelta(days=(4 - session.weekday()) % 7)
    return prior_business_day(friday)

def is_end_of_week_expiration(expiration: date) -> bool:
    friday = expiration + timedelta(days=(4 - expiration.weekday()) % 7)
    return expiration == prior_business_day(friday)

def calendar_dte(as_of: date, expiration: date) -> int:
    return (expiration - as_of).days

def classify_dte_band(dte: int, universe: UniverseConfig | None = None) -> DteBand:
    cfg = universe or UniverseConfig()
    if dte < cfg.min_dte or dte > cfg.max_dte:
        return DteBand.OUT_OF_RANGE
    if 14 <= dte <= 21:
        return DteBand.DTE_14_21
    if 22 <= dte <= 35:
        return DteBand.DTE_22_35
    return DteBand.DTE_36_45
