
from __future__ import annotations
import json, sys
from datetime import date, datetime, timezone
from vector.board.render import render_board_markdown
from vector.contracts.enums import Direction
from tests.helpers import make_contract, make_market, make_thesis
from vector.pipeline import evaluate_candidate

def main():
    cutoff = datetime(2026,9,15,16,5,tzinfo=timezone.utc)
    listed = {date(2026,10,2), date(2026,10,9)}
    cases = [
        ("behavior_only_strong_tape", None, True, {}),
        ("gamma_unavailable", None, False, {}),
        ("high_score_spread_veto", None, True, {"bid":1.00,"ask":1.40}),
        ("stale_sage", {"source_identity":"SAGE","established":True,"regime":"risk-on","cutoff":"2026-08-01T00:00:00+00:00","official_freeze_count":3,"posterior":{"risk-on":0.7}}, True, {}),
    ]
    packets = []
    for name, sage, gamma_ok, extra in cases:
        market = make_market() if gamma_ok else make_market(gamma=None)
        packets.append(evaluate_candidate(
            ticker="SPY", direction=Direction.CALL, setup=name, market=market,
            contract=make_contract(**extra),
            alternatives=[
                make_contract(occ_symbol="SPY261002C00585000", strike=585.0, delta=0.38),
                make_contract(occ_symbol="SPY261009C00580000", strike=580.0, expiration=date(2026,10,9), dte=24, delta=0.40),
            ],
            thesis=make_thesis(), sage_payload=sage, listed_expirations=listed,
            cutoff=cutoff, run_id=f"demo-{name}",
        ))
    print(render_board_markdown(packets, cutoff=cutoff.isoformat(), run_id="demo-stage1"))
    print("FIXTURE_LABEL = SYNTHETIC")
    print("NETWORK_CALLS = 0")
    print("BROKER_ORDERS = 0")
    print(json.dumps([{"setup":p.setup,"mode":p.operating_mode.value,"sage":p.sage.status.value,
                       "score":p.score.raw_score,"grade":p.score.grade.value,"disposition":p.disposition.value,
                       "vetoes":p.vetoes,"freeze_count":p.sage.as_public_dict().get("officialFreezeCount"),
                       "authority":p.authority.model_dump()} for p in packets], indent=2))

if __name__ == "__main__":
    sys.exit(main())
