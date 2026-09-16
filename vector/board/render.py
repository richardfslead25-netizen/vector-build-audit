from __future__ import annotations
from vector.config import DEFAULT_AUTHORITY, RULES_VERSION
from vector.contracts.packet import ResearchPacket

def render_board_markdown(packets: list[ResearchPacket], *, cutoff: str, run_id: str) -> str:
    lines = [
        "# VECTOR Daily Options Opportunity Board", "",
        f"- run_id: `{run_id}`", f"- cutoff: `{cutoff}`",
        f"- rules_version: `{RULES_VERSION}`",
        f"- research_enabled: `{DEFAULT_AUTHORITY.research_enabled}`",
        f"- paper_execution_enabled: `{DEFAULT_AUTHORITY.paper_execution_enabled}`",
        f"- live_execution_enabled: `{DEFAULT_AUTHORITY.live_execution_enabled}`", "",
        "| Ticker | Dir | Mode | Gamma | SAGE | Score | Grade | Disposition | Vetoes | Expiry | Strike | DTE |",
        "|---|---|---|---|---|---:|---|---|---|---|---:|---:|",
    ]
    if not packets:
        lines.append("| — | — | — | — | — | — | — | NO QUALIFIED CANDIDATE | — | — | — | — |")
    for p in packets:
        row = p.to_board_row()
        lines.append(
            "| {ticker} | {direction} | {mode} | {gamma_variant} | {sage_status} | {score} | {grade} | {disposition} | {vetoes} | {expiry} | {strike} | {dte} |".format(
                ticker=row["ticker"], direction=row["direction"], mode=row["mode"],
                gamma_variant=row["gamma_variant"], sage_status=row["sage_status"],
                score="" if row["score"] is None else f"{row['score']:.2f}",
                grade=row["grade"] or "", disposition=row["disposition"],
                vetoes=",".join(row["vetoes"]) or "none",
                expiry=row["expiry"] or "",
                strike=row["strike"] if row["strike"] is not None else "",
                dte=row["dte"] if row["dte"] is not None else "",
            )
        )
    lines += ["", "## Required declaration", "", "```text",
              "LIVE_EXECUTION_AUTHORIZED = FALSE", "PAPER_EXECUTION_ENABLED = FALSE",
              "OWNER_FINAL_AUTHORITY = TRUE", "MISSING_DATA_WAS_NOT_INVENTED = TRUE",
              "GEX_VENDOR_AND_AS_OF_STAMPED = TRUE", "ORIGINAL_THESIS_PRESERVED = TRUE",
              "```", ""]
    return "\n".join(lines)
