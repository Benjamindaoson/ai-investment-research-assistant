"""Render a persisted ResearchRun snapshot into a readable local investment memo PDF."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def text(value: object) -> str:
    return escape(str(value or "").replace("\u2013", "-").replace("\u2014", "-"))


class StatusBanner(Flowable):
    def __init__(self, label: str, good: bool) -> None:
        super().__init__()
        self.label = label
        self.good = good
        self.width = 7.1 * inch
        self.height = 0.34 * inch

    def draw(self) -> None:
        self.canv.setFillColor(colors.HexColor("#E6F4EA" if self.good else "#FFF4E5"))
        self.canv.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=0)
        self.canv.setFillColor(colors.HexColor("#176B3A" if self.good else "#9A5A00"))
        self.canv.setFont("Helvetica-Bold", 9)
        self.canv.drawString(12, 9, self.label)


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("ReportTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=25, leading=30, textColor=colors.HexColor("#172033"), alignment=TA_LEFT, spaceAfter=8),
        "subtitle": ParagraphStyle("Subtitle", parent=base["Normal"], fontName="Helvetica", fontSize=10, leading=15, textColor=colors.HexColor("#5C667A"), spaceAfter=14),
        "h1": ParagraphStyle("H1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=colors.HexColor("#172033"), spaceBefore=16, spaceAfter=8),
        "h2": ParagraphStyle("H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=colors.HexColor("#23436B"), spaceBefore=9, spaceAfter=5),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#263044"), spaceAfter=7),
        "small": ParagraphStyle("Small", parent=base["BodyText"], fontName="Helvetica", fontSize=7.5, leading=10, textColor=colors.HexColor("#5C667A")),
        "callout": ParagraphStyle("Callout", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=colors.HexColor("#172033"), backColor=colors.HexColor("#F1F5F9"), borderColor=colors.HexColor("#D7DEE8"), borderWidth=0.5, borderPadding=8, spaceAfter=8),
        "table": ParagraphStyle("Table", parent=base["BodyText"], fontName="Helvetica", fontSize=7.2, leading=9, textColor=colors.HexColor("#263044")),
        "table_head": ParagraphStyle("TableHead", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.2, leading=9, textColor=colors.white),
    }


def table(data: list[list[object]], widths: list[float], style: dict[str, object]) -> Table:
    converted = [[Paragraph(text(cell), style["table_head"] if row == 0 else style["table"]) for cell in row] for row in data]
    result = Table(converted, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#23436B")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7DEE8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FC")]),
    ]))
    return result


def build(snapshot: dict[str, object], output: Path) -> None:
    case = snapshot.get("case") or {}
    run = snapshot["run"]
    events = snapshot.get("events", [])
    memo = run.get("memo")
    thesis = run.get("thesis")
    evidence = run.get("evidence", [])
    claims = run.get("claims", [])
    tasks = run.get("tasks", [])
    receipts = [item for item in run.get("tool_executions", []) if item.get("operation") == "CLAIM_VERIFICATION"]
    completion_events = {item.get("payload", {}).get("claim_id"): item.get("payload", {}) for item in events if item.get("event_type") == "CLAIM_VERIFICATION_COMPLETED"}
    s = styles()
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=letter, rightMargin=0.7 * inch, leftMargin=0.7 * inch, topMargin=0.65 * inch, bottomMargin=0.6 * inch, title=f"Investment memo - {run.get('case_id')}")
    story: list[object] = []
    ready = run.get("state") == "COMPLETED" and memo and memo.get("status") == "READY_FOR_REVIEW"
    story.append(Paragraph("Financial Deep Research Investment Memo", s["title"]))
    story.append(Paragraph(f"Target: <b>{text(case.get('target') or run.get('case_id'))}</b> | Run: {text(run.get('id'))}", s["subtitle"]))
    story.append(StatusBanner("READY FOR HUMAN REVIEW" if ready else "DRAFT - HUMAN REVIEW REQUIRED", bool(ready)))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Research mandate", s["h1"]))
    story.append(Paragraph(text(case.get("question") or snapshot.get("run", {}).get("plan", {}).get("question", "Research question unavailable.")), s["callout"]))
    story.append(Paragraph(f"Run state: <b>{text(run.get('state'))}</b> &nbsp;&nbsp; Memo status: <b>{text(memo.get('status') if memo else 'NOT GENERATED')}</b>", s["body"]))

    story.append(Paragraph("Executive conclusion", s["h1"]))
    story.append(Paragraph(text(memo.get("executive_summary") if memo else "No executive summary was produced."), s["callout"]))
    if thesis:
        story.append(Paragraph("Thesis and scenarios", s["h1"]))
        story.append(table([["Thesis", "Bull", "Base", "Bear"], [thesis.get("statement", ""), thesis.get("bull", ""), thesis.get("base", ""), thesis.get("bear", "")]], [1.75 * inch, 1.75 * inch, 1.75 * inch, 1.75 * inch], s))

    qualified = sum(item.get("qualification") == "QUALIFIED" for item in evidence)
    counter = sum(item.get("stance") in {"COUNTER", "CONFLICTING"} for item in evidence)
    provenance = sum(bool(item.get("source_url") and item.get("locator") and item.get("content_hash")) for item in evidence)
    story.append(Paragraph("Evidence quality", s["h1"]))
    story.append(table([["Observed", "Qualified", "Counter/conflicting", "Complete provenance"], [len(evidence), qualified, counter, f"{provenance}/{len(evidence)}"]], [1.6 * inch] * 4, s))
    story.append(Paragraph("Qualification is an evidence service/runtime result, not a statement that the investment thesis is true. Counter-evidence remains visible in the memo.", s["small"]))

    story.append(Paragraph("Evidence-linked claims", s["h1"]))
    claim_rows = [["Task", "Status", "Claim", "Evidence"]]
    for claim in claims:
        claim_rows.append([claim.get("task_id", ""), claim.get("status", ""), claim.get("statement", ""), len(claim.get("evidence_ids", []))])
    story.append(table(claim_rows, [1.0 * inch, 0.85 * inch, 4.35 * inch, 0.8 * inch], s))

    story.append(Paragraph("Claim verification receipts", s["h1"]))
    verification_rows = [["Claim", "Supported", "Status", "Provider", "Reason"]]
    for receipt in receipts:
        claim_id = receipt.get("claim_id") or next((key for key, value in completion_events.items() if value.get("attempt_id") == receipt.get("id")), "unresolved")
        event = completion_events.get(claim_id, {})
        verification_rows.append([claim_id, event.get("supported", receipt.get("verification_supported")), receipt.get("status"), receipt.get("provider"), "Unsupported by external verifier" if event.get("supported") is False else receipt.get("error_message") or "No bounded diagnostic"])
    if len(verification_rows) == 1:
        verification_rows.append(["None recorded", "N/A", "N/A", "N/A", "No claim verification receipt was persisted"])
    story.append(table(verification_rows, [1.35 * inch, 0.75 * inch, 0.7 * inch, 1.55 * inch, 2.75 * inch], s))
    story.append(Paragraph("A claim that is not externally supported remains a review item. This report does not promote it to an investment conclusion.", s["small"]))

    story.append(Paragraph("Structured memo sections", s["h1"]))
    if memo:
        for section in memo.get("sections", []):
            story.append(KeepTogether([Paragraph(text(section.get("title")), s["h2"]), Paragraph(text(section.get("body")), s["body"]), Paragraph(f"Claims: {len(section.get('claim_ids', []))} | Evidence: {len(section.get('evidence_ids', []))} | Unresolved requirements: {len(section.get('unresolved_requirement_ids', []))}", s["small"])]))
    else:
        story.append(Paragraph("No memo sections recorded.", s["body"]))

    story.append(PageBreak())
    story.append(Paragraph("Research plan and source appendix", s["h1"]))
    task_rows = [["Task", "State", "Tool", "Evidence requirements"]]
    for task in tasks:
        task_rows.append([task.get("title", task.get("id", "")), task.get("state", ""), task.get("tool_name", ""), len(task.get("evidence_requirements", []))])
    story.append(table(task_rows, [3.4 * inch, 0.8 * inch, 1.2 * inch, 1.0 * inch], s))
    story.append(Spacer(1, 10))
    evidence_rows = [["Evidence ID", "Stance", "Qualification", "Source", "Locator"]]
    for item in evidence:
        evidence_rows.append([item.get("id", ""), item.get("stance", ""), item.get("qualification", ""), item.get("source_title", item.get("source_id", "")), item.get("locator", "")])
    story.append(table(evidence_rows, [1.45 * inch, 0.8 * inch, 1.05 * inch, 2.45 * inch, 1.35 * inch], s))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Source provenance and review boundary", s["h1"]))
    story.append(Paragraph("Evidence records retain source identity, URL, locator, content hash, and provider provenance in the durable runtime. This memo is an auditable research artifact, not a price target, personalized investment advice, or a substitute for analyst and investment committee review.", s["body"]))

    def footer(canvas, document) -> None:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D7DEE8"))
        canvas.line(0.7 * inch, 0.42 * inch, 7.8 * inch, 0.42 * inch)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawString(0.7 * inch, 0.25 * inch, "Financial Deep Research Runtime - evidence-first memo")
        canvas.drawRightString(7.8 * inch, 0.25 * inch, f"Page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(json.loads(args.snapshot.read_text(encoding="utf-8")), args.output)
    print(json.dumps({"output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
