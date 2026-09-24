# VECTOR — Basic Architecture Map

Date: 2026-09-24
Kind: ARCHITECTURE INVESTIGATION / DOCUMENTATION ONLY
Status: MAP COMPLETED. No implementation slice opened. No scoring, gate, Sage, broker, or persistence change.

```
VECTOR_ARCHITECTURE_MAP = COMPLETED
IMPLEMENTATION_AUTHORIZED = NO
NEXT_IMPLEMENTATION_SLICE = HOLD
REVIEW != APPROVAL != TRADE
```

This document maps VECTOR as evidenced by source and contracts. Intended-product language from skill references is cited only as SPECIFIED_ONLY.

State vocabulary used throughout:

- IMPLEMENTED
- PARTIAL_CODE
- SPECIFIED_ONLY
- NOT_IMPLEMENTED
- NOT_VERIFIED
- FORBIDDEN
- NOT_FOUND_IN_INSPECTED_SOURCES

---

## Inspection pins

| Object | Value |
|---|---|
| Primary repo | `richardfslead25-netizen/vector-build-audit` |
| Implementation branch | `build/stage-1-contracts` |
| Implementation HEAD inspected | `f7d24bb15044c6347aecd49f004db67159c07ed1` |
| Functional accepted runtime cited by last review | G1 handoff `5a463bdf1e768976b08516ac6f0ae6aebb6e33ed` |
| `main` HEAD inspected | `0b0d7c874bfcea960f83c9e8d7df9aa6db681327` |
| PR #1 | OPEN / HOLD — `build/stage-1-contracts` → `main` |
| PR #2 | OPEN / AUDIT ONLY — parallel momentum-scanner mailbox |
| PR #3 | OPEN / stale base `55dff75` — OCC rules already ported onto Stage 1 at `6c9a79c` |
| Bridge repo | `richardfslead25-netizen/sage-vector-bridge` |
| Bridge HEAD inspected | `2a3c0b93435bcbc47ef90485e3da8fa17e3a4f97` |
| Desk repo inspected (boundary only) | `richardfslead25-netizen/market-agent-desk` `main` `faa016199391ff8c9a02d0f9a25fb17af23d4baa` |
| BeeKeeper application repo | NOT REGISTERED / NOT_VERIFIED |

`main` is skill + coordination. Runtime code lives on `build/stage-1-contracts` and is not merged.

---

## 1. System purpose

**What VECTOR is (implemented identity).**  
VECTOR is a single-process Python 3.12 / Pydantic v2 / pytest research engine that evaluates supplied option-candidate snapshots into a `ResearchPacket`, score, disposition, markdown board row, and in-memory journal entry. It is not an embedding store, not a vector database, and not a trading system.

Evidence: `docs/ARCHITECTURE.md`; `vector/pipeline.py` `evaluate_candidate`; `README.md` Stage 1 section. Repo `vector-build-audit` / `build/stage-1-contracts` / `f7d24bb`.

**What VECTOR owns (current code + accepted offline path).**

- Typed research contracts (`vector/contracts/`)
- Read-only Sage payload classification (`vector/sage/adapter.py`)
- Offline/synthetic snapshot admission (`vector/data/ingestion.py`)
- Hard eligibility / OCC identity (`vector/eligibility/`)
- Deterministic feature formulas on supplied bars (`vector/features/`)
- Deterministic scoring and first-order scenario grid (`vector/scoring/`)
- Stage-1 red-team critique that cannot PROMOTE (`vector/redteam/critique.py`)
- Markdown board render (`vector/board/render.py`)
- In-memory append-only research log (`vector/journal/store.py`)
- Offline commentary → discovery record → G1 nomination (`vector/discovery/`)

**What VECTOR explicitly does not own.**

- Sage catalog, pillars, freeze minting, posterior, persistence, successors, transition stage
- BeeKeeper interpretation, durable history, or position management
- Broker accounts, order tickets, fills
- Official freeze count
- Live market-data entitlement

**Relationship to SAGE.**  
Downstream, read-only, optional. Absence of Sage does not block `BEHAVIOR_ONLY` scoring. VECTOR has explicit write-forbidden methods. Production `SAGE_INFORMED` admission is locked closed in config and is not reachable from adapter output.

Evidence: `vector/config.py` `SAGE_INFORMED_ADMISSION_ENABLED = False` and Settings validator; `vector/sage/adapter.py` `SageWriteError`; `sage-vector-bridge` `engine/HOW-VECTOR-MUST-CONSUME.md`; `mailbox/STATUS.md`.

**Relationship to BeeKeeper.**  
Specified future consumer of immutable published VECTOR artifacts. No BeeKeeper reader, publisher, or shared store exists in inspected VECTOR source. Bridge documents require BeeKeeper not to rescore, alter eligibility, change weights, trigger discovery, or trigger broker activity.

Evidence: `audits/2026-09-18-beekeeper-integration-handoff.md`; bridge `THREE-BUILD-OPERATING-MODEL.md`; bridge `beekeeper/2026-09-24-vector-journal-append-only-review.md`.

**Current execution authority.**

```
RESEARCH_ENABLED = true
PAPER_EXECUTION_ENABLED = false
LIVE_EXECUTION_ENABLED = false
LIVE_EXECUTION_AUTHORIZED = FALSE
```

