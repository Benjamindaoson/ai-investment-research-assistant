import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";

export default async function ResearchCasePage({ params }: { params: Promise<{ caseId: string }> }) {
  const { caseId } = await params;
  return <AppShell context={<div className="context-heading"><b>Research case</b><span>Mock handoff</span></div>}><div className="page-title"><div><p>RESEARCH CASE · {caseId}</p><h1>Research created</h1><span>The setup and editable plan have been accepted by the mock service.</span><small className="fixture-notice">Mock research data — for product demonstration only</small></div></div><div className="empty-state"><b>Research execution is ready to begin</b><span>The next implementation batch adds the streaming timeline, plan controls, and progressive findings to this case route.</span><Link className="link-button" href="/new-research">Review another setup</Link></div></AppShell>;
}
