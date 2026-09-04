import type { EvidenceWorkspace } from "@/domain/research";

export const mockEvidenceWorkspace: EvidenceWorkspace = {
  fixtureNotice: "Mock research data — for product demonstration only",
  caseId: "case-value-pools",
  claims: [
    { id: "claim-data-bottleneck", statement: "High-quality robot training data is becoming a binding commercialization constraint.", evidenceIds: ["ev-pi-data", "ev-hiring", "ev-synthetic"], confidence: .82, status: "supported" },
    { id: "claim-infra-value", statement: "Independent data and development infrastructure can capture durable value outside robot OEMs.", evidenceIds: ["ev-funding", "ev-vertical"], confidence: .63, status: "challenged" },
    { id: "claim-simulation", statement: "Synthetic data will complement rather than replace real-world robot data over the next three years.", evidenceIds: ["ev-paper-transfer", "ev-synthetic"], confidence: .57, status: "draft" },
  ],
  sources: [
    { id: "src-pi", title: "On general-purpose robot policies", publisher: "Physical Intelligence", author: "Research team", url: "https://example.com/mock/pi", publishedAt: "2026-06-12T00:00:00.000Z", retrievedAt: "2026-08-29T00:00:00.000Z", kind: "official", originalDocument: "Mock archived HTML" },
    { id: "src-jobs", title: "Robot data operations roles", publisher: "Representative company hiring page", url: "https://example.com/mock/jobs", publishedAt: "2026-07-08T00:00:00.000Z", retrievedAt: "2026-08-29T00:00:00.000Z", kind: "hiring" },
    { id: "src-paper", title: "Scaling synthetic-to-real transfer", publisher: "Mock Robotics Review", author: "A. Researcher et al.", url: "https://example.com/mock/paper", publishedAt: "2026-05-20T00:00:00.000Z", retrievedAt: "2026-08-28T00:00:00.000Z", kind: "paper", originalDocument: "Mock PDF · page 8" },
    { id: "src-funding", title: "Robot infrastructure financing overview", publisher: "Mock Industry Report", url: "https://example.com/mock/funding", publishedAt: "2026-08-01T00:00:00.000Z", retrievedAt: "2026-08-29T00:00:00.000Z", kind: "industry-report" },
    { id: "src-oem", title: "Integrated training platform update", publisher: "Representative robot OEM", url: "https://example.com/mock/oem", publishedAt: "2026-07-24T00:00:00.000Z", retrievedAt: "2026-08-29T00:00:00.000Z", kind: "official" },
  ],
  evidence: [
    { id: "ev-pi-data", sourceId: "src-pi", excerpt: "The mock source describes data diversity and quality as central constraints on policy generalization.", citation: "Section: Data mixture and generalization", stance: "supporting", verificationStatus: "verified" },
    { id: "ev-hiring", sourceId: "src-jobs", excerpt: "Open roles expand teleoperation, data curation, and evaluation operations across multiple deployment sites.", citation: "Roles 4–11 · accessed Aug 29", stance: "supporting", verificationStatus: "partially-supported" },
    { id: "ev-synthetic", sourceId: "src-paper", excerpt: "Large synthetic datasets reduce real-world sample needs in the reported manipulation benchmark.", citation: "Page 8 · Table 3", stance: "counter", verificationStatus: "conflicting" },
    { id: "ev-funding", sourceId: "src-funding", excerpt: "Capital formation is increasing around data collection, simulation, and robot developer tooling.", citation: "Infrastructure financing · page 14", stance: "supporting", verificationStatus: "needs-review" },
    { id: "ev-vertical", sourceId: "src-oem", excerpt: "The OEM states that its data engine and training stack are developed and operated internally.", citation: "Platform update · paragraph 6", stance: "counter", verificationStatus: "verified" },
    { id: "ev-paper-transfer", sourceId: "src-paper", excerpt: "Transfer performance deteriorates on tasks outside the synthetic generator's modeled distribution.", citation: "Page 11 · limitations", stance: "supporting", verificationStatus: "unverified" },
  ],
  reviewLog: [],
};
