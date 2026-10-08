"use client";

import { useState } from "react";
import type { RuntimeRun, RuntimeToolExecution } from "@/services/research-runtime-service";

type RecoveryAction = "RETRY" | "MARK_FAILED";

function attemptLabel(attempt: RuntimeToolExecution): string {
  const operation = attempt.operation?.replaceAll("_", " ").toLowerCase() ?? "tool call";
  return `${attempt.task_id} · ${operation} · ${attempt.tool_name}`;
}

export function RuntimeBlockedRecovery({ run, onResolved }: { run: RuntimeRun; onResolved: () => void }) {
  const [activeAttemptId, setActiveAttemptId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const unresolvedAttempts = run.tool_executions.filter((attempt) => attempt.status === "UNKNOWN_EFFECT" && !attempt.resolution);
  const baseUrl = process.env.NEXT_PUBLIC_RESEARCH_RUNTIME_URL?.replace(/\/$/, "");

  async function resolveAttempt(attempt: RuntimeToolExecution, action: RecoveryAction) {
    if (!baseUrl) {
      setError("Research Runtime URL is not configured.");
      return;
    }
    setError(null);
    setSuccess(null);
    setActiveAttemptId(attempt.id);
    try {
      const response = await fetch(`${baseUrl}/api/v1/research-runs/${encodeURIComponent(run.id)}/tool-attempts/${encodeURIComponent(attempt.id)}/resolve`, {
        method: "POST",
        headers: { accept: "application/json", "content-type": "application/json" },
        body: JSON.stringify({ action }),
      });
      if (!response.ok) throw new Error(`Recovery request failed with HTTP ${response.status}.`);
      setSuccess(action === "RETRY" ? "Retry authorized. Refreshing run state…" : "Attempt marked failed. Refreshing run state…");
      onResolved();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Recovery request failed.");
    } finally {
      setActiveAttemptId(null);
    }
  }

  if (run.state !== "BLOCKED") return null;

  return (
    <section className="decision-panel">
      <header>
        <div>
          <small>RECOVERY REQUIRED · UNKNOWN TOOL EFFECT</small>
          <h2>Resolve blocked tool attempts</h2>
        </div>
        <span>{unresolvedAttempts.length} unresolved attempts</span>
      </header>
      <p className="form-note">Choose Retry only when the prior tool effect is safe to repeat. Choose Mark failed when repeating could duplicate or corrupt external state.</p>
      {unresolvedAttempts.length === 0 && <p className="form-note">No unresolved UNKNOWN_EFFECT attempts remain. Refresh the run to load the latest state.</p>}
      <div className="memo-section-grid">
        {unresolvedAttempts.map((attempt) => (
          <article className="memo-section" key={attempt.id}>
            <header>
              <h3>{attemptLabel(attempt)}</h3>
              <span>{attempt.provider ?? "unknown provider"}</span>
            </header>
            <p>{attempt.error_message ?? "The runtime could not determine whether this tool call took effect."}</p>
            <small>Attempt: {attempt.id}</small>
            <div className="form-actions compact">
              <button type="button" className="outline" disabled={activeAttemptId !== null} onClick={() => { void resolveAttempt(attempt, "RETRY"); }}>
                {activeAttemptId === attempt.id ? "Resolving…" : "Retry"}
              </button>
              <button type="button" className="outline" disabled={activeAttemptId !== null} onClick={() => { void resolveAttempt(attempt, "MARK_FAILED"); }}>
                Mark failed
              </button>
            </div>
          </article>
        ))}
      </div>
      {error && <p className="form-error" role="alert">{error}</p>}
      {success && <p className="form-note" role="status">{success}</p>}
    </section>
  );
}
