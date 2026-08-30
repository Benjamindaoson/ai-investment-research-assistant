"use client";

import { Check, ExternalLink, Search, ShieldCheck, ShieldQuestion, ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import type { Evidence, EvidenceWorkspace as Workspace } from "@/domain/research";
import { useEvidenceWorkspaceQuery, useRequestMoreResearchMutation, useReviewClaimMutation, useUpdateEvidenceStatusMutation } from "@/queries/use-evidence-workspace";

const statusLabels: Record<Evidence["verificationStatus"], string> = { unverified: "Unverified", verified: "Verified", "partially-supported": "Partially supported", conflicting: "Conflicting", "needs-review": "Needs review", rejected: "Rejected" };

export function EvidenceWorkspace({ caseId }: { caseId: string }) {
  const query = useEvidenceWorkspaceQuery(caseId);
  const updateStatus = useUpdateEvidenceStatusMutation(caseId);
  const reviewClaim = useReviewClaimMutation(caseId);
  const requestResearch = useRequestMoreResearchMutation(caseId);
  const [selectedClaimId, setSelectedClaimId] = useState("claim-data-bottleneck");
  const [researchQuestion, setResearchQuestion] = useState("");
  const [search, setSearch] = useState("");

  if (query.isPending) return <AppShell context={<EvidenceContextSkeleton />}><div className="skeleton-stack"><i /><i /><i /></div></AppShell>;
  if (query.isError) return <AppShell context={<EvidenceContextSkeleton />}><div className="error-state" role="alert"><b>Evidence Workspace could not be loaded</b><span>{query.error.message}</span><button onClick={() => query.refetch()} type="button">Try again</button></div></AppShell>;
  const data = query.data;
  const selectedClaim = data.claims.find((claim) => claim.id === selectedClaimId) ?? data.claims[0];
  const claimEvidence = data.evidence.filter((item) => selectedClaim.evidenceIds.includes(item.id) && `${item.excerpt} ${item.citation}`.toLowerCase().includes(search.toLowerCase()));
  const supporting = claimEvidence.filter((item) => item.stance === "supporting");
  const counter = claimEvidence.filter((item) => item.stance === "counter");
  const sourceById = new Map(data.sources.map((source) => [source.id, source]));

  async function askForMore() { if (researchQuestion.trim().length < 5) return; await requestResearch.mutateAsync({ claimId: selectedClaim.id, question: researchQuestion }); setResearchQuestion(""); }

  return <AppShell context={<EvidenceContext data={data} claimId={selectedClaim.id} />}>
    <header className="evidence-page-header"><div><p>EVIDENCE INTELLIGENCE</p><h1>Why does the research say this?</h1><span>Trace claims to source passages, inspect counter-evidence, and take analyst control.</span><small>{data.fixtureNotice}</small></div><label><Search size={15} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search selected claim evidence" /></label></header>
    <div className="evidence-workspace-grid">
      <aside className="claims-column"><header><small>CLAIMS</small><b>{data.claims.length}</b></header>{data.claims.map((claim) => <button type="button" key={claim.id} className={claim.id === selectedClaim.id ? "selected" : ""} onClick={() => setSelectedClaimId(claim.id)}><span className={`claim-state ${claim.status}`}>{claim.status}</span><b>{claim.statement}</b><small>{claim.evidenceIds.length} linked evidence · {Math.round(claim.confidence * 100)}% model confidence</small></button>)}</aside>
      <main className="selected-claim-column"><header><small>SELECTED CLAIM</small><h2>{selectedClaim.statement}</h2><div className="claim-actions"><button type="button" onClick={() => reviewClaim.mutate({ claimId: selectedClaim.id, decision: "approve" })}><ThumbsUp size={14} />Approve claim</button><button type="button" onClick={() => reviewClaim.mutate({ claimId: selectedClaim.id, decision: "reject" })}><ThumbsDown size={14} />Reject claim</button></div></header><EvidenceGroup title="Supporting Evidence" tone="support" items={supporting} sourceById={sourceById} onStatus={(evidenceId, status) => updateStatus.mutate({ evidenceId, status })} /><EvidenceGroup title="Counter Evidence" tone="counter" items={counter} sourceById={sourceById} onStatus={(evidenceId, status) => updateStatus.mutate({ evidenceId, status })} />{claimEvidence.length === 0 && <div className="empty-state"><b>No evidence matches this search</b><span>Clear the search to restore linked supporting and counter-evidence.</span></div>}</main>
      <aside className="evidence-actions-column"><header><small>ANALYST CONTROL</small><h2>Challenge the claim</h2></header><label>Request more research<textarea rows={4} value={researchQuestion} onChange={(event) => setResearchQuestion(event.target.value)} placeholder="What uncertainty or competing explanation should the mock research worker investigate?" /></label><button className="blue-button" type="button" disabled={researchQuestion.trim().length < 5 || requestResearch.isPending} onClick={askForMore}>Request more research</button><section><small>LATEST REVIEW ACTIONS</small>{data.reviewLog.length === 0 ? <p>No analyst action recorded yet.</p> : data.reviewLog.slice(0, 5).map((action) => <div className="review-log-row" key={action.id}><Check size={12} /><span><b>{action.summary}</b><small>{action.actor} · {new Date(action.occurredAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</small></span></div>)}</section></aside>
    </div>
  </AppShell>;
}

function EvidenceGroup({ title, tone, items, sourceById, onStatus }: { title: string; tone: "support" | "counter"; items: Evidence[]; sourceById: Map<string, Workspace["sources"][number]>; onStatus: (id: string, status: Evidence["verificationStatus"]) => void }) { return <section className={`evidence-group ${tone}`}><header><span>{tone === "support" ? <ShieldCheck size={15} /> : <ShieldQuestion size={15} />}{title}</span><b>{items.length}</b></header>{items.map((item) => { const source = sourceById.get(item.sourceId); return <article className="evidence-card" key={item.id}><div className="evidence-source"><div><small>{source?.kind.replace("-", " ")}</small><b>{source?.publisher}</b><span>{source?.title}</span></div><a href={source?.url} aria-label={`Open mock source ${source?.title}`}><ExternalLink size={14} /></a></div><blockquote>{item.excerpt}</blockquote><div className="citation-row"><span>{item.citation}</span><select value={item.verificationStatus} aria-label={`Verification status for ${item.id}`} className={`evidence-status ${item.verificationStatus}`} onChange={(event) => onStatus(item.id, event.target.value as Evidence["verificationStatus"])}>{Object.entries(statusLabels).map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></div>{source && <details><summary>Source provenance</summary><dl><dt>Author</dt><dd>{source.author ?? "Not stated"}</dd><dt>Published</dt><dd>{new Date(source.publishedAt).toLocaleDateString()}</dd><dt>Retrieved</dt><dd>{source.retrievedAt ? new Date(source.retrievedAt).toLocaleDateString() : "Not recorded"}</dd><dt>Original</dt><dd>{source.originalDocument ?? "Web source"}</dd></dl></details>}</article>; })}</section>; }
function EvidenceContext({ data, claimId }: { data: Workspace; claimId: string }) { const linked = data.claims.find((claim) => claim.id === claimId)?.evidenceIds ?? []; const evidence = data.evidence.filter((item) => linked.includes(item.id)); return <><div className="context-heading"><b>Evidence coverage</b><span>Selected claim</span></div><div className="context-summary"><small>SUPPORTING</small><b>{evidence.filter((item) => item.stance === "supporting").length}</b><small>COUNTER</small><b>{evidence.filter((item) => item.stance === "counter").length}</b><small>CONFLICTING</small><b>{evidence.filter((item) => item.verificationStatus === "conflicting").length}</b><small>NEEDS REVIEW</small><b>{evidence.filter((item) => ["unverified", "needs-review"].includes(item.verificationStatus)).length}</b></div><p className="context-note">Verification state is explainable and analyst-controlled; it is not a generic confidence score.</p></>; }
function EvidenceContextSkeleton() { return <div className="skeleton-stack compact"><i /><i /><i /></div>; }
