# Merge brief — VECTOR Stage 1 + Momentum Option Scanner

Date: 2026-09-15 PT
Owner: Richard
Authors of notes: Grok (this desk)

## What is being combined

1. VECTOR Stage 1 quantitative options research engine
   Repo: https://github.com/richardfslead25-netizen/vector-build-audit
   Branch: `build/stage-1-contracts`
   PR #1 HOLD — do not merge into production execution
   Audit SHA (GPT asked): `2c5a06050e09f05aba774004568513d8ee2d1a41`
   Later lock commits exist on the same branch after that SHA

2. Momentum Option Scanner (sibling Grok skill)
   Hunt layer: unusual flow, Webull tool map, H&S / reversal patterns, universe gather
   Must NOT be imported as the SAGE layer

Related desk: https://github.com/richardfslead25-netizen/market-agent-desk

## Locked authority for any merge build

```
RESEARCH_ENABLED = true
PAPER_EXECUTION_ENABLED = false
LIVE_EXECUTION_ENABLED = false
VECTOR_WRITES_TO_SAGE = false
SAGE_INFORMED_ADMISSION_ENABLED = false
```

Do not invent SAGE. Do not treat SIGIL as SAGE. Do not authorize paper or live. Do not merge PR #1 as execution authority.

## Grok audit of 2c5a060 (summary)

P0 open on that SHA:
- Settings.sage_informed_admission_enabled is caller-settable
- Complete unverified SAGE claims still status=ESTABLISHED
- as_public_dict publishes regime when ESTABLISHED
- accept_snapshot accepts non-synthetic data if VECTOR_OFFLINE=0
- receipt may precede cutoff; posterior allows 1.04 and coerced bools

P0 eligibility mostly closed: timestamps, DTE, listings, OCC, coherence.
P1 open: nearby comparison is not identity-safe; red team stub can PROMOTE.
OCC parser at 2c5a060: safe enough for listed equity OSI.
Verdict on 2c5a060: STAGE_1_CORRECTIONS_REQUIRED. NO_GO live ingestion. NO_GO A/A_PLUS.

## Take from VECTOR (contract wins)

Single-agent 15-step process. Downstream-only SAGE. NOT_ESTABLISHED valid. Fusion cannot be CONSISTENT while SAGE null/unverified. Sage-confirmation requires verified_established + SAGE_INFORMED + CONSISTENT. Fixed DTE bands, no interpolation. Vendor GEX or zero gamma. Hard vetoes. EOW 14-45. Scenarios need Greeks. OCC identity. Empty boards valid. Stage 1 red team cannot PROMOTE.

## Take from Momentum Scanner (hunt layer only)

Unusual flow source list. Webull tool map for later Stage 2 entitlement (not now). Account crowding notes. H&S / reversal checklist. Universe gathering. Three-number display as labels only — do not replace VECTOR weights.

## Do not import from the scanner

Mandatory SIGIL-first bias. Catalog IDs from a web app. Reconstructed flow as SAGE confirmation. 14-30-only universe. 0.50/0.30/0.20 blend. Broker preview or orders.

## Target architecture

```
SAGE official freeze or explicit NOT_ESTABLISHED
        → market-behavior engine (tape, vol, RS, patterns, flow-as-hypothesis)
        → fusion CONSISTENT | INCONSISTENT | INSUFFICIENT
        → VECTOR eligibility + DTE-band score + scenarios + red team
        → board
```

Hunt layer may propose tickers. VECTOR decides gates, score, and disposition.

## Definition of done

1. SAGE admission cannot be enabled by ordinary Settings.
2. Unverified claims never publish as ESTABLISHED.
3. accept_snapshot requires synthetic + stage1-synthetic-only + VECTOR_STAGE=1.
4. Nearby alts same underlying, same right, proximity, freshness.
5. Red team cannot PROMOTE in Stage 1.
6. Scanner hunt helpers cannot mint a regime.
7. Tests green offline. No Webull client. No orders.
8. Docs match code.
