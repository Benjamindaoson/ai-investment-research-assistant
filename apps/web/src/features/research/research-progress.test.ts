import { describe, expect, it } from "vitest";

import { createResearchProgress } from "./research-progress";

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
});
