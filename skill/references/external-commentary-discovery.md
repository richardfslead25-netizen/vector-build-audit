# External Commentary → Candidate Discovery

Status: specification only. No runtime channel. Issue #5 docs slice.

Parent implementation HEAD at assignment: `b0999882391a72e19f178f88a2940751f7f65833`  
Functional OCC HEAD: `6c9a79c4302cf834285f5ee0eb415f3275d10170`  
Branch: `build/stage-1-contracts`

```
COMMENTARY_ROLE = NOMINATE
VECTOR_ROLE = VALIDATE
SAGE_ROLE = OPTIONAL_READ_ONLY_UPSTREAM
SCORING_CHANGE = NONE
RUNTIME_CHANNEL = NOT_AUTHORIZED
```

## Purpose

Use published research, strategist revisions, company guidance, and major news to nominate prospective bullish or bearish names **before** a setup is fully formed.

Commentary is not proof of causation, timing, regime, or trade approval. VECTOR still has to verify tape, identity, liquidity, contract economics, and red-team gates. Commentary never becomes Sage evidence and never writes a Sage pillar.

Illustrative mechanism only — not a current Sage reading and not a verified event:

> Strategist lowers an index target because higher yields justify a lower P/E → valuation-compression hypothesis → inspect rate-sensitive, richly valued exposures → independently validate earnings, technicals, positioning, and contracts.

The phrase “consistent with a QT-T valuation channel” names a **hypothetical** transmission path. It does not establish QT-T, mint a freeze, or award Sage-confirmation points.

## What this slice does not do

- No live ingestion, Webull, scheduler, scraper, or new provider entitlement.
- No scoring formula, DTE-band, or weight change.
- No new score bucket and no automatic commentary points.
- No Sage write, freeze mint, regime inference, or SAGE_INFORMED admission.
- No parallel ranking engine.
- No 0DTE path.
- No paper or live execution authority.

## Placement in the existing stack

Commentary sits **upstream of G1**, not beside scoring.

```
external commentary
        ↓ nominate only
discovery watchlist (unscored)
        ↓ independent VECTOR validation
existing catalyst intake + provenance
        ↓
G0 freshness → G0b fusion → G1 thesis/catalyst
        ↓
G2 gamma/structure ↓ G3 contract/liquidity → G4 red team
        ↓
existing board / disposition / journal
```

Reuse these surfaces. Do not invent a second board.

| Existing surface | Future integration point | This spec may |
|---|---|---|
| `MarketSnapshot.catalyst_id`, `catalyst_verified`, `catalyst_time`, `catalyst_inside_horizon` | Attach a discovery event id only after independent verification | Propose field mapping |
| `Provenance` | Carry source URL, publisher, publication time, retrieval time, synthetic/entitlement flags | Propose required fields |
| Fusion `CONSISTENT` / `INCONSISTENT` / `INSUFFICIENT` | Map Sage relationship; no freeze → `INSUFFICIENT` | Use existing enum |
| `_score_catalyst` | Still requires verified catalyst + timing inside horizon | Unchanged |
| `_score_macro` Sage-confirmation conjunction | Still requires `verified_established` + `SAGE_INFORMED` + `ESTABLISHED` + `CONSISTENT` | Unchanged; commentary cannot satisfy it |
| Journal / packet `thesis` | Trigger, invalidation, horizon remain VECTOR fields | Commentary may suggest; VECTOR must own |
| Eligibility / OCC / nearby freshness | Apply only when a contract is evaluated | Unchanged |
| Stage 1 red team | Still cannot `PROMOTE` | Unchanged |

Byte-unchanged in this slice: `vector/scoring/engine.py`, `vector/config.py`, `vector/sage/adapter.py`, `vector/eligibility/identity.py`, `vector/pipeline.py`, DTE bands, authority defaults.

## Discovery record

One originating source event produces one discovery record. Syndicated reprints of the same note are the same event.

Required fields:

| Field | Rule |
|---|---|
| `source_event_id` | Stable id of the originating note/guidance/filing, not the reprint URL |
| `source_url` / document identity | Primary preferred |
| `author` / `publisher` | As printed |
| `published_at` + timezone | Original publication, not syndication time |
| `retrieved_at` + timezone | VECTOR retrieval |
| `source_class` | `PRIMARY_RESEARCH` / `COMPANY_GUIDANCE` / `PRIMARY_NEWS` / `SECONDARY_REPORTING` / `UNVERIFIED_CLAIM` |
| `forecast_horizon` | Horizon **the source** stated |
| `prior_estimate` / `new_estimate` / units | Missing prior stays `UNAVAILABLE` |
| `stated_rationale` | Source’s own words, quoted or tightly paraphrased |
| `vector_inference` | Separate from stated rationale; may be empty |
| `mechanisms[]` | See taxonomy below; multiple allowed |
| `candidate` | Index, sector, or issuer |
| `direction` | `BULLISH` / `BEARISH` / `NO_SETUP` |
| `exposure_rationale` | Why this name, not just its sector label |
| `contradiction` | Known contrary facts at capture time |
| `sage_relationship` | `CONSISTENT` / `INCONSISTENT` / `INSUFFICIENT` |
| `official_freeze_ref` | Exact freeze identity if a valid official freeze exists; else null |
| `evidence_still_needed` | Explicit gaps |
| `suggested_trigger` / `suggested_invalidation` | Commentary suggestions only |
| `transmission_horizon` | When VECTOR expects the mechanism to show in tape, if at all |
| `holding_horizon` | Only if a 14–45 DTE thesis is later proposed |
| `contract_expiry` / `dte` | Only after an actual contract is evaluated |
| `status` | Discovery lifecycle below |
| `supersedes` / `correction_of` | Pointers; never silent overwrite |

