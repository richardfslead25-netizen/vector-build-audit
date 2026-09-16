# Grok Stage 1 code-and-contract audit — head `2c5a060`

**Date:** 2026-09-16 PT  
**Auditor:** Grok (this conversation)  
**Requested implementation head:** `2c5a06050e09f05aba774004568513d8ee2d1a41`  
**PR:** https://github.com/richardfslead25-netizen/vector-build-audit/pull/1  
**Exact-head CI:** https://github.com/richardfslead25-netizen/vector-build-audit/actions/runs/35049068343 (reported success)  
**Do not:** invent SAGE, invent market data, authorize paper/live, merge.

```text
RESEARCH_ENABLED = true
PAPER_EXECUTION_ENABLED = false
LIVE_EXECUTION_ENABLED = false
VECTOR_WRITES_TO_SAGE = false
SAGE_INFORMED_ADMISSION_ENABLED = false
```

```text
DECISION ON 2c5a060 = STAGE_1_CORRECTIONS_STILL_REQUIRED
LIVE_MARKET_DATA_INGESTION = NO_GO
A_OR_A_PLUS_PROMOTION = NO_GO
MERGE = NO
```

Green CI is not execution authority. Empty boards and `NO_TRADE` rows remain valid.

---

## Scope note — requested head vs branch tip

Reviewed implementation is `2c5a060`.

The hold mailbox says later commits are docs-only. That is **false** of current `build/stage-1-contracts` tip `55dff75`. After `2c5a060` the branch contains code commits including:

- `823adc7` Close SAGE admission bypass and unverified ESTABLISHED publication
- `11ff4ae` Reject unverified SAGE claims; tighten timestamp and posterior policy
- `0c1ae94` Lock Stage 1 snapshots to synthetic entitlement
- `1ee479e` Assert Stage 1 red team cannot PROMOTE

Those later commits are **out of scope for the requested-head verdict**. They are mentioned only to prevent treating the current tip as the reviewed artifact.

---

## Verdict in one page

P0 SAGE *scoring* isolation is mostly closed: default admission is off, SIGIL cannot confer confirmation points, null/unavailable does not invent `officialFreezeCount`, writes raise `SageWriteError`.

P0 SAGE *publication* is **not** closed at `2c5a060`. A structurally complete placeholder payload is stored as `SageStatus.ESTABLISHED` and `SageContext.as_public_dict()` then emits `CURRENT_REGIME` / `POSTERIOR` / `FREEZE`. Honest upstream today is `NOT_ESTABLISHED`. Field-complete is not a verified freeze.

P0 eligibility identity/timestamps/listings are largely closed. Remaining eligibility holes: unused `quote_max_age`, unused OI-report lag, boolean presence flags still paying full flow/transmission points.

P1 scoring/scenario gates hold for the items named in the prior GPT pass (wrong-way walls, signed RS, geometry, nearby strike **and** expiry, executable half-spread + commission, missing Greeks → no scenarios). Red team at this head is still a stub that **will PROMOTE** a synthetic A/A_PLUS packet with no vetoes.

OCC/OSI parser is acceptable for Stage 1 compact + 21-char padded + digit roots. Not a reason to open live chains.

---

## GPT-AUDIT.md questions at `2c5a060`

| # | Question | Answer at 2c5a060 |
|---|---|---|
| 1 | Downstream of Sage, or tape-minted regime? | Downstream. Adapter does not mint a catalog ID from tape. `observed_direction` / `transmission_observed` are accepted on `ingest()` and unused. |
| 2 | `NOT_ESTABLISHED` as product, or hole to fill? | Null/explicit-false are valid product states. Complete placeholder claims are published as `ESTABLISHED`. That is a hole. |
| 3 | Fusion `CONSISTENT` while Sage null? | Default path stays `INSUFFICIENT`. Admission-on path would copy payload `alignment`. Flag is off. |
| 4 | Persistence/successors separate? | Stored as separate upstream fields. Not computed. Published only when status is `ESTABLISHED`. |
| 5 | Sage-confirmation points when Sage null? | Zero. Also zero when admission is disabled even if status is `ESTABLISHED`. |
| 6 | GEX vendor model? | `gamma_variant_of()` requires vendor, methodology, underlying, coverage, as-of, units, sign, spot. Missing → `GAMMA_UNAVAILABLE` and zero gamma points. Still synthetic-vendor capable. |
| 7 | 0DTE leak? | Universe 14–45 + EOW gate. No 0DTE path in code. |
| 8 | Veto overrides high score? | Yes. Any veto → `NO_TRADE`. Stub red team cannot keep `PROMOTE` if vetoes exist. |
| 9 | Paper/live default off? | Yes. Pipeline rewrites authority back to defaults if a packet claims otherwise. |
| 10 | What must change before live A/A_PLUS? | See remaining defects and promotion blockers below. |

