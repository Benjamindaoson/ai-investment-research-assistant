import { RuntimeRunWorkspace } from "@/components/runtime/runtime-run-workspace";

export default async function RuntimeRunPage({ params }: { params: Promise<{ runId: string }> }) {
  const { runId } = await params;
  return <RuntimeRunWorkspace runId={runId} />;
}
