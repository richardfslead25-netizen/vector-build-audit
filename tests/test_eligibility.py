from datetime import date, datetime, timezone
from tests.helpers import make_contract
from vector.eligibility.gates import evaluate_eligibility
LISTED = {date(2026,9,25), date(2026,10,2)}
NOW = datetime(2026,9,15,16,5,tzinfo=timezone.utc)

def test_missing_greeks_or_quotes():
    c = make_contract(bid=None, ask=None, delta=None, gamma=None, theta=None, vega=None)
    v = evaluate_eligibility(c, now=NOW, listed_expirations=LISTED)
    assert "MISSING_QUOTES" in v and "MISSING_DELTA" in v and "MISSING_GAMMA" in v

def test_stale_chain_and_timestamp_mismatch():
    c = make_contract(quote_time=datetime(2026,9,14,10,tzinfo=timezone.utc), greeks_time=datetime(2026,9,15,16,tzinfo=timezone.utc))
    v = evaluate_eligibility(c, now=NOW, listed_expirations=LISTED)
    assert "STALE_CHAIN" in v and "TIMESTAMP_MISMATCH" in v

def test_incorrect_contract_identity():
    c = make_contract(underlying="QQQ", occ_symbol="ZZZ999999C00000000")
    assert "CONTRACT_IDENTITY_MISMATCH" in evaluate_eligibility(c, now=NOW, listed_expirations=LISTED)

def test_negative_put_delta_uses_absolute_value():
    c = make_contract(right="P", occ_symbol="SPY260925P00580000", delta=-0.44)
    assert c.abs_delta == 0.44
    assert "MISSING_DELTA" not in evaluate_eligibility(c, now=NOW, listed_expirations=LISTED)

def test_spread_veto_and_zero_bid():
    assert "SPREAD_GT_15PCT" in evaluate_eligibility(make_contract(bid=1.0, ask=1.4), now=NOW, listed_expirations=LISTED)
    assert "ZERO_BID" in evaluate_eligibility(make_contract(bid=0.0, ask=1.2), now=NOW, listed_expirations=LISTED)

def test_dte_out_of_range_and_unlisted():
    assert "DTE_OUT_OF_RANGE" in evaluate_eligibility(make_contract(dte=5, expiration=date(2026,9,18)), now=NOW, listed_expirations=LISTED)
    assert "UNLISTED_EXPIRATION" in evaluate_eligibility(make_contract(expiration=date(2026,9,24), dte=17), now=NOW, listed_expirations=LISTED)

def test_premarket_without_live_chain():
    v = evaluate_eligibility(None, now=NOW, listed_expirations=LISTED, premarket_without_live_chain=True)
    assert "PREMARKET_NO_LIVE_CHAIN" in v and "MISSING_CONTRACT" in v