A score, grade, or red-team verdict cannot enable paper or live execution. `evaluate_candidate` rewrites any packet that claims paper/live enabled back to `DEFAULT_AUTHORITY` and adds `EXECUTION_AUTHORITY_MUST_REMAIN_DISABLED`.

Evidence: `vector/config.py` `DEFAULT_AUTHORITY`; `vector/pipeline.py` authority clamp; `tests/test_pipeline_and_authority.py`.

---

## 2. Current runtime / data-flow map

The intended diagram in the task prompt and in `docs/ARCHITECTURE.md` is **not** the implemented call graph.

### Implemented Stage 1 research path

```text
caller-supplied objects
  MarketSnapshot (may already contain FeaturePacket / GammaSnapshot)
  OptionContract + alternatives
  Thesis
  sage_payload | None
  listed_expirations | None
        |
        v
vector/pipeline.py :: evaluate_candidate
        |
        +--> vector/sage/adapter.py :: SageReadOnlyAdapter.ingest
        |         always BEHAVIOR_ONLY + alignment INSUFFICIENT today
        |
        +--> vector/pipeline.py :: gamma_variant_of(market.gamma stamp)
        |
        +--> vector/eligibility/gates.py :: evaluate_eligibility
        |         + coherence_vetoes
        |         + nearby-strike / nearby-expiry freshness flags
        |         + thesis geometry / scenario availability vetoes
        |
        +--> vector/features/expiration.py :: calendar_dte / classify_dte_band
        |
        +--> vector/scoring/scenarios.py :: estimate_scenarios (if Greeks+mid+spot)
        |
        +--> vector/scoring/engine.py :: score_candidate
        |
        +--> assemble ResearchPacket
        |
        +--> authority clamp (paper/live forced false)
        |
        v
vector/redteam/critique.py :: critique
        |
        v
ResearchPacket  (disposition WATCH | NO_TRADE | REJECT)
        |
        +--> vector/board/render.py :: render_board_markdown   [optional caller]
        +--> vector/journal/store.py :: append_packet          [optional caller]
```

State: IMPLEMENTED for the boxes that exist as functions above. Demo entry: `vector/demo/run_stage1.py` builds synthetic fixtures via `tests/helpers.py` and prints markdown + JSON. NETWORK_CALLS = 0 by construction.

### Adjacent offline path (not wired into evaluate_candidate)

```text
CandidateDiscoveryRecord
        |
        v
vector/discovery/validate.py :: evaluate_discovery
        |
        v
vector/discovery/handoff.py :: handoff_to_g1
        |
        v
G1HandoffNomination  (catalyst_verified=False, score_points=0, no contract)
```

State: IMPLEMENTED as offline nomination. NOT_IMPLEMENTED as an automatic feed into scoring or the board.

### Boxes from the assumed diagram that are not inside evaluate_candidate

| Assumed box | Actual state |
|---|---|
| market-data adapter fetch | `OfflineMarketSource.fetch_quote` / `fetch_chain` raise `LiveIngestionBlocked`. Caller may optionally `accept_snapshot` first. PARTIAL_CODE / live FORBIDDEN |
| feature calculation | `compute_features` exists but is **not called** by `evaluate_candidate`. Scoring reads `market.features` if the caller already attached it. PARTIAL_CODE |
| Sage alignment assessment | Adapter always emits `INSUFFICIENT`. `observed_direction` and `transmission_observed` kwargs are accepted by pipeline and **ignored** by adapter. PARTIAL_CODE / alignment CONSISTENT path NOT_IMPLEMENTED |
| option-contract selection | No universe scanner. Caller supplies the contract. Nearby comparison is a gate on supplied alternatives, not a selector. PARTIAL_CODE |
| durable journal / BeeKeeper publish | NOT_IMPLEMENTED |

`ARCHITECTURE_DISCREPANCY = PRESENT` between `docs/ARCHITECTURE.md` flow ("features then alignment then scoring") and `vector/pipeline.py` (features not invoked; alignment never becomes CONSISTENT).

---

## 3. Module map