---

## What is actually closed vs `e5ef1be`

Closed at `2c5a060`:

- Forged `established: true` without required fields → `INVALID` (`vector/sage/adapter.py` `_handle_established_claim`).
- Unknown `source_identity` → `INVALID`.
- Future / naive SAGE timestamps → `INVALID`.
- Scalar or empty posterior → `INVALID`.
- SIGIL payload isolated; confirmation points stay 0.
- `UNAVAILABLE` freeze count is `None`, `freeze_count_invented=False`.
- Write / update_posterior / mint_regime raise `SageWriteError`.
- Quote and Greeks times required; naive and future vetoed; DTE derived vs claimed; listings required.
- OCC parse is field identity, not substring membership.
- Directional walls and signed RS.
- Nearby strike **and** nearby expiration required for promotion path.
- Numeric thesis geometry required.
- Missing Greeks → scenarios unavailable → veto.
- Scenario P&L uses quoted half-spread + commission both sides.
- High score + veto → `NO_TRADE`.
- Fixed DTE bands, no missing-data reweight, grade boundaries classified before rounding.
- Offline ingestion class raises `LiveIngestionBlocked` on fetch/order.
- Authority defaults off; saved JSON cannot claim live/paper in tests.

---

## Remaining defects (requested head)

### P0 — SAGE publication of unverified ESTABLISHED

**File:** `vector/sage/adapter.py` `_handle_established_claim` (admission-disabled branch)  
**File:** `vector/contracts/sage.py` `SageContext.as_public_dict`  
**File:** `tests/test_sage_adapter.py` `test_complete_established_does_not_admit_sage_informed_in_production`

When required fields validate and `sage_informed_admission_enabled` is False, status is still `SageStatus.ESTABLISHED`. Public dict then publishes regime, posterior, freeze, and freeze count.

**Effect on SAGE:** VECTOR does not write upstream. It *does* present an unofficial placeholder schema (`sage-unagreed-placeholder` in tests) as an established freeze.  
**Effect on VECTOR:** Confirmation points stay 0 because mode remains `BEHAVIOR_ONLY`. Board/journal readers can still treat `SAGE_STATUS=ESTABLISHED` as real.  
**Required rule:** structurally complete ≠ verified. Publish `NOT_ESTABLISHED` or a distinct `CLAIMED_UNVERIFIED` and keep `CURRENT_REGIME=null` until an agreed contract and Owner/ChatGPT admission exist.

### P0 — stub red team can PROMOTE A/A_PLUS

**File:** `vector/redteam/critique.py`  
Condition: `raw_score >= 82` and no vetoes → `RedTeamVerdict.PROMOTE` and `Disposition.RESEARCH_ELIGIBLE`.

Synthetic helper packets at this head can clear every Stage 1 gate and land in the A/A_PLUS band (full gamma + momentum + catalyst + transmission notes + tight spread + geometry). The critique labels itself `"stub critique; not a completed comprehensive red-team review"` and still promotes.

**Effect:** Promotion gate “red-team review passes” is not a review. It is a score threshold.  
**Required rule:** Stage 1 must not emit `PROMOTE` or `RESEARCH_ELIGIBLE` for live or synthetic A/A_PLUS until the required critique checklist exists.

### P1 — presence flags still pay full points

**File:** `vector/scoring/engine.py` `_score_flow`, `_score_macro`  
**File:** `vector/contracts/market.py` (via helpers)

`volume_profile_present` + poc/vah, `order_flow_present`, and `transmission_observed` + notes award full subfactor points. Notes are free text. That is the old “asserted presence” defect in a thinner form.

**Effect:** A caller can manufacture transmission and VP scores without a reproducible feature formula. Fine for offline fixtures. Unsafe for live A packets.

