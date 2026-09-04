import type { ResearchPlan, ResearchSetup, ResearchSetupOptions } from "@/domain/research";

export const mockResearchSetupOptions: ResearchSetupOptions = {
  fixtureNotice: "Mock research data — for product demonstration only",
  targets: [
    { id: "industry-embodied", label: "Embodied intelligence", kind: "industry" },
    { id: "industry-agent-infra", label: "Agent infrastructure", kind: "industry" },
    { id: "technology-vla", label: "Vision-language-action models", kind: "technology" },
    { id: "technology-world-models", label: "World models", kind: "technology" },
    { id: "technology-robot-data", label: "Robot data infrastructure", kind: "technology" },
    { id: "company-figure", label: "Figure", kind: "company" },
    { id: "company-tesla", label: "Tesla Optimus", kind: "company" },
    { id: "company-physical-intelligence", label: "Physical Intelligence", kind: "company" },
  ],
  recommendedSourceTypes: ["official", "research-papers", "news", "github", "patents", "hiring"],
};

export function buildMockResearchPlan(setup: ResearchSetup): ResearchPlan {
  const topic = setup.question.replace(/[?？]+$/, "");
  const sectionTasks: Record<ResearchPlan["sections"][number]["title"], string[]> = {
    Market: ["Estimate addressable value pools and growth", "Test commercialization timing and buyer demand"],
    Technology: ["Compare VLA, world-model, and robot-data dependencies", "Assess maturity, scaling constraints, and defensibility"],
    Competition: ["Map leading companies and strategic positioning", "Identify concentration and vertical-integration pressure"],
    "Value Chain": ["Locate margin pools across model, data, simulation, hardware, and deployment", "Test build-versus-buy behavior"],
    Risk: ["Search for technical and commercial counter-evidence", "Define evidence that would disconfirm the emerging thesis"],
  };

  return {
    goal: `Build an evidence-backed answer to “${topic}” while explicitly testing competing explanations and disconfirming evidence.`,
    sections: Object.entries(sectionTasks).map(([title, questions], sectionIndex) => ({
      id: `plan-${sectionIndex + 1}`,
      title: title as ResearchPlan["sections"][number]["title"],
      tasks: questions.map((question, taskIndex) => ({
        id: `plan-${sectionIndex + 1}-task-${taskIndex + 1}`,
        question,
        priority: sectionIndex * 2 + taskIndex + 1,
        status: "pending" as const,
      })),
    })),
  };
}
