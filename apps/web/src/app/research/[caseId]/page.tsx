import { ResearchCaseWorkspace } from "@/components/research/research-case-workspace";

export default async function ResearchCasePage({ params }: { params: Promise<{ caseId: string }> }) {
  const { caseId } = await params;
  return <ResearchCaseWorkspace caseId={caseId} />;
}
