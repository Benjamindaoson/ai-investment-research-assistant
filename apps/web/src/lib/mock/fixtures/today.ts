import type { TodayData } from "@/domain/research";

// MOCK FIXTURE DATA: deliberately static and never presented as live research.
const companies = [
  ["northstar", "Northstar Analytics", "NSTAR"], ["nvidia", "NVIDIA", "NVDA"], ["microsoft", "Microsoft", "MSFT"],
  ["amazon", "Amazon", "AMZN"], ["alphabet", "Alphabet", "GOOGL"], ["oracle", "Oracle", "ORCL"],
  ["snowflake", "Snowflake", "SNOW"], ["palantir", "Palantir", "PLTR"], ["servicenow", "ServiceNow", "NOW"],
  ["datadog", "Datadog", "DDOG"], ["crowdstrike", "CrowdStrike", "CRWD"], ["adobe", "Adobe", "ADBE"],
] as const;

const questions = [
  "AI infrastructure margin durability", "Accelerator demand and capital intensity", "Cloud backlog conversion and pricing",
  "Enterprise software expansion efficiency", "Data-center power constraints and returns", "AI monetization beyond pilot revenue",
  "Recurring revenue quality and retention", "Competitive concentration in observability", "Security platform consolidation signals",
  "Free cash flow durability through the cycle", "Valuation sensitivity to growth normalization", "Management capital allocation discipline",
] as const;

export const mockTodayData: TodayData = {
  fixtureNotice: "Synthetic research data — product demonstration only; not investment advice",
  items: companies.map(([id, name, ticker], index) => ({
    id: `case-${id}`,
    companyId: id,
    title: questions[index],
    question: questions[index],
    status: index < 5 ? "needs-review" : index < 9 ? "in-research" : "awaiting-review",
    priority: index === 0 || index === 2 ? "high" : "medium",
    openQuestion: "What would invalidate the thesis?",
    completedWork: "Source mapping · evidence qualification",
    updatedAt: "2026-08-30T09:30:00.000Z",
    company: { id, name, ticker, sector: "AI infrastructure & software" },
  })),
  overview: {
    updatedAtLabel: "Updated 09:30",
    stats: [
      { label: "Fast research", value: 12, kind: "research" }, { label: "In progress", value: 4, kind: "progress" },
      { label: "Awaiting review", value: 3, kind: "review" }, { label: "Completed", value: 8, kind: "completed" },
    ],
    coverage: [["Cloud infrastructure", 74], ["Enterprise software", 62], ["AI applications", 51], ["Cybersecurity", 43], ["Semiconductors", 38]].map(([label, value]) => ({ label: String(label), value: Number(value) })),
    triggers: [["Earnings / guidance", 72], ["Capital expenditure", 49], ["Product release", 38], ["Policy / regulation", 20], ["Competition", 17]].map(([label, value]) => ({ label: String(label), value: Number(value) })),
    changes: [
      { id: "change-northstar", label: "Northstar Analytics", summary: "Synthetic earnings update shows improving gross margin with slower enterprise expansion.", materiality: "high" },
      { id: "change-capex", label: "AI infrastructure", summary: "Capital spending remains elevated; return-on-invested-capital evidence needs review.", materiality: "medium" },
      { id: "change-pricing", label: "Cloud pricing", summary: "Public pricing actions create a counter-case to durable software margin expansion.", materiality: "medium" },
    ],
    recent: [
      { id: "case-margin-durability", title: "AI infrastructure margin durability", status: "awaiting-review", updatedAtLabel: "Updated 2m ago" },
      { id: "case-nvidia", title: "Accelerator demand and capital intensity", status: "in-research", updatedAtLabel: "Updated 18m ago" },
      { id: "case-agent-infra", title: "Enterprise software platform layers", status: "completed", updatedAtLabel: "Completed yesterday" },
    ],
  },
};