| Domain | Module/file | Responsibility | Current state |
|---|---|---|---|
| Contracts / enums | `vector/contracts/enums.py` `packet.py` `sage.py` `options.py` `market.py` `provenance.py` | Typed packets, thesis, score, Sage context, quotes, bars, GEX stamp | IMPLEMENTED |
| Configuration / authority | `vector/config.py` | Rules version, freshness, universe, DTE weights, Sage admission lock, authority defaults | IMPLEMENTED |
| Pipeline | `vector/pipeline.py` | Orchestrates one candidate evaluation | IMPLEMENTED |
| Market-data ingestion | `vector/data/ingestion.py` `OfflineMarketSource` | Block live fetch/orders; accept labeled synthetic snapshots only | PARTIAL_CODE (boundary only) |
| Sage adapter | `vector/sage/adapter.py` | Classify payload; never write; never admit SAGE_INFORMED | IMPLEMENTED (fail-closed subset) |
| Official freeze conjunction | bridge `engine/HOW-VECTOR-MUST-CONSUME.md` | Mailbox dump + ok + freeze id + count>0 + engineCommit pin + COMPLETE six pillars + lineage | SPECIFIED_ONLY |
| Eligibility | `vector/eligibility/gates.py` | Hard vetoes | IMPLEMENTED |
| OCC identity | `vector/eligibility/identity.py` | OSI parse; year 2000-2099; no hyphen/slash remap; SPX ≠ SPXW | IMPLEMENTED |
| Features | `vector/features/technical.py` | EMA/momentum/rvol/RS/RVol/sweep-run formulas | IMPLEMENTED as library; not pipeline-invoked |
| Expiration / DTE | `vector/features/expiration.py` | Calendar DTE, holiday-adjusted EOW, fixed bands | IMPLEMENTED |
| Scoring | `vector/scoring/engine.py` | Deterministic subfactors; no reweight | IMPLEMENTED |
| Scenarios | `vector/scoring/scenarios.py` | First-order Greeks Taylor grid | IMPLEMENTED (local approx) |
| Red team | `vector/redteam/critique.py` | Second pass; Stage 1 cannot PROMOTE | IMPLEMENTED |
| Option-contract selection | none | No scanner / no chain picker | NOT_IMPLEMENTED |
| Board render | `vector/board/render.py` | Markdown table + authority declaration | IMPLEMENTED |
| Board template | `skill/assets/DAILY-OPTIONS-OPPORTUNITY-BOARD.md` | Specified richer board | SPECIFIED_ONLY vs renderer |
| Journal | `vector/journal/store.py` | In-memory append; rewrite refused | IMPLEMENTED (in-memory) |
| Discovery | `vector/discovery/models.py` `validate.py` `handoff.py` | Offline commentary lifecycle → G1 nomination | IMPLEMENTED (offline) |
| Demo | `vector/demo/run_stage1.py` | Synthetic board print | IMPLEMENTED |
| Tests | `tests/test_*.py` | Offline fixtures; no live network | IMPLEMENTED |
| Skill / intended product | `skill/SKILL.md` + `skill/references/*` | Operating skill and target architecture | SPECIFIED_ONLY |
| Webull questionnaire | `docs/WEBULL-ENTITLEMENT-QUESTIONS.md` | Planned provider questions | SPECIFIED_ONLY |
| BeeKeeper reader | none in VECTOR tree | Future published-artifact consumer | SPECIFIED_ONLY / NOT_IMPLEMENTED |

Do not treat `PROVIDER_CANDIDATE = "webull"` on `OfflineMarketSource` as a connected client. It is a string label on a blocker class.

---

## 4. Data objects

### ResearchPacket — `vector/contracts/packet.py`

- Producer: `evaluate_candidate` then `critique`
- Consumer: board renderer, journal, tests, demo; specified future BeeKeeper reader
- Important fields: `run_id`, `cutoff`, `generated_at`, `rules_version`, `operating_mode`, `gamma_variant`, `sage`, `alignment`, `ticker`, `direction`, `setup`, `thesis`, `contract`, `alternatives`, `scenarios`, `score`, `vetoes`, `missing_evidence`, `disposition`, `red_team`, `authority`, `notes`
- Immutable/frozen: Pydantic model, not `frozen=True`. Mutated in place by red team (`disposition`, `red_team`, thesis restored)
- Persisted: no. Optional in-memory journal stores a reduced `JournalEntry`
- Synthetic vs production: production-shaped type; current demo/tests are synthetic-only

### SageContext / SageUpstreamFields — `vector/contracts/sage.py`

- Producer: `SageReadOnlyAdapter.ingest`
- Consumer: pipeline packet, `_score_macro`, discovery `official_freeze_admitted`, public dict
- Important fields: `status`, `alignment`, `operating_mode`, `upstream.*`, `freeze_count_reported`, `freeze_count_invented`, `claimed_established`, `verified_established`
- `as_public_dict()` publishes regime/posterior/freeze only if `verified_established` AND `ESTABLISHED` AND `SAGE_INFORMED` — a conjunction the adapter cannot currently satisfy
- Persisted: no
- Synthetic: payloads may be marked synthetic; entitlement on claim provenance is `unverified`

### Thesis — `vector/contracts/packet.py`

- Producer: caller (`make_thesis` in tests/demo)
- Consumer: eligibility geometry, scoring risk, red team, journal text fields
- Fields: trigger / expected_response / because / invalidated_if / alternate_path / expected_horizon / why_this_contract / prices / horizon_sessions
- Red team copies and restores original thesis (`original_thesis_preserved`)

### OptionContract — `vector/contracts/options.py`

- Producer: caller / synthetic helpers. Live chain producer FORBIDDEN in Stage 1
- Consumer: gates, OCC match, scenarios, scoring, board row
- Fields: OCC, right, strike, expiration, DTE, quotes, OI, Greeks, IV, quote_time, greeks_time, adjusted/nonstandard, provenance
- `mid` / `spread` / `spread_pct` derived after init
- `abs_delta` uses absolute value (puts)

### ScenarioResult — `vector/contracts/options.py`

- Producer: `estimate_scenarios`
- Consumer: packet.scenarios; support test for economics veto
- Not a probability. Notes declare local approximation

### MarketSnapshot / FeaturePacket / GammaSnapshot / Bar — `vector/contracts/market.py`

- Producer: caller. Features library can fill FeaturePacket. Gamma is a vendor-model object, not inventory
- Consumer: pipeline, scoring, coherence vetoes
- Gamma printable + stamp fields required for `GAMMA_CONFIRMED`

### ScoreBreakdown — `packet.py`

- Producer: `score_candidate`
- Missing subfactors listed; `reweighted` always False in engine

### Vetoes / missing evidence

