# Scoring, Contract Rules, and Packet Fields

## DTE-band scoring

Score every eligible candidate from 0–100. Use one fixed weight set for the candidate’s DTE band. Do not interpolate between bands.

- 14–21 DTE uses the 14–21 column only
- 22–35 DTE uses the 22–35 column only
- 36–45 DTE uses the 36–45 column only
- DTE outside 14–45 is a hard veto, not a scored band

Stage 1 `GAMMA_UNAVAILABLE` receives zero gamma points. Structure substitutes do not earn the gamma bucket.
Sage-confirmation points require verified_established, SAGE_INFORMED, and fusion CONSISTENT.
