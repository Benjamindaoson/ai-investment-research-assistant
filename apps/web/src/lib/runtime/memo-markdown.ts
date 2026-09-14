import type { RuntimeMemo, RuntimeRun } from "@/services/research-runtime-service";

export function serializeRuntimeMemo(run: Pick<RuntimeRun, "id" | "state"> & { memo: RuntimeMemo }): string {
  const memo = run.memo;
  const list = (items: string[]) => items.length ? items.map((item) => `- ${item}`).join("\n") : "- None recorded";
  const sections = memo.sections.map((section) => [
    `### ${section.title}`,
    section.body,
    `Claims: ${list(section.claim_ids)}`,
    `Evidence: ${list(section.evidence_ids)}`,
    `Unresolved requirements: ${list(section.unresolved_requirement_ids)}`,
  ].join("\n\n")).join("\n\n");
  return [
    "# Investment Memo", `- Run: ${run.id}`, `- Run state: ${run.state}`, `- Memo status: ${memo.status}`, `- Memo ID: ${memo.id}`, "",
    "## Executive summary", memo.executive_summary, "", "## Thesis reference", `Thesis ID: ${memo.thesis_id}`, `Claim IDs: ${list(memo.claim_ids)}`, "",
    "## Structured sections", sections || "No structured sections recorded.", "", "## Evidence references",
    `Supporting evidence IDs:\n${list(memo.evidence_ids)}`, `Counter/conflicting evidence IDs:\n${list(memo.counter_evidence_ids)}`, `Unresolved requirement IDs:\n${list(memo.unresolved_requirement_ids)}`, `IC review IDs:\n${list(memo.ic_review_ids)}`, "",
    "## Provenance", "```json", JSON.stringify(memo.provenance, null, 2), "```", "",
    "> This is a durable research projection, not a price target, investment advice, or a substitute for human review.", "",
  ].join("\n");
}

export function memoDownloadFilename(runId: string): string {
  const safeId = runId.replace(/[^a-zA-Z0-9_-]+/g, "-").replace(/^-+|-+$/g, "") || "run";
  return `investment-memo-${safeId}.md`;
}
