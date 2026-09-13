"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { useCreateRuntimeCaseMutation } from "@/queries/use-runtime-run";

export function RuntimeStartWorkspace() {
  const router = useRouter();
  const createCase = useCreateRuntimeCaseMutation();
  const [target, setTarget] = useState("ACME");
  const [question, setQuestion] = useState("Assess ACME margin durability using supporting and disconfirming evidence.");
  const configured = Boolean(process.env.NEXT_PUBLIC_RESEARCH_RUNTIME_URL);

  async function submit() {
    const result = await createCase.mutateAsync({ target, question });
    router.push(`/runtime/${result.run_id}`);
  }

  return (
    <AppShell context={<><div className="context-heading"><b>Live Research Runtime</b><span>{configured ? "Connected" : "Not configured"}</span></div><p className="context-note">The backend remains the source of truth for plan, evidence, and memo state.</p></>}>
      <div className="page-title"><div><p>LIVE RUNTIME · NEW CASE</p><h1>Start a canonical research run</h1><span>Use the durable backend workflow when a Research Runtime URL is configured.</span></div></div>
      {!configured && <div className="error-state" role="alert"><b>Research Runtime URL is not configured</b><span>Set NEXT_PUBLIC_RESEARCH_RUNTIME_URL before using this live workspace. The existing workspace remains explicitly synthetic.</span></div>}
      <section className="setup-section">
        <header><h2>Target</h2><p>Use the backend target identity for Investment Memory grouping.</p></header>
        <div><input className="text-control" value={target} onChange={(event) => setTarget(event.target.value)} aria-label="Runtime target" /></div>
      </section>
      <section className="setup-section">
        <header><h2>Investment question</h2><p>The question is hashed into the canonical research plan input.</p></header>
        <div><textarea value={question} onChange={(event) => setQuestion(event.target.value)} rows={5} aria-label="Runtime investment question" /></div>
      </section>
      {createCase.isError && <p className="form-error" role="alert">{createCase.error.message}</p>}
      <div className="form-actions"><button type="button" className="blue-button" disabled={!configured || target.trim().length === 0 || question.trim().length < 3 || createCase.isPending} onClick={submit}>{createCase.isPending ? "Creating run…" : "Create runtime case"}</button></div>
    </AppShell>
  );
}