- Vetoes: `list[str]` on packet from eligibility + pipeline geometry/scenario + authority clamp
- Missing evidence: copied from `score.missing_subfactors`
- High score + veto → disposition `NO_TRADE` before and after red team

### JournalEntry — `vector/journal/store.py`

- Producer: `EvaluationJournal.append_packet`
- Not frozen. Has unused `outcome` / `outcome_notes` fields that are never written by current code
- Collection exposed as `tuple`; contained models remain mutable — deep immutability NOT_ESTABLISHED
- Persisted: no

### CandidateDiscoveryRecord / G1HandoffNomination

- Producer: offline validate/handoff
- `G1HandoffNomination` is `frozen=True`
- Does not mint Sage, contract, GEX, or points
- Synthetic default `True`

### Provenance — `vector/contracts/provenance.py`

- Required on Stage 1 snapshot accept: `synthetic=True`, `data_status=SYNTHETIC`, `entitlement=stage1-synthetic-only`

---

## 5. Eligibility versus scoring

Separation is implemented.

**Eligibility** (`evaluate_eligibility` + pipeline extras + `coherence_vetoes`) produces veto strings. Any veto forces `Disposition.NO_TRADE` before red team. Red team cannot clear a veto. Scoring still runs so the packet can explain the grade, but grade cannot promote a vetoed row.

Evidence: `vector/eligibility/gates.py` docstring; `vector/pipeline.py` disposition block; `vector/redteam/critique.py` lucky_path check; `tests/test_pipeline_and_authority.py` `test_high_score_plus_hard_veto_is_no_trade`.

### What can veto a candidate (implemented codes)

From `evaluate_eligibility`:

`PREMARKET_NO_LIVE_CHAIN`, `MISSING_CONTRACT`, `LISTINGS_UNAVAILABLE`, `DTE_MISMATCH`, `DTE_OUT_OF_RANGE`, `NOT_END_OF_WEEK`, `UNLISTED_EXPIRATION`, `MISSING_QUOTES`, `CROSSED_QUOTES`, `ZERO_BID`, `ZERO_MID`, `MALFORMED_QUOTES`, `SPREAD_GT_15PCT`, `MISSING_OPEN_INTEREST`, `OI_BELOW_MINIMUM`, `MISSING_DELTA/GAMMA/THETA/VEGA/IV`, `NONFINITE_*`, `DELTA_OUT_OF_RANGE`, `IV_OUT_OF_RANGE`, `INVALID_STRIKE`, `MISSING_QUOTE_TIME`, `MISSING_GREEKS_TIME`, `NAIVE_QUOTE_TIMESTAMP`, `NAIVE_GREEKS_TIMESTAMP`, `FUTURE_*_TIMESTAMP`, `STALE_CHAIN`, `STALE_GREEKS`, `TIMESTAMP_MISMATCH`, `ADJUSTED_CONTRACT`, `NONSTANDARD_DELIVERABLE`, `UNSUPPORTED_MULTIPLIER`, plus OCC identity vetoes (`CONTRACT_IDENTITY_UNPARSEABLE`, `CONTRACT_UNDERLYING_MISMATCH`, `CONTRACT_RIGHT_MISMATCH`, `CONTRACT_EXPIRY_MISMATCH`, `CONTRACT_STRIKE_MISMATCH`).

From pipeline:

`MISSING_NEARBY_STRIKE`, `MISSING_NEARBY_EXPIRATION`, `THESIS_GEOMETRY_INCOMPLETE`, `SCENARIOS_UNAVAILABLE`, `SCENARIO_ECONOMICS_FAIL`, `EXECUTION_AUTHORITY_MUST_REMAIN_DISABLED`.

From coherence:

`TICKER_CONTRACT_MISMATCH`, `MARKET_CONTRACT_MISMATCH`, `DIRECTION_RIGHT_MISMATCH`, `GAMMA_UNDERLYING_MISMATCH`, `FEATURE_SYMBOL_MISMATCH`.

### Can a high score override a veto?

No. IMPLEMENTED_GATE.

### DTE rules (implemented)

- Calendar DTE = `(expiration - as_of).days`
- Declared `contract.dte` must match or `DTE_MISMATCH`
- Universe 14–45 inclusive; outside → `DTE_OUT_OF_RANGE` and score 0 / REJECT
- Fixed bands 14–21 / 22–35 / 36–45; no interpolation (`docs/CONFLICTS.md`, `DTE_FACTOR_WEIGHTS`)

### Expiration rules (implemented)

- `require_end_of_week=True`: holiday-adjusted EOW via `US_EQUITY_HOLIDAYS_2025_2027`
- If `listed_expirations` is None and required → `LISTINGS_UNAVAILABLE`
- Expiration not in supplied listed set → `UNLISTED_EXPIRATION`
- No fabricated Friday: identity must parse from OCC and match fields

### Liquidity / OI / spread (implemented)

- OI required and ≥ 100
- Spread > 15% of mid hard veto
- Zero bid / zero mid excluded
- Scoring liquidity points use 5% / 10% / 15% bands but cannot override the 15% veto

### Stale chain / stale Greeks (implemented)

- Quote max age: `freshness.chain_max_age` = 20 minutes → `STALE_CHAIN`
- Greeks max age: 15 minutes → `STALE_GREEKS`
- Cross-input tolerance 30 minutes → `TIMESTAMP_MISMATCH`
- Naive and future timestamps rejected
- Nearby alternatives must also be fresh at cutoff or they do not count (`_alternative_fresh_at_cutoff`)