Publication verified ≠ mechanism verified ≠ transmission observed.

## Mechanism taxonomy

Classify source-stated and VECTOR-inferred mechanisms separately.

- Valuation compression / expansion (target or multiple change with unchanged fundamentals)
- Earnings / estimate revisions
- Credit / refinancing pressure
- Demand changes
- Input-cost / supply changes
- Policy catalyst
- Company-specific catalyst (guidance, product, legal, capital action)

Index target revisions and EPS revisions are distinct. A target cut does not establish an EPS cut, credit stress, or a bearish single-name setup.

Fame of the analyst adds no points.

## Horizon split (mandatory)

Keep three clocks. Do not collapse them.

1. **Source forecast horizon** — what the note claims (often months or a year-end target).
2. **Transmission horizon** — when, if ever, VECTOR expects the mechanism to appear in prices/breadth/credit.
3. **Holding / contract horizon** — 14–45 DTE EOW only after a contract is selected.

A six-month strategist target cannot establish a two-week catalyst without independent timing evidence. That failure is `HORIZON_MISMATCH`, not a reason to invent 0DTE or stretch DTE bands.

## Sage relationship

Compare commentary only to a latest **valid official Sage freeze** under the existing adapter contract.

| Upstream Sage state | Discovery `sage_relationship` | Score effect |
|---|---|---|
| `UNAVAILABLE` / `INVALID` / `STALE` / `NOT_ESTABLISHED` | `INSUFFICIENT` | Zero Sage-confirmation points |
| Official freeze exists, tape/commentary path agrees | `CONSISTENT` only after adapter `verified_established` | Still zero until production admission is separately enabled |
| Official freeze exists, path conflicts | `INCONSISTENT` | Existing macro penalty only; do not kill tape solely from fusion |

Today: `SAGE_INPUT=UNAVAILABLE`, `OFFICIAL_FREEZE_COUNT=0`, `SAGE_INFORMED=disabled`. Every live discovery row is therefore `INSUFFICIENT` at the regime layer.

Commentary must not:

- overwrite Sage
- mint `OS-H`, `QT-T`, or any catalog ID
- treat “consistent with QT-T” as confirmation
- write tape or commentary into Sage pillars

Consult ≠ freeze.

## Lifecycle (reuse existing words; do not invent grades)

| Status | Meaning |
|---|---|
| `CAPTURED` | Source event recorded; unverified |
| `WATCH` | Tracking only. Not an earned numeric score |
| `UNVERIFIED` | Source or mechanism quality, not a scoring grade |
| `PROMOTED_TO_CATALYST_INTAKE` | Passed independent verification enough to enter existing G1 fields |
| `REJECT` | Scored candidate failed a gate; cannot be relabeled `WATCH` to hide the veto |
| `NO_SETUP` | Commentary does not produce a VECTOR thesis |
| `SUPERSEDED` / `WITHDRAWN` | Correction or retraction retained in journal |

An unscored discovery row has **no fabricated score**. `WATCH` in discovery ≠ grade `WATCH` (≥62).

Promotion from discovery to the opportunity board still requires G0–G4, OCC identity, nearby-comparison freshness, and Stage 1 red-team rules. Missing chain or GEX cannot be fabricated. Missing GEX → `GAMMA_UNAVAILABLE`, zero gamma points.

## Dedup and non-double-count

- Three articles quoting one strategist note = one `source_event_id`.
- That event must not later be counted again as independent corroboration in both catalyst and macro buckets.
- Secondary reporting is labeled secondary even when it names a famous desk.
- Corrections and withdrawn forecasts append; they do not erase the original hypothesis.

## Required discovery table

When a future runtime or a manual desk note prints discovery rows, use:

Source/time | Mechanism | Candidate | Direction | Exposure rationale | SAGE relationship | Evidence still needed | Trigger | Invalidation | Horizon | Status

Horizon column must show source forecast / transmission / holding as three values, not one.

## Future acceptance cases (tests not added in this slice)

1. Target cut with unchanged EPS remains a valuation hypothesis, not an earnings-revision setup.
2. Three syndicated stories produce one source event.
3. No valid Sage freeze → `INSUFFICIENT` / `UNAVAILABLE` and zero Sage-confirmation points.
4. Verified quotation with unsupported mechanism stays unpromoted.
5. Six-month forecast cannot establish a two-week catalyst without independent timing evidence.
6. Missing chain/GEX cannot be fabricated or used to bypass G2/G3.
7. Contradictory tape, stale commentary, corrections, and non-qualifying contracts keep existing downgrade/rejection behavior.
8. Existing scores, weights, and authority are unchanged by discovery intake.

## Authority

```
RESEARCH_ENABLED = true
PAPER_EXECUTION_ENABLED = false
LIVE_EXECUTION_ENABLED = false
VECTOR_WRITES_TO_SAGE = false
SAGE_INFORMED_ADMISSION_ENABLED = false
SAGE_INPUT = UNAVAILABLE
SAGE_POINTS = 0
LIVE_DATA_INGESTION = NO_GO
0DTE = PROHIBITED
REVIEW != APPROVAL != TRADE
```
