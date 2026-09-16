from __future__ import annotations
from vector.config import DEFAULT_SETTINGS, Settings
from vector.contracts.enums import OptionRight
from vector.contracts.options import OptionContract, ScenarioResult

def estimate_scenarios(contract: OptionContract, spot: float, settings: Settings | None = None):
    cfg = (settings or DEFAULT_SETTINGS).scenarios
    mid = contract.mid or 0.0
    results = []
    delta = contract.delta or 0.0
    gamma = contract.gamma or 0.0
    theta = contract.theta or 0.0
    vega = contract.vega or 0.0
    iv = contract.iv or 0.0
    for ds in cfg.spot_moves:
        for days in cfg.days_elapsed:
            for div in cfg.iv_moves:
                d_spot = spot * ds
                est = mid + delta * d_spot + 0.5 * gamma * d_spot * d_spot + theta * days + vega * (iv * div)
                est = max(est, 0.0)
                pnl = (est - mid) * contract.multiplier
                results.append(ScenarioResult(
                    spot_move=ds, days_elapsed=days, iv_move=div,
                    estimated_value=round(est, 4), pnl_per_contract=round(pnl, 2),
                    notes="greeks-taylor; not a probability",
                ))
    return results

def scenarios_support_thesis(contract, spot, right, settings=None) -> bool:
    rows = estimate_scenarios(contract, spot, settings)
    mid = contract.mid or 0.0
    slip = (settings or DEFAULT_SETTINGS).scenarios.slippage_pct_of_mid
    entry = mid * (1.0 + slip)
    target_move = 0.04 if right is OptionRight.CALL else -0.04
    for row in rows:
        if row.spot_move == target_move and row.days_elapsed == 7 and row.iv_move == 0.0:
            return bool(row.estimated_value is not None and row.estimated_value > entry)
    return False