### Missing-data handling (implemented)

- Mandatory quote/Greek/OI fields veto
- Optional scoring evidence (gamma stamp, catalyst, flow, Sage confirmation, transmission) scores 0 and is listed in `missing_subfactors`
- Engine does not redistribute missing points (`reweighted=False`)

### Not implemented as eligibility (do not infer)

- Live chain presence detector beyond the caller flag `premarket_without_live_chain`
- Automatic holiday calendar beyond the hardcoded 2025–2027 set
- Delta-outside-preferred-band as a hard veto (preferred 0.35–0.50 is a scoring fit, not a gate; `max_abs_delta=1.0` is the hard cap)
- Intraday time-of-day relative volume normalization (feature uses last bar vs prior N daily volumes)

---

## 6. SAGE boundary

### Stage 1 adapter (implemented)

File: `vector/sage/adapter.py` `SageReadOnlyAdapter.ingest`

What it actually checks:

- `payload is None` → `UNAVAILABLE`, freeze count not invented
- SIGIL / `legacy_sigil` → isolated `UNAVAILABLE`
- Parse failure → `INVALID`
- `status_text == UNAVAILABLE` and not established → `UNAVAILABLE`
- `NOT_ESTABLISHED` or `established is False` → `NOT_ESTABLISHED`, preserve supplied count only
- `established is True`:
  - source_identity must be in `{SAGE}`
  - required fields: schema_version, source_identity, cutoff, receipt_time, freeze_identity, regime
  - timezone-aware cutoff/receipt; no future; receipt ≥ cutoff
  - posterior must be a dict of finite masses in [0,1] summing to 1.0 (no bool/string/scalar)
  - cutoff older than 36h → `STALE` still `BEHAVIOR_ONLY`
  - otherwise structurally complete claim → `NOT_ESTABLISHED`, `claimed_established=True`, `verified_established=False`, `BEHAVIOR_ONLY`, `INSUFFICIENT`

Write / update_posterior / mint_regime raise `SageWriteError`.

Settings cannot open admission: `sage_informed_admission_enabled` validator always returns False. Adapter has **no branch** that returns `SageStatus.ESTABLISHED` + `OperatingMode.SAGE_INFORMED` + `verified_established=True`.

Scoring Sage points require that unreachable conjunction (`_score_macro`). Discovery freeze comparison requires the same plus `upstream.freeze_identity` (`official_freeze_admitted`).

Unused ingest kwargs `observed_direction` and `transmission_observed` must stay unused. Tape cannot become Sage alignment. Documented in `audits/2026-09-20-sage-adapter-integration-review.md`.

### Official freeze admission contract (specified only)

File: `sage-vector-bridge` `engine/HOW-VECTOR-MUST-CONSUME.md` @ `2a3c0b9`

Required conjunction (all):

1. Genuine official freeze dump on `mailbox/SAGE-TO-VECTOR.md`
2. `ok = true`
3. `officialFreezeId` present
4. `officialFreezeCount` integer > 0
5. `engineCommit` equals Sage `implementationCommit` `b7f52bef5b6c4e133b3e860c89387c6417117c79` and VECTOR has actually seen it
6. cutoff with Sage session convention
7. completeness COMPLETE on all six pillars
8. authoritative lineage preserved, including `evidenceLineage.rawBytesSha256[]`
9. schema name pinned by Sage (example schema is not pinned)

Stage 1 adapter does **not** read the mailbox file, does **not** check `ok`, `engineCommit`, six-pillar completeness, or raw-byte lineage. It is a local payload classifier plus an admission lock.

`ARCHITECTURE_DISCREPANCY = PRESENT`:

- Stage 1 adapter field subset + hard close
- versus full official-freeze conjunction in `HOW-VECTOR-MUST-CONSUME.md`

Do not claim the Stage 1 adapter implements the complete official-freeze conjunction.

### Current governance (bridge + VECTOR config)

```
OFFICIAL_FREEZE_COUNT = 0
SAGE_INPUT = UNAVAILABLE
SAGE_INFORMED = disabled
CONSULT_IS_NOT_FREEZE = YES
```

Evidence: bridge `mailbox/STATUS.md`, `engine/LOCKS.md`; VECTOR `SAGE_INFORMED_ADMISSION_ENABLED = False`.

VECTOR must not reconstruct Sage from chat, consult, technicals, tape, BeeKeeper, prior narratives, display HTML, or synthetic/replayed evidence. Consult channel exists on the bridge only (`consult/VECTOR-ASKS.md`) and is specified as non-admission.

---

## 7. Market-data boundary

