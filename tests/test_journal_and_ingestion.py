from tests.helpers import make_contract, make_market, make_thesis
from vector.contracts.enums import DataStatus, Direction
from vector.contracts.provenance import Provenance
from vector.data.ingestion import LiveIngestionBlocked, OfflineMarketSource
from vector.journal.store import EvaluationJournal
from vector.pipeline import evaluate_candidate

def test_journal_is_append_only():
    packet = evaluate_candidate(
        ticker="SPY",
        direction=Direction.CALL,
        setup="journal",
        market=make_market(),
        contract=make_contract(),
        thesis=make_thesis(),
        sage_payload=None,
    )
    journal = EvaluationJournal()
    first = journal.append_packet(packet)
    second = journal.append_packet(packet)
    assert first.seq == 1 and second.seq == 2
    assert len(journal.entries) == 2
    try:
        journal.rewrite(seq=1, outcome="win")
        raise AssertionError("rewrite should have failed")
    except PermissionError:
        pass
    assert journal.entries[0].outcome is None
    assert journal.entries[0].authority["live_execution_enabled"] is False

def test_offline_source_blocks_live_and_orders():
    src = OfflineMarketSource(entitlement="not-connected")
    try:
        src.fetch_quote("SPY")
        raise AssertionError("live quote should be blocked")
    except LiveIngestionBlocked:
        pass
    try:
        src.fetch_chain("SPY")
        raise AssertionError("live chain should be blocked")
    except LiveIngestionBlocked:
        pass
    try:
        src.submit_order(symbol="SPY")
        raise AssertionError("order should be blocked")
    except LiveIngestionBlocked:
        pass

def test_offline_source_accepts_labeled_synthetic_only():
    src = OfflineMarketSource()
    market, contracts = src.accept_snapshot(
        make_market(),
        [make_contract()],
        Provenance(
            provider="synthetic-fixture",
            dataset="stage1-offline",
            instrument="SPY",
            data_status=DataStatus.SYNTHETIC,
            entitlement="stage1-synthetic-only",
            synthetic=True,
        ),
    )
    assert market.symbol == "SPY"
    assert contracts[0].underlying == "SPY"
    try:
        src.accept_snapshot(
            make_market(),
            [make_contract()],
            Provenance(
                provider="webull-proposed",
                dataset="option-chain",
                instrument="SPY",
                data_status=DataStatus.UNKNOWN,
                entitlement="unverified",
                synthetic=False,
            ),
        )
        raise AssertionError("unverified live snapshot should be blocked")
    except LiveIngestionBlocked:
        pass
