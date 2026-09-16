from datetime import date
from vector.features.expiration import calendar_dte, classify_dte_band, expected_eow_date, is_end_of_week_expiration, prior_business_day
from vector.contracts.enums import DteBand

def test_holiday_adjusted_expiration_july_2026():
    assert prior_business_day(date(2026,7,3)) == date(2026,7,2)
    assert is_end_of_week_expiration(date(2026,7,2))
    assert not is_end_of_week_expiration(date(2026,7,3))

def test_normal_friday_is_eow():
    assert is_end_of_week_expiration(date(2026,9,25))
    assert not is_end_of_week_expiration(date(2026,9,24))

def test_expected_eow_from_midweek():
    assert expected_eow_date(date(2026,9,15)) == date(2026,9,18)

def test_fixed_dte_band_boundaries():
    assert classify_dte_band(13) is DteBand.OUT_OF_RANGE
    assert classify_dte_band(14) is DteBand.DTE_14_21
    assert classify_dte_band(21) is DteBand.DTE_14_21
    assert classify_dte_band(22) is DteBand.DTE_22_35
    assert classify_dte_band(35) is DteBand.DTE_22_35
    assert classify_dte_band(36) is DteBand.DTE_36_45
    assert classify_dte_band(45) is DteBand.DTE_36_45
    assert classify_dte_band(46) is DteBand.OUT_OF_RANGE

def test_calendar_dte():
    assert calendar_dte(date(2026,9,7), date(2026,9,25)) == 18
