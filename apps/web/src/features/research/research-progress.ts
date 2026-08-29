export type ResearchStage = "planning" | "searching" | "reading" | "extracting" | "analyzing" | "counter-evidence" | "human-review" | "completed";

export function createResearchProgress(status: "running" | "completed" = "running") {
  const stages: ResearchStage[] = ["planning", "searching", "reading", "extracting", "analyzing", "counter-evidence", "human-review", "completed"];
  const activeIndex = status === "completed" ? stages.length : 3;
  return stages.map((id, index) => ({ id, state: index < activeIndex ? "completed" : index === activeIndex ? "active" : "pending" }));
}
