import type { TodayData } from "@/domain/research";

// MOCK FIXTURE DATA: deliberately static and never presented as live research.
const companies = [
  ["nvidia", "NVIDIA", "NVDA"], ["figure", "Figure", "FIGURE"], ["tesla", "Tesla Optimus", "TSLA"],
  ["physical-intelligence", "Physical Intelligence", "PI"], ["agibot", "智元机器人", "AGIBOT"],
  ["unitree", "Unitree", "UNITREE"], ["openai", "OpenAI", "OPENAI"], ["anthropic", "Anthropic", "ANTHROPIC"],
  ["boston-dynamics", "Boston Dynamics", "BD"], ["agility", "Agility Robotics", "AGILITY"],
  ["sanctuary", "Sanctuary AI", "SANCTUARY"], ["apptronik", "Apptronik", "APPTRONIK"],
] as const;

const questions = [
  "Robotics compute demand and capex signal", "Humanoid deployment and enterprise pilots", "Manufacturing learning curve and dexterity",
  "Foundation models for robot control", "China supply-chain and rollout momentum", "Cost-down path and developer ecosystem",
  "Model roadmap for embodied agents", "Reliable-agent infrastructure signals", "Commercial deployment readiness",
  "Warehouse automation economics", "Task reliability and labor economics", "Manufacturing scale-up and partnerships",
] as const;

export const mockTodayData: TodayData = {
  fixtureNotice: "Mock research data — for product demonstration only",
  items: companies.map(([id, name, ticker], index) => ({
    id: `case-${id}`,
    companyId: id,
    title: questions[index],
    question: questions[index],
    status: index < 5 ? "needs-review" : index < 9 ? "in-research" : "awaiting-review",
    priority: index === 0 || index === 2 ? "high" : "medium",
    openQuestion: "What changes the thesis?",
    completedWork: "Source scan · evidence extraction",
    updatedAt: "2026-08-30T09:30:00.000Z",
    company: { id, name, ticker, sector: "AI & embodied intelligence" },
  })),
  overview: {
    updatedAtLabel: "Updated 09:30",
    stats: [
      { label: "Fast research", value: 12, kind: "research" }, { label: "In progress", value: 4, kind: "progress" },
      { label: "Awaiting review", value: 3, kind: "review" }, { label: "Completed", value: 8, kind: "completed" },
    ],
    coverage: [["Humanoid robotics", 74], ["Agent infrastructure", 52], ["Foundation models", 47], ["Industrial AI", 36], ["Compute", 28]].map(([label, value]) => ({ label: String(label), value: Number(value) })),
    triggers: [["Deployment signal", 72], ["Capital / funding", 49], ["Technical release", 38], ["Policy / regulation", 20], ["Competition", 17]].map(([label, value]) => ({ label: String(label), value: Number(value) })),
  },
};
