import { RuntimeCaseBridge } from "@/components/runtime/runtime-case-bridge";

export default async function ResearchCasePage({ params }: { params: Promise<{ caseId: string }> }) {
  const { caseId } = await params;
  return <RuntimeCaseBridge caseId={caseId} />;
}
