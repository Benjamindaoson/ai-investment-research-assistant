import type { ResearchPlan, ResearchSetup, ResearchSetupOptions } from "@/domain/research";

export const mockResearchSetupOptions: ResearchSetupOptions = {
  fixtureNotice: "Synthetic research data — product demonstration only; not investment advice",
  targets: [
    { id: "industry-software", label: "Enterprise software", kind: "industry" },
    { id: "industry-infrastructure", label: "Cloud infrastructure", kind: "industry" },
    { id: "technology-ai-infra", label: "AI infrastructure", kind: "technology" },
    { id: "technology-observability", label: "Observability platforms", kind: "technology" },
    { id: "technology-cybersecurity", label: "Cybersecurity", kind: "technology" },
    { id: "company-northstar", label: "Northstar Analytics", kind: "company" },
    { id: "company-nvidia", label: "NVIDIA", kind: "company" },
    { id: "company-microsoft", label: "Microsoft", kind: "company" },
  ],
  recommendedSourceTypes: ["official", "research-papers", "news", "filings", "transcripts", "industry-reports"],
};

export function buildMockResearchPlan(setup: ResearchSetup): ResearchPlan {
  const topic = setup.question.replace(/[?？]+$/, "");
  const sectionTasks: Record<ResearchPlan["sections"][number]["title"], string[]> = {
    Market: ["Estimate addressable demand and durable growth drivers", "Test customer willingness to pay and adoption timing"],
    Technology: ["Assess infrastructure requirements and operating leverage", "Separate product capability from measurable customer outcomes"],
    Competition: ["Map public-company positioning and switching costs", "Identify concentration, substitutes, and pricing pressure"],
    "Value Chain": ["Locate gross-margin pools across hardware, cloud, and software", "Test build-versus-buy behavior and supplier dependence"],
    Risk: ["Search for financial, competitive, and execution counter-evidence", "Define evidence that would disconfirm the emerging thesis"],
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
