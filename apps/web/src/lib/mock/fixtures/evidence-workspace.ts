import type { EvidenceWorkspace } from "@/domain/research";

export const mockEvidenceWorkspace: EvidenceWorkspace = {
  fixtureNotice: "Synthetic research data — product demonstration only; not investment advice",
  caseId: "case-margin-durability",
  claims: [
    { id: "claim-margin-pool", statement: "AI infrastructure demand can support a durable gross-margin pool, but free-cash-flow durability depends on capital intensity.", evidenceIds: ["ev-demand", "ev-margin", "ev-capex"], confidence: .82, status: "supported" },
    { id: "claim-platform-power", statement: "Mission-critical workflows can create switching costs that protect independent platform economics.", evidenceIds: ["ev-retention", "ev-workload"], confidence: .63, status: "challenged" },
    { id: "claim-pricing", statement: "Cloud bundling and open alternatives may compress standalone software pricing over the next three years.", evidenceIds: ["ev-pricing", "ev-bundle"], confidence: .57, status: "draft" },
  ],
  sources: [
    { id: "src-filing", title: "Quarterly filing and investor presentation", publisher: "Synthetic public-company filing", author: "Investor relations", url: "https://example.com/mock/filing", publishedAt: "2026-06-12T00:00:00.000Z", retrievedAt: "2026-08-29T00:00:00.000Z", kind: "official", originalDocument: "Synthetic archived filing" },
    { id: "src-transcript", title: "Earnings call transcript", publisher: "Synthetic public-company transcript", url: "https://example.com/mock/transcript", publishedAt: "2026-07-08T00:00:00.000Z", retrievedAt: "2026-08-29T00:00:00.000Z", kind: "filing" },
    { id: "src-paper", title: "Measuring infrastructure utilization and returns", publisher: "Synthetic Finance Review", author: "A. Researcher et al.", url: "https://example.com/mock/paper", publishedAt: "2026-05-20T00:00:00.000Z", retrievedAt: "2026-08-28T00:00:00.000Z", kind: "paper", originalDocument: "Synthetic PDF · page 8" },
    { id: "src-industry", title: "Cloud infrastructure pricing survey", publisher: "Synthetic Industry Report", url: "https://example.com/mock/industry", publishedAt: "2026-08-01T00:00:00.000Z", retrievedAt: "2026-08-29T00:00:00.000Z", kind: "industry-report" },
    { id: "src-competitor", title: "Bundled platform product update", publisher: "Synthetic cloud provider", url: "https://example.com/mock/competitor", publishedAt: "2026-07-24T00:00:00.000Z", retrievedAt: "2026-08-29T00:00:00.000Z", kind: "official" },
  ],
  evidence: [
    { id: "ev-demand", sourceId: "src-filing", excerpt: "The synthetic filing describes workload growth and contracted demand as central drivers of the next planning cycle.", citation: "Business outlook · page 4", stance: "supporting", verificationStatus: "verified" },
    { id: "ev-margin", sourceId: "src-filing", excerpt: "Reported gross margin expands with scale, while depreciation and capacity commitments remain material.", citation: "Financial statements · page 18", stance: "supporting", verificationStatus: "partially-supported" },
    { id: "ev-capex", sourceId: "src-paper", excerpt: "Returns deteriorate when capacity is built ahead of utilization and contracted workload conversion.", citation: "Page 8 · Table 3", stance: "counter", verificationStatus: "conflicting" },
    { id: "ev-retention", sourceId: "src-transcript", excerpt: "Customers describe embedded workflows and migration friction, but renewal data is not independently disclosed.", citation: "Earnings call · question 7", stance: "supporting", verificationStatus: "needs-review" },
    { id: "ev-workload", sourceId: "src-transcript", excerpt: "Mission-critical workloads increase integration depth and the cost of switching providers.", citation: "Earnings call · prepared remarks", stance: "supporting", verificationStatus: "verified" },
    { id: "ev-pricing", sourceId: "src-industry", excerpt: "Survey respondents report increasing pressure to consolidate infrastructure spend with strategic vendors.", citation: "Pricing survey · page 11", stance: "counter", verificationStatus: "verified" },
    { id: "ev-bundle", sourceId: "src-competitor", excerpt: "The provider positions adjacent capabilities as a bundled alternative to standalone tools.", citation: "Product update · paragraph 6", stance: "counter", verificationStatus: "unverified" },
  ],
  reviewLog: [],
};
