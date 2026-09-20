"""OCC / OSI identity parsing. Do not treat substring membership as identity.

Preferred order:
1. Compact ASCII spaces and uppercase. Tabs, newlines, and other whitespace are not padding.
2. If the compact string matches OSI shape, slice root / YYMMDD / right / mills.
3. Otherwise reverse-parse: strike (8) + right (1) + YYMMDD (6) + root remainder.
4. Reject invalid calendar dates, rights other than C/P, non-positive strikes,
   roots longer than six, hyphen or slash roots, and years outside 2000-2099.

Locked Stage 1 rules:
- Hyphen and slash are not normalized to dot or removed. BRK-B and BRK/B do not become BRK.B or BRKB.
- OSI root is compared exactly to the contract underlying after space-compact. SPX is not SPXW.
- YY is 2000 + yy only. format_occ_symbol refuses years outside 2000-2099 rather than wrapping 1999 to 99.
"""

from __future__ import annotations

import re
from datetime import date

from vector.contracts.enums import OptionRight
from vector.contracts.options import OptionContract

# Compact OSI after ASCII spaces removed. Root may include digits (SPXW, RUTW).
# Dot is allowed in the root. Hyphen and slash are not.
COMPACT_OSI_RE = re.compile(r"^([A-Z0-9.]{1,6})(\d{6})([CP])(\d{8})$")
PADDED_TAIL_RE = re.compile(r"^(\d{6})([CP])(\d{8})$")
MAX_ROOT_LEN = 6
STRIKE_MILLS = 1000.0
OSI_YEAR_MIN = 2000
OSI_YEAR_MAX = 2099


def compact_occ(symbol: str) -> str:
    return symbol.replace(" ", "").upper()


def pad_osi_symbol(symbol: str) -> str | None:
    """Return a 21-character OSI record only when the compact form is a valid identity."""
    compact = compact_occ(symbol)
    match = COMPACT_OSI_RE.fullmatch(compact)
    if not match:
        return None
    root, yymmdd, right, strike_raw = match.groups()
    assembled = _assemble(root, yymmdd, right, strike_raw)
    if assembled is None:
        return None
    return str(assembled["osi_padded"])


def format_occ_symbol(
    root: str,
    expiration: date,
    right: OptionRight | str,
    strike: float,
    *,
    padded: bool = False,
) -> str | None:
    """Rebuild an OSI symbol. Returns None instead of inventing an invalid record."""
    compact_root = compact_occ(root)
    if not compact_root or len(compact_root) > MAX_ROOT_LEN:
        return None
    if not re.fullmatch(r"[A-Z0-9.]+", compact_root):
        return None
    if any(token in compact_root for token in "-/"):
        return None
    if expiration.year < OSI_YEAR_MIN or expiration.year > OSI_YEAR_MAX:
        return None
    if strike is None or strike <= 0:
        return None
    mills = int(round(float(strike) * STRIKE_MILLS))
    if mills <= 0 or mills > 99_999_999:
        return None
    right_token = right.value if isinstance(right, OptionRight) else str(right).upper()
    if right_token not in {"C", "P"}:
        return None
    yymmdd = f"{expiration.year % 100:02d}{expiration.month:02d}{expiration.day:02d}"
    body = f"{compact_root}{yymmdd}{right_token}{mills:08d}"
    if padded:
        return f"{compact_root:<6}{yymmdd}{right_token}{mills:08d}"
    return body


def parse_occ_symbol(symbol: str) -> dict[str, object] | None:
    if symbol is None:
        return None
    raw = symbol.upper()
    padded = pad_osi_symbol(raw)
    if padded is not None:
        return _fields_from_padded(padded)
    compact = compact_occ(raw)
    return _fields_from_reverse(compact)


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


def _fields_from_padded(padded: str) -> dict[str, object] | None:
    if len(padded) != 21:
        return None
    root = padded[0:6].rstrip()
    tail = padded[6:21]
    match = PADDED_TAIL_RE.fullmatch(tail)
    if not match:
        return None
    yymmdd, right, strike_raw = match.groups()
    return _assemble(root, yymmdd, right, strike_raw)


def _fields_from_reverse(compact: str) -> dict[str, object] | None:
    if len(compact) < 15 or len(compact) > 21:
        return None
    strike_raw = compact[-8:]
    right = compact[-9:-8]
    yymmdd = compact[-15:-9]
    root = compact[:-15]
    if not root or len(root) > MAX_ROOT_LEN:
        return None
    if not re.fullmatch(r"[A-Z0-9.]+", root):
        return None
    if not yymmdd.isdigit() or not strike_raw.isdigit() or right not in {"C", "P"}:
        return None
    return _assemble(root, yymmdd, right, strike_raw)


def _assemble(root: str, yymmdd: str, right: str, strike_raw: str) -> dict[str, object] | None:
    expiration = _parse_yymmdd(yymmdd)
    if expiration is None:
        return None
    strike = int(strike_raw) / STRIKE_MILLS
    if strike <= 0:
        return None
    return {
        "underlying": root,
        "expiration": expiration,
        "right": OptionRight.CALL if right == "C" else OptionRight.PUT,
        "strike": strike,
        "osi_padded": f"{root:<6}{yymmdd}{right}{strike_raw}",
        "osi_compact": f"{root}{yymmdd}{right}{strike_raw}",
    }


def _parse_yymmdd(yymmdd: str) -> date | None:
    if len(yymmdd) != 6 or not yymmdd.isdigit():
        return None
    year = 2000 + int(yymmdd[0:2])
    month = int(yymmdd[2:4])
    day = int(yymmdd[4:6])
    if year < OSI_YEAR_MIN or year > OSI_YEAR_MAX:
        return None
    try:
        return date(year, month, day)
    except ValueError:
        return None
