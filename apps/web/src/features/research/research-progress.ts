export type ResearchStage = "planning" | "searching" | "reading" | "extracting" | "analyzing" | "counter-evidence" | "human-review" | "completed";

export function createResearchProgress(status: "running" | "completed" = "running") {
  const stages: ResearchStage[] = ["planning", "searching", "reading", "extracting", "analyzing", "counter-evidence", "human-review", "completed"];
  const activeIndex = status === "completed" ? stages.length : 3;
  return stages.map((id, index) => ({ id, state: index < activeIndex ? "completed" : index === activeIndex ? "active" : "pending" }));
}

export function getVisibleFindingIds<T extends { id: string; revealedAtStage: ResearchStage }>(findings: T[], currentStage: ResearchStage) {
  const stages: ResearchStage[] = ["planning", "searching", "reading", "extracting", "analyzing", "counter-evidence", "human-review", "completed"];
  const currentIndex = stages.indexOf(currentStage);
  return findings.filter((finding) => currentIndex >= stages.indexOf(finding.revealedAtStage)).map((finding) => finding.id);
}