### P1 — quote freshness config is not the gate that runs

**File:** `vector/config.py` `FreshnessConfig.quote_max_age` (15m)  
**File:** `vector/eligibility/gates.py` quote stale path uses `chain_max_age` (20m)

`quote_max_age` is dead. Cross-input tolerance is implemented.

### P1 — OI reporting-date lag unused

**File:** `vector/config.py` `open_interest_report_lag_ok`  
**File:** `vector/eligibility/gates.py` checks OI exists and `>= 100`, not as-of date vs cutoff.

### P1 — first-order Taylor scenarios are local, not a pricing model

**File:** `vector/scoring/scenarios.py`

Documented as `first_order_greeks_taylor`. Support rule is “nearest grid node has `pnl_per_contract > 0`.” That can pass because gamma convexity on an 8% node explodes a $6 mid into a large positive. Acceptable as a disclosed research toy. Not sufficient to claim contract economics are validated for live promotion.

### P2 — OCC year pivot and root-vs-ticker

**File:** `vector/eligibility/identity.py` `_parse_yymmdd` uses `2000 + yy` only.  
Root is compared to `contract.underlying` exactly. `SPXW` vs `SPX` will veto, which is correct-strict. Adjusted-root names (BRK/B) will also veto. Stage 1 should keep the veto, not invent a mapping table.

Parser is otherwise safe for compact OSI, padded 21-char OSI, digit roots, mill strikes, invalid dates, zero strikes, and old OPRA junk.

### P2 — gamma sign points ignore candidate direction

**File:** `vector/scoring/engine.py` `_score_gamma`

`POSITIVE` regime gets 0.7 of sign max, `NEGATIVE`/`NEAR_FLIP` get 1.0, regardless of call vs put. Walls are directional. Sign bucket is not. Research-parameter issue, not a trust-boundary break.

### P2 — demo imports `tests.helpers`

**File:** `vector/demo/run_stage1.py`

Package demo depends on the test fixture module. Offline-only smell. Not a live-data path.

---

## Authority and ingestion

`vector/config.py`: paper and live false; `SAGE_INFORMED_ADMISSION_ENABLED = False`.  
`vector/pipeline.py`: if a packet arrives with paper/live true, it is forced back to defaults and vetoed.  
`vector/data/ingestion.py`: `fetch_quote`, `fetch_chain`, `submit_order` raise `LiveIngestionBlocked`. Offline accept path requires labeled synthetic provenance.

No Webull client is wired at this head. That is necessary and not sufficient for a live-ingestion GO.

---

## GO / NO_GO

| Gate | Decision | Why |
|---|---|---|
| Merge PR #1 | **NO** | Hold for audit. Dirty merge state vs `main` is irrelevant. |
| Live market-data ingestion | **NO_GO** | Unverified SAGE can still publish `ESTABLISHED`. Entitlement is unverified. Red team is a stub that promotes. Presence flags are caller-asserted. No authorized provider contract. |
| A / A_PLUS promotion | **NO_GO** | Stub `PROMOTE` on score ≥ 82 with empty veto list. Scenarios are a first-order toy. GEX may be a labeled synthetic vendor. |
| Continue offline Stage 1 fixtures | **GO** | Deterministic tests, blocked live fetch, authority off, BEHAVIOR_ONLY path works. |
| Paper or live orders | **NO_GO** | Locked. Unchanged. |

---

## Items that must stay frozen

- No SAGE write path.
- No tape → regime catalog ID.
- SIGIL ≠ SAGE.
- `BEHAVIOR_ONLY` without an established freeze.
- Fixed DTE-band weights; no interpolation; no missing-data reweight.
- No gamma points from technical substitutes.
- 14–45 EOW long premium only.
- Paper/live default off. Score is not authority.

---

## Next concrete step (implementation, not this audit)

If Owner wants the requested head to become the next review SHA:

1. Stop publishing `ESTABLISHED` when admission is closed.
2. Forbid Stage 1 `PROMOTE` / `RESEARCH_ELIGIBLE`.
3. Keep live fetch raising.
4. Do not start Webull.

Later tip `55dff75` appears to attempt (1) and (2). That tip is a different artifact and needs its own exact-head review. It does not change the verdict on `2c5a060`.
