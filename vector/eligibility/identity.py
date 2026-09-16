"""OCC / OSI identity parsing. Do not treat substring membership as identity."""

from __future__ import annotations

import re
from datetime import date

from vector.contracts.enums import OptionRight
from vector.contracts.options import OptionContract

OCC_RE = re.compile(r"^([A-Z]{1,6})(\d{6})([CP])(\d{8})$")


def compact_occ(symbol: str) -> str:
    return symbol.replace(" ", "").upper()


def parse_occ_symbol(symbol: str) -> dict[str, object] | None:
    match = OCC_RE.fullmatch(compact_occ(symbol))
    if not match:
        return None
    root, yymmdd, right, strike_raw = match.groups()
    year = 2000 + int(yymmdd[0:2])
    month = int(yymmdd[2:4])
    day = int(yymmdd[4:6])
    try:
        expiration = date(year, month, day)
    except ValueError:
        return None
    return {
        "underlying": root,
        "expiration": expiration,
        "right": OptionRight.CALL if right == "C" else OptionRight.PUT,
        "strike": int(strike_raw) / 1000.0,
    }


def contract_matches_occ(contract: OptionContract) -> list[str]:
    parsed = parse_occ_symbol(contract.occ_symbol)
    vetoes: list[str] = []
    if parsed is None:
        return ["CONTRACT_IDENTITY_UNPARSEABLE"]
    if parsed["underlying"] != compact_occ(contract.underlying):
        vetoes.append("CONTRACT_UNDERLYING_MISMATCH")
    if parsed["right"] != contract.right:
        vetoes.append("CONTRACT_RIGHT_MISMATCH")
    if parsed["expiration"] != contract.expiration:
        vetoes.append("CONTRACT_EXPIRY_MISMATCH")
    if abs(float(parsed["strike"]) - contract.strike) > 1e-6:
        vetoes.append("CONTRACT_STRIKE_MISMATCH")
    return vetoes