| Source class | Module | IMPLEMENTED | CONNECTED | ENTITLED | LIVE | WRITE_CAPABLE |
|---|---|---|---|---|---|---|
| Synthetic fixture / snapshot | `tests/helpers.py`, `OfflineMarketSource.accept_snapshot` | YES | N/A (in-process) | `stage1-synthetic-only` | NO | NO |
| Offline source object | `vector/data/ingestion.py` | YES (blocker + accept) | NO network | synthetic only | NO | NO |
| Live quote source | `fetch_quote` | method exists only to raise | NO | NO | NO | NO |
| Live options chain | `fetch_chain` | method exists only to raise | NO | NO | NO | NO |
| Greeks | fields on `OptionContract` | type + freshness gates | NO vendor | synthetic fixtures | NO | NO |
| GEX / vendor gamma | `GammaSnapshot` + `gamma_variant_of` | type + scoring variant | NO vendor API | NO | NO | NO |
| OCC identity | `vector/eligibility/identity.py` | parser only | N/A | N/A | N/A | NO |
| Broker data | none | NO | NO | NO | NO | NO |
| Webull programmatic | questionnaire + candidate string | NO | NO | NO | NO | NO |
| Order submit | `submit_order` | raises `LiveIngestionBlocked` | NO | NO | NO | FORBIDDEN |

`docs/MARKET-DATA-PROVIDER.md` and `docs/WEBULL-ENTITLEMENT-QUESTIONS.md` are planning artifacts. They are not integrations.

GEX is a vendor-model object. Missing/incomplete stamp → `GAMMA_UNAVAILABLE` and zero gamma points. Technical structure cannot award gamma points (`_score_gamma` + `docs/CONFLICTS.md`).

---

## 8. Journal / persistence architecture

Inspected: `vector/journal/store.py`, `tests/test_journal_and_ingestion.py`, bridge `beekeeper/2026-09-24-vector-journal-append-only-review.md`.

| Property | State |
|---|---|
| In-memory vs durable | IN_MEMORY_ONLY (`list` on `EvaluationJournal`) |
| Append | IMPLEMENTED (`append_packet`, monotonic `seq`) |
| Rewrite | REFUSED (`rewrite` raises `PermissionError`) |
| Identity model | `seq` + `run_id` only |
| Content hashing | NOT_IMPLEMENTED |
| Linked outcomes | Fields exist (`outcome`, `outcome_notes`) but are never written; linked-observation model NOT_IMPLEMENTED |
| Crash safety | NOT_IMPLEMENTED |
| Idempotent replay | NOT_IMPLEMENTED |
| Persistence backend | NOT_IMPLEMENTED |
| Deep immutability | NOT_ESTABLISHED (entries are mutable Pydantic models) |

Preserve:

```
VECTOR_STAGE1_JOURNAL = IN_MEMORY_ONLY
VECTOR_DURABLE_STORE = NOT_IMPLEMENTED
```

This journal is not BeeKeeper storage. Relabeling it as BeeKeeper is FORBIDDEN.

Pipeline does not auto-append. Callers (tests) construct `EvaluationJournal` separately.

---

## 9. Execution boundary

| Gate | Code | Actual capability |
|---|---|---|
| Research | `AuthorityConfig.research_enabled=True` | Packet evaluation allowed |
| Paper execution | default False; packet clamp | Cannot enable via score/JSON |
| Live execution | default False; packet clamp | Cannot enable via score/JSON |
| Broker submission | `OfflineMarketSource.submit_order` | Raises; no SDK |
| Order creation | NOT_FOUND_IN_INSPECTED_SOURCES | none |
| Account access | NOT_FOUND_IN_INSPECTED_SOURCES | none |

`Disposition.RESEARCH_ELIGIBLE` exists on the enum but Stage 1 pipeline/red team never assign it. Best non-veto outcome after critique is `WATCH` with red-team `REDUCE`.

Saved JSON cannot claim execution authority (`test_saved_json_cannot_claim_execution_authority`).

---

## 10. BeeKeeper boundary

What VECTOR can eventually publish (specified, not implemented):

- Full `ResearchPacket` including exact quote/OI/Greek times, thesis, vetoes, Sage public dict, authority block
- Not merely `to_board_row()`
- Zero candidates is valid
- Watch ≠ position

Invariants (specified on bridge / VECTOR handoff docs):

```
VECTOR WATCH != BEEKEEPER POSITION
BEEKEEPER → VECTOR FEEDBACK = PROPOSAL_ONLY
```

BeeKeeper must not rescore VECTOR, alter eligibility, change weights, trigger candidate discovery, or trigger broker activity.

Inspected VECTOR tree contains no BeeKeeper client, reader, publisher, or shared schema module.

```
BEEKEEPER_VECTOR_READER = SPECIFIED_NOT_IMPLEMENTED
```

BeeKeeper application repository: NOT REGISTERED in `THREE-BUILD-OPERATING-MODEL.md`. Not claimed present.

market-agent-desk has a `vector/` folder and governance IDs referenced by `docs/SOURCE-INVENTORY.md`. Desk artifacts are research/governance, not VECTOR runtime and not automatically BeeKeeper’s publication destination.

---

## 11. Fail-closed architecture

Six accepted detection tests applied to inspected VECTOR code. Criteria source: bridge `beekeeper/2026-09-24-fail-open-detection-tests.md` @ `2a3c0b9`.

### 1. Can a non-owner channel satisfy a required field?

- SIGIL / legacy_sigil isolated: `SageReadOnlyAdapter.ingest` — IMPLEMENTED_GATE
- Null payload cannot invent freeze count — IMPLEMENTED_GATE
- Consult / chat / mailbox dump are not read by the adapter — SPECIFIED_ONLY that they cannot admit; no consult parser in VECTOR runtime (GAP vs full consume contract, but also means consult cannot currently satisfy adapter fields either)
- Discovery tokens (`OS-H` etc.) do not admit freeze comparison; `official_freeze_admitted` conjunction — IMPLEMENTED_GATE

