from __future__ import annotations

from vector.config import DEFAULT_SETTINGS, Settings
from vector.contracts.enums import OptionRight
from vector.contracts.options import OptionContract, ScenarioResult
from vector.contracts.packet import Thesis


def scenarios_available(contract: OptionContract | None, spot: float | None) -> bool:
    if contract is None or spot is None or spot <= 0:
        return False
    required = (contract.mid, contract.delta, contract.gamma, contract.theta, contract.vega, contract.iv)
    return all(value is not None for value in required)


def estimate_scenarios(contract: OptionContract, spot: float, settings: Settings | None = None):
    if not scenarios_available(contract, spot):
        return []
    cfg = (settings or DEFAULT_SETTINGS).scenarios
    mid = contract.mid or 0.0
    results = []
    for ds in cfg.spot_moves:
        for days in cfg.days_elapsed:
            for div in cfg.iv_moves:
                d_spot = spot * ds
                est = (
                    mid
                    + contract.delta * d_spot
                    + 0.5 * contract.gamma * d_spot * d_spot
                    + contract.theta * days
                    + contract.vega * (contract.iv * div)
                )
                est = max(est, 0.0)
                half_spread = (contract.spread / 2.0) if cfg.use_quoted_half_spread and contract.spread is not None else mid * cfg.fallback_slippage_pct_of_mid
                entry = mid + half_spread + cfg.commission_per_contract / contract.multiplier
                exit_px = max(est - half_spread, 0.0)
                pnl = (exit_px - entry) * contract.multiplier - cfg.commission_per_contract
                results.append(ScenarioResult(
                    spot_move=ds,
                    days_elapsed=days,
                    iv_move=div,
                    estimated_value=round(est, 4),
                    pnl_per_contract=round(pnl, 2),
                    notes=f"{cfg.pricing_method}; {cfg.iv_unit}; local approximation; not a probability",
                ))
    return results


def scenarios_support_thesis(
    contract: OptionContract,
    spot: float,
    right: OptionRight,
    settings: Settings | None = None,
    thesis: Thesis | None = None,
) -> bool | None:
    if not scenarios_available(contract, spot):
        return None
    rows = estimate_scenarios(contract, spot, settings)
    if not rows:
        return None
    if thesis and thesis.target_price is not None and spot > 0:
        target_move = (thesis.target_price - spot) / spot
        horizon = thesis.horizon_sessions if thesis.horizon_sessions is not None else 7
    else:
        target_move = 0.04 if right is OptionRight.CALL else -0.04
        horizon = 7
    nearest = min(
        rows,
        key=lambda row: abs(row.spot_move - target_move) + abs(row.days_elapsed - horizon) + abs(row.iv_move),
    )
    if abs(nearest.spot_move - target_move) > 0.021:
        return False
    return bool(nearest.pnl_per_contract is not None and nearest.pnl_per_contract > 0)
