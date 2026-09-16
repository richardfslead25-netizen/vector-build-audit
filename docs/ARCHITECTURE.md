# Stage 1 architecture

Stack: Python 3.12 + Pydantic v2 + pytest. Single process. No microservices. No broker SDK. No SAGE write client.

```text
SageReadOnlyAdapter
  -> OfflineMarketSource | supplied snapshot + provenance
  -> eligibility gates
  -> market-behavior features
  -> SAGE alignment (INSUFFICIENT unless ESTABLISHED)
  -> deterministic scoring (fixed DTE bands)
  -> scenario grid
  -> single-agent red team
  -> board render + append-only journal
```

Layers kept distinct:

| Layer | Stage 1 module |
|---|---|
| Read-only SAGE adapter | `vector/sage/adapter.py` |
| Market-data ingestion | `vector/data/ingestion.py` (live blocked) |
| Data quality / eligibility | `vector/eligibility/gates.py` |
| Market-behavior features | `vector/features/technical.py` |
| SAGE alignment | adapter `alignment` field |
| Contract selection / scenarios | `vector/scoring/scenarios.py` |
| Deterministic ranking | `vector/scoring/engine.py` |
| Red-team review | `vector/redteam/critique.py` |
| Board + journal | `vector/board/render.py`, `vector/journal/store.py` |

Modes: `BEHAVIOR_ONLY` / `SAGE_INFORMED`.
Gamma variants: `GAMMA_CONFIRMED` / `GAMMA_UNAVAILABLE`.
Authority defaults cannot be flipped by score, grade, or `PROMOTE`.
