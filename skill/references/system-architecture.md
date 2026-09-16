# System Architecture — SIGIL / SAGE / Behavior / Fusion / VECTOR

VECTOR is the options-expression layer. It does not mint regimes.

## Imagined full system

```text
SIGIL / SAGE          macro regime engine
        ↓ official freeze or explicit NOT_ESTABLISHED
Market-behavior engine    tape, vol, momentum, correlation, volume, options structure
        ↓
Fusion layer              consistent / inconsistent / insufficient
        ↓ confidence adjustment only — never a new regime
VECTOR                    contract expression
```

```text
macro regime != asset transmission != security expression != option expression
```

A Markov, ML, or Bayesian transition model may later estimate successor states. VECTOR does not run that model. VECTOR may read an official successor list. It may not invent one.

## SAGE contract (locked)

Sage shape is Bayesian. Sage computation is not live.

P(regime | evidence) = P(evidence | regime) P(regime) / P(evidence)

Sage would need a taxonomy of regime IDs, a prior P(R), a likelihood from six official pillars, a posterior that sums to 1, and decision rule ARGMAX_POSTERIOR with ties to NOT_ESTABLISHED.

What actually runs now:

- Current-regime inferencer is unimplemented and rejects.
- Pillar aggregation, persistence, and successors throw. They do not guess.
- Engine-access gate returns ok: false, regime: null, posterior: null.
- Reasons include INSUFFICIENT_EVIDENCE, LEGACY_SOURCE_UNRECOVERED, SOURCE_PAYLOAD_UNAVAILABLE.
- officialFreezeCount = 0.
- Charts, HTML, agent estimates, and tape are SUBSTITUTION_REJECTED. They cannot fill a pillar.

Honest SAGE output until Owner/ChatGPT authorizes a live inferencer:

```text
SAGE_STATUS = NOT_ESTABLISHED
POSTERIOR = null
CURRENT_REGIME = null
PERSISTENCE = null
SUCCESSORS = null
TRANSITION_STAGE = null
FREEZE = none
officialFreezeCount = 0
```

NOT_ESTABLISHED is the product, not a bug. Do not replace it with Risk-On, Tightening, bullish, bearish, or any catalog ID. The catalog of regime IDs is unresolved.

### Freeze fields (only if an official freeze is later minted)

- currentRegime or explicit notEstablished
- fullPosteriorDistribution that sums to 1
- selection rule ARGMAX_POSTERIOR
- tie-break NOT_ESTABLISHED
- leadingSuccessor as a label, not a trade

High current posterior must not hide transition evidence. Persistence and successors are separate models.

### Missing evidence

Missing WTI, HY OAS, MOVE, late H.4.1 / H.10, or empty/partial shadow observations make the likelihood undefined. Then the whole posterior is NOT_ESTABLISHED. Missing != last week. Missing != 0.5. Missing != neutral.

### Methods that fit Sage later (research only — do not run tonight)

1. Sequential Bayes on an unbroken official freeze chain.
2. Hierarchical Bayes across correlated pillars. Fused weighted mash-ups remain forbidden.
3. Dirichlet-categorical over a finite regime catalog.
4. HMM / switching for persistence, only on official freeze history.
5. Missing-not-at-random → refuse the posterior.

Methods that do not fit: imputing pillars from tape, charts-as-pillars, vibe regimes, silently turning on L04.

## SIGIL

If a timestamped SIGIL machine output is supplied, consume it as upstream context. Do not rewrite it. Do not treat it as strike selection. If SIGIL is absent, write SIGIL_UNAVAILABLE and continue.

## Market-behavior engine (VECTOR owns this layer)

Observe and stamp, never use to mint a regime: price structure, relative volume, momentum level vs acceleration, RS, RV vs IV, GEX/flip/walls, objective historical setups only.

## Fusion layer

| Fusion | Meaning | VECTOR effect |
|---|---|---|
| CONSISTENT | Tape transmits the official regime/catalyst path | Allow full macro-transmission points |
| INCONSISTENT | Tape contradicts official regime or dual-path is live | Cut macro points; keep tape-led setups; stamp the conflict |
| INSUFFICIENT | SAGE/SIGIL null, pillars missing, or transmission not established | Award zero SAGE-confirmation points; continue catalyst + structure |

If SAGE is NOT_ESTABLISHED, fusion cannot be CONSISTENT with a Sage regime. It can only be INSUFFICIENT at the regime layer.

## VECTOR expression stack

```text
regime/catalyst alignment
  -> technical break
  -> increasing relative volume
  -> momentum confirmation
  -> gamma-flip failure (run, not sweep)
  -> negative GEX
  -> open runway to next gamma/technical level
  -> liquid 0.35-0.50 delta weekly (14-45 DTE EOW)
```

0DTE scalp logic is not this stack. Horizon mismatch -> NO_TRADE.

## What VECTOR may never do

- Invent SAGE/SIGIL posteriors, persistence, successors, or freeze hashes.
- Fill pillars from charts, HTML, or tape.
- Treat a high tape score as a regime.
- Treat successor labels as trades.
- Turn on Bayesian/HMM computation inside this skill.
- Change Sage taxonomy, priors, or inferencer code.
