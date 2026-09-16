from __future__ import annotations

from enum import Enum

class SageStatus(str, Enum):
    UNAVAILABLE = "UNAVAILABLE"
    INVALID = "INVALID"
    STALE = "STALE"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    ESTABLISHED = "ESTABLISHED"

class AlignmentState(str, Enum):
    CONSISTENT = "CONSISTENT"
    INCONSISTENT = "INCONSISTENT"
    INSUFFICIENT = "INSUFFICIENT"

class OperatingMode(str, Enum):
    BEHAVIOR_ONLY = "BEHAVIOR_ONLY"
    SAGE_INFORMED = "SAGE_INFORMED"

class GammaVariant(str, Enum):
    GAMMA_CONFIRMED = "GAMMA_CONFIRMED"
    GAMMA_UNAVAILABLE = "GAMMA_UNAVAILABLE"

class GammaRegime(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEAR_FLIP = "NEAR_FLIP"
    GEX_NOT_PRINTABLE = "GEX_NOT_PRINTABLE"

class Direction(str, Enum):
    CALL = "CALL"
    PUT = "PUT"

class OptionRight(str, Enum):
    CALL = "C"
    PUT = "P"

class DteBand(str, Enum):
    DTE_14_21 = "14-21"
    DTE_22_35 = "22-35"
    DTE_36_45 = "36-45"
    OUT_OF_RANGE = "OUT_OF_RANGE"

class Grade(str, Enum):
    A_PLUS = "A_PLUS"
    A = "A"
    B_DEVELOPING = "B_DEVELOPING"
    WATCH = "WATCH"
    REJECT = "REJECT"

class Disposition(str, Enum):
    RESEARCH_ELIGIBLE = "RESEARCH_ELIGIBLE"
    WATCH = "WATCH"
    NO_TRADE = "NO_TRADE"
    REJECT = "REJECT"

class RedTeamVerdict(str, Enum):
    PROMOTE = "PROMOTE"
    REDUCE = "REDUCE"
    KILL = "KILL"
    OPPOSITE_PATH = "OPPOSITE_PATH"

class SweepRun(str, Enum):
    SWEEP = "SWEEP"
    RUN = "RUN"
    UNCLASSIFIED = "UNCLASSIFIED"

class DataStatus(str, Enum):
    REAL_TIME = "REAL_TIME"
    DELAYED = "DELAYED"
    HISTORICAL = "HISTORICAL"
    SYNTHETIC = "SYNTHETIC"
    UNKNOWN = "UNKNOWN"

class QuoteQuality(str, Enum):
    OK = "OK"
    CROSSED = "CROSSED"
    ZERO_BID = "ZERO_BID"
    ZERO_MID = "ZERO_MID"
    STALE = "STALE"
    INCOMPLETE = "INCOMPLETE"
    MALFORMED = "MALFORMED"
