import { describe, expect, it } from "vitest";

import { createResearchProgress, getVisibleFindingIds } from "./research-progress";

describe("createResearchProgress", () => {
  it("reveals research stages in the evidence-first workflow order", () => {
    expect(createResearchProgress("running").map((step) => step.id)).toEqual([
      "planning",
      "searching",
      "reading",
      "extracting",
      "analyzing",
      "counter-evidence",
      "human-review",
      "completed",
    ]);
  });

  it("reveals findings only after their evidence-producing stage", () => {
    const findings = [
      { id: "evidence", revealedAtStage: "extracting" as const },
      { id: "analysis", revealedAtStage: "analyzing" as const },
      { id: "counter", revealedAtStage: "counter-evidence" as const },
    ];
    expect(getVisibleFindingIds(findings, "reading")).toEqual([]);
    expect(getVisibleFindingIds(findings, "analyzing")).toEqual(["evidence", "analysis"]);
    expect(getVisibleFindingIds(findings, "completed")).toEqual(["evidence", "analysis", "counter"]);
  });
});