Classification: PARTIAL_CODE overall. Local channels blocked; official mailbox conjunction not coded.

### 2. Can PARTIAL / stale pass as COMPLETE / current?

- Sage cutoff older than 36h → `STALE`, not ESTABLISHED — IMPLEMENTED_GATE (`_handle_established_claim`)
- Stale quotes/Greeks veto — IMPLEMENTED_GATE
- Stale commentary > 14 days cannot promote discovery — IMPLEMENTED_GATE
- Six-pillar `completeness=COMPLETE` not checked — SPECIFIED_ONLY / GAP versus official contract
- Nearby stale alts do not count as comparisons — IMPLEMENTED_GATE (P1)

Classification: IMPLEMENTED_GATE for VECTOR-native freshness; SPECIFIED_ONLY for Sage pillar completeness.

### 3. Are nulls coerced before admission?

- UNAVAILABLE public dict `officialFreezeCount` is None, not 0-invented — IMPLEMENTED_GATE
- Posterior bool/string/scalar rejected — IMPLEMENTED_GATE `_posterior_policy`
- Naive timestamps rejected rather than assumed UTC on Sage cutoff/receipt — IMPLEMENTED_GATE
- Missing contract returns veto list instead of synthesizing a chain — IMPLEMENTED_GATE

Classification: IMPLEMENTED_GATE for inspected adapters/gates.

### 4. Can a consumer read mint upstream evidence?

- `write` / `update_posterior` / `mint_regime` raise `SageWriteError` — IMPLEMENTED_GATE
- `verified_established` never set True — IMPLEMENTED_GATE
- Public Sage fields unpublished unless verified conjunction — IMPLEMENTED_GATE `as_public_dict`
- G1 nomination `catalyst_verified=False`, `score_points=0`, no contract/GEX — IMPLEMENTED_GATE
- BeeKeeper reader absent so it cannot mint into VECTOR from this repo — NOT_IMPLEMENTED consumer (safe by absence, not a BeeKeeper proof)

Classification: IMPLEMENTED_GATE for VECTOR→Sage minting.

### 5. Can an earlier stage authorize a later stage?

- Score cannot override veto — IMPLEMENTED_GATE
- Red team cannot PROMOTE; PROMOTE coerced to REDUCE — IMPLEMENTED_GATE
- Discovery promotion ≠ catalyst_verified ≠ scored packet — IMPLEMENTED_GATE
- Paper/live remain disabled even if packet JSON says otherwise — IMPLEMENTED_GATE
- `RESEARCH_ELIGIBLE` enum value unused; Stage 1 cannot graduate to trade-ready — PARTIAL_CODE relative to later-stage product

Classification: IMPLEMENTED_GATE for execution and Sage-informed; later research-eligible promotion is locked, not implemented.

### 6. Can a closed state be silently repaired?

- Complete ESTABLISHED-shaped payload still closed as unverified `NOT_ESTABLISHED` — IMPLEMENTED_GATE
- Settings flag cannot open admission — IMPLEMENTED_GATE
- Unused tape kwargs not wired into alignment — IMPLEMENTED_GATE (non-repair)
- Journal `outcome` fields exist and could become a future silent repair if someone adds `update_outcome()` — GAP / latent schema risk (documented; not active code)
- Closed Sage cannot be repaired by gamma, features, or discovery tokens — IMPLEMENTED_GATE in scoring/discovery conjunctions

Classification: IMPLEMENTED_GATE for Sage closed-state; GAP for latent journal outcome mutation if later code writes those fields.

---

## 12. What VECTOR does NOT currently have

Use NOT_FOUND_IN_INSPECTED_SOURCES rather than a universal negative.

| Capability | Finding |
|---|---|
| Durable database | NOT_FOUND_IN_INSPECTED_SOURCES (no sqlite/postgres/files store module) |
| Embedding / vector database | NOT_FOUND_IN_INSPECTED_SOURCES |
| Live broker client | NOT_FOUND_IN_INSPECTED_SOURCES; `submit_order` is a raise-only stub |
| Webull programmatic connection | NOT_FOUND_IN_INSPECTED_SOURCES; questionnaire only |
| Production Sage freeze admission | NOT_IMPLEMENTED (adapter cannot emit verified ESTABLISHED) |
| Official freeze mailbox ingest | NOT_FOUND_IN_INSPECTED_SOURCES in VECTOR runtime |
| BeeKeeper runtime integration | NOT_FOUND_IN_INSPECTED_SOURCES |
| Live execution | FORBIDDEN in this build; no path found |
| Automatic learning / retuning | NOT_FOUND_IN_INSPECTED_SOURCES |
| FastAPI / HTTP service | NOT_FOUND_IN_INSPECTED_SOURCES (`docs/ARCHITECTURE.md` says single process; no API module) |
| Scheduler / daily job runner | NOT_FOUND_IN_INSPECTED_SOURCES |
| Historical options backtest | NOT_FOUND_IN_INSPECTED_SOURCES |
| Live GEX vendor client | NOT_FOUND_IN_INSPECTED_SOURCES |
| Universe scanner / contract picker | NOT_FOUND_IN_INSPECTED_SOURCES |
| Intraday TOD relative-volume normalizer | NOT_FOUND_IN_INSPECTED_SOURCES |
| Alignment CONSISTENT / INCONSISTENT computation | NOT_FOUND_IN_INSPECTED_SOURCES (enum exists; adapter never sets them) |
| `evaluate_candidate` → journal auto-write | NOT_FOUND_IN_INSPECTED_SOURCES |

