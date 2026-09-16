from datetime import date, datetime, timezone

from tests.helpers import make_contract
from vector.contracts.enums import OptionRight
from vector.eligibility.gates import evaluate_eligibility
from vector.eligibility.identity import (
    compact_occ,
    contract_matches_occ,
    format_occ_symbol,
    pad_osi_symbol,
    parse_occ_symbol,
)

NOW = datetime(2026, 9, 15, 16, 5, tzinfo=timezone.utc)
LISTED = {date(2026, 10, 2), date(2026, 10, 9)}


def test_compact_spy_parses_root_expiry_right_strike():
    parsed = parse_occ_symbol("SPY261002C00580000")
    assert parsed is not None
    assert parsed["underlying"] == "SPY"
    assert parsed["expiration"] == date(2026, 10, 2)
    assert parsed["right"] is OptionRight.CALL
    assert parsed["strike"] == 580.0
    assert parsed["osi_padded"] == "SPY   261002C00580000"


def test_padded_21_char_osi_parses():
    parsed = parse_occ_symbol("SPY   261002C00580000")
    assert parsed is not None
    assert parsed["underlying"] == "SPY"
    assert parsed["osi_compact"] == "SPY261002C00580000"


def test_digit_root_spxw_parses():
    parsed = parse_occ_symbol("SPXW261002P05800000")
    assert parsed is not None
    assert parsed["underlying"] == "SPXW"
    assert parsed["right"] is OptionRight.PUT
    assert parsed["strike"] == 5800.0


def test_fractional_strike_mills():
    parsed = parse_occ_symbol("LAMR150117C00052500")
    assert parsed is not None
    assert parsed["strike"] == 52.5
    assert parsed["expiration"] == date(2015, 1, 17)


def test_invalid_calendar_date_is_unparseable():
    assert parse_occ_symbol("SPY261331C00580000") is None


def test_zero_strike_is_unparseable():
    assert parse_occ_symbol("SPY261002C00000000") is None


def test_garbage_and_old_opra_codes_unparseable():
    assert parse_occ_symbol("ZZZ999999C00000000") is None
    assert parse_occ_symbol("SZVXI") is None
    assert parse_occ_symbol("") is None


def test_format_round_trip():
    built = format_occ_symbol("spy", date(2026, 10, 2), OptionRight.CALL, 580.0)
    assert built == "SPY261002C00580000"
    assert parse_occ_symbol(built)["strike"] == 580.0
    assert pad_osi_symbol(built) == "SPY   261002C00580000"


def test_contract_match_vetoes_each_field():
    good = make_contract()
    assert contract_matches_occ(good) == []
    assert "CONTRACT_RIGHT_MISMATCH" in contract_matches_occ(
        make_contract(occ_symbol="SPY261002P00580000")
    )
    assert "CONTRACT_STRIKE_MISMATCH" in contract_matches_occ(
        make_contract(occ_symbol="SPY261002C00585000")
    )
    assert "CONTRACT_EXPIRY_MISMATCH" in contract_matches_occ(
        make_contract(occ_symbol="SPY261009C00580000")
    )
    assert "CONTRACT_UNDERLYING_MISMATCH" in contract_matches_occ(
        make_contract(underlying="QQQ")
    )


def test_substring_is_not_identity():
    assert compact_occ("spy 261002c00580000") == "SPY261002C00580000"
    vetoes = evaluate_eligibility(
        make_contract(underlying="SPY", occ_symbol="NOTANOCC"),
        now=NOW,
        listed_expirations=LISTED,
    )
    assert "CONTRACT_IDENTITY_UNPARSEABLE" in vetoes
