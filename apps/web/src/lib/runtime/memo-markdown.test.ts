import { describe, expect, it } from "vitest";
import { memoDownloadFilename, serializeRuntimeMemo } from "./memo-markdown";
import type { RuntimeMemo } from "@/services/research-runtime-service";

const memo: RuntimeMemo = {
  id: "memo-1", run_id: "run-1", case_id: "case-1", title: "ACME memo", status: "READY_FOR_REVIEW",
  executive_summary: "Observed evidence supports review.", thesis_id: "thesis-1", claim_ids: ["claim-1"], evidence_ids: ["evidence-1"],
  counter_evidence_ids: ["evidence-2"], unresolved_requirement_ids: ["requirement-1"], ic_review_ids: [],
  sections: [{ section_key: "thesis", title: "Investment thesis", body: "Observed thesis.", claim_ids: ["claim-1"], evidence_ids: ["evidence-1"], unresolved_requirement_ids: [] }],
  provenance: { generator: "test" }, generated_at: "2026-09-14T00:00:00.000Z",
};

describe("memo-markdown", () => {
  it("serializes review state and evidence references without inventing citations", () => {
    const output = serializeRuntimeMemo({ id: "run-1", state: "COMPLETED", memo });
    expect(output).toContain("Memo status: READY_FOR_REVIEW");
    expect(output).toContain("Observed thesis.");
    expect(output).toContain("evidence-1");
    expect(output).toContain("Counter/conflicting evidence IDs:");
    expect(output).toContain("IC review IDs:");
    expect(output).toContain("requirement-1");
    expect(output).toContain("not a price target, investment advice");
  });

  it("sanitizes the run identifier in the download filename", () => {
    expect(memoDownloadFilename("run/../unsafe id")).toBe("investment-memo-run-unsafe-id.md");
  });
});