---

## 13. Architecture diagram (source-corrected)

```text
SAGE official freeze
  |
  | specified only: mailbox dump + full conjunction
  | implemented today: no freeze ingest; count documented 0
  | status: UNAVAILABLE / FORBIDDEN to reconstruct
  v
VECTOR  (build/stage-1-contracts @ f7d24bb)
  |
  +-- [implemented] caller-supplied synthetic MarketSnapshot + OptionContract
  +-- [implemented / live forbidden] OfflineMarketSource accept_snapshot / raise on fetch
  +-- [implemented] SageReadOnlyAdapter  -> always BEHAVIOR_ONLY / INSUFFICIENT
  +-- [implemented] eligibility + OCC identity + nearby freshness
  +-- [library implemented, not pipeline-invoked] compute_features
  +-- [partial] alignment field present; CONSISTENT path unavailable
  +-- [implemented] deterministic scoring (Sage points = 0)
  +-- [implemented] first-order scenario grid
  +-- [implemented] red team (PROMOTE forbidden)
  +-- [implemented] ResearchPacket
  +-- [implemented in-memory] journal append / rewrite refused
  +-- [implemented markdown] board render
  +-- [implemented offline, not scored] discovery -> G1 nomination
        |
        | specified only: published immutable artifact boundary
        | implemented today: no publisher, no durable artifact store
        v
BEEKEEPER
        reader SPECIFIED_NOT_IMPLEMENTED
        must not rescore / change gates / discover / trade
        application repo NOT_VERIFIED
```

Connection marks:

- SAGE → VECTOR official freeze: specified only; currently unavailable
- Consult → VECTOR admission: forbidden
- VECTOR → SAGE write: forbidden / implemented raise
- VECTOR → BeeKeeper publish: specified only
- BeeKeeper → VECTOR feedback: specified proposal-only; no reader
- Webull → VECTOR: specified only; live fetch forbidden
- Broker → VECTOR: forbidden

---

## Documented discrepancies (do not silently resolve)

`ARCHITECTURE_DISCREPANCY = PRESENT`

1. `docs/ARCHITECTURE.md` sequences feature calculation and SAGE alignment inside the runtime; `vector/pipeline.py` does not call `compute_features` and never receives CONSISTENT alignment from the adapter.
2. Stage 1 Sage adapter checks a local field subset; `engine/HOW-VECTOR-MUST-CONSUME.md` requires a different, stricter official-freeze conjunction. Adapter close is fail-closed, not equivalent implementation of that conjunction.
3. `main` (`0b0d7c8`) is skill/coordination; implementation HEAD is `build/stage-1-contracts` (`f7d24bb`). PR #1 HOLD. Treating `main` as the runtime is incorrect.
4. `Disposition.RESEARCH_ELIGIBLE` and `RedTeamVerdict.PROMOTE` exist on enums; Stage 1 critique forbids PROMOTE and never emits RESEARCH_ELIGIBLE.
5. Board template `skill/assets/DAILY-OPTIONS-OPPORTUNITY-BOARD.md` specifies a richer packet display than `vector/board/render.py` actually prints.
6. README authority block still says `SAGE_STATUS = NOT_ESTABLISHED` while bridge status says `SAGE_INPUT = UNAVAILABLE`. Related but not the same enum. Adapter uses both statuses depending on payload; governance lock is UNAVAILABLE / disabled informed mode.

Conflict log already records older skill interpolations vs Stage 1 fixed bands (`docs/CONFLICTS.md`). Those older wordings do not govern runtime.

---

## Final status block

```
VECTOR_ARCHITECTURE_MAP = COMPLETED
VECTOR_STAGE1_RUNTIME = SYNTHETIC_SNAPSHOT_EVALUATOR_ON_PR_BRANCH
VECTOR_DURABLE_STORE = NOT_IMPLEMENTED
VECTOR_LIVE_MARKET_DATA = BLOCKED
VECTOR_WEBULL_INTEGRATION = NOT_IMPLEMENTED
VECTOR_SAGE_ADMISSION = CLOSED_UNAVAILABLE
BEEKEEPER_VECTOR_READER = SPECIFIED_NOT_IMPLEMENTED
LIVE_EXECUTION_AUTHORIZED = FALSE
OFFICIAL_FREEZE_COUNT = 0
SAGE_INPUT = UNAVAILABLE
SAGE_INFORMED = disabled
IMPLEMENTATION_AUTHORIZED = NO
NEXT_IMPLEMENTATION_SLICE = HOLD
REVIEW != APPROVAL != TRADE
PR_1 = HOLD
WEBULL = HOLD
VECTOR_WRITES_TO_SAGE = false
VECTOR_STAGE1_JOURNAL = IN_MEMORY_ONLY
ADAPTER_CAN_MINT_ESTABLISHED = NO
CONSULT_IS_NOT_FREEZE = YES
```

Inspected implementation HEAD: `richardfslead25-netizen/vector-build-audit` `build/stage-1-contracts` `f7d24bb15044c6347aecd49f004db67159c07ed1`.

This map does not authorize a slice, a merge, Sage admission, Webull, or execution.
