/**
 * Workspace Page - Analysis Workspace with Tabs
 */

import { useParams, useNavigate, NavLink } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { analysisApi } from "../api/client";

export function WorkspacePage() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();

  const { data: task, isLoading, error } = useQuery({
    queryKey: ["task", taskId],
    queryFn: () => analysisApi.get(taskId!),
    enabled: !!taskId,
    refetchInterval: 5000,
  });

  if (!taskId) {
    return <ErrorMessage message="No task specified" />;
  }

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error || !task) {
    return <ErrorMessage message="Failed to load analysis" />;
  }

  const state = task.state || task.status;
  const isRunning = state === "RUNNING" || state === "running";

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 bg-white border-b border-[#E5E7EB] shrink-0">
        <div className="flex items-center justify-between mb-4">
          <div>
            <button
              onClick={() => navigate("/analyses")}
              className="text-[12px] text-[#9CA3AF] hover:text-[#1A1A2E] mb-1"
            >
              ← Back to Analyses
            </button>
            <h1 className="text-[16px] font-semibold text-[#1A1A2E]">{task.question}</h1>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge state={state} />
            {isRunning && (
              <button
                onClick={() => analysisApi.cancel(taskId)}
                className="px-3 py-1.5 text-[12px] border border-[#E5E7EB] rounded-lg hover:bg-[#F5F5F5]"
              >
                Cancel
              </button>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1">
          <NavTab to={`/analyses/${taskId}`} label="Overview" end />
          <NavTab to={`/analyses/${taskId}/investigation`} label="Investigation" />
          <NavTab to={`/analyses/${taskId}/dashboard`} label="Dashboard" />
          <NavTab to={`/analyses/${taskId}/evidence`} label="Evidence" />
          <NavTab to={`/analyses/${taskId}/report`} label="Report" />
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* Summary */}
        {task.summary && (
          <div className="bg-white rounded-xl border border-[#E5E7EB] p-6 mb-6">
            <h2 className="text-[14px] font-semibold text-[#1A1A2E] mb-3">Executive Summary</h2>
            <p className="text-[14px] text-[#6B7280] leading-relaxed">{task.summary}</p>
          </div>
        )}

        {/* Claims/Findings */}
        {task.claims && task.claims.length > 0 && (
          <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
            <div className="px-5 py-4 border-b border-[#E5E7EB]">
              <h2 className="text-[14px] font-semibold text-[#1A1A2E]">Key Findings</h2>
            </div>
            <div className="divide-y divide-[#F3F4F6]">
              {task.claims.map((claim) => (
                <div key={claim.id} className="px-5 py-4">
                  <div className="flex items-start gap-3">
                    <ClaimTypeBadge type={claim.type} />
                    <div>
                      <p className="text-[14px] text-[#1A1A2E]">{claim.text}</p>
                      {claim.confidence !== undefined && (
                        <p className="text-[12px] text-[#9CA3AF] mt-1">
                          Confidence: {Math.round(claim.confidence * 100)}%
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Running State */}
        {isRunning && (
          <div className="bg-[#DBEAFE] rounded-xl border border-[#BFDBFE] p-4">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#2563EB] animate-pulse" />
              <span className="text-[14px] text-[#1D4ED8]">AI is analyzing your data...</span>
            </div>
          </div>
        )}

        {/* Limitations */}
        {task.limitations && task.limitations.length > 0 && (
          <div className="mt-6 bg-[#FEF3C7] rounded-xl border border-[#FCD34D] p-4">
            <h3 className="text-[13px] font-semibold text-[#92400E] mb-2">Limitations</h3>
            <ul className="text-[13px] text-[#B45309] space-y-1">
              {task.limitations.map((lim, i) => (
                <li key={i}>• {lim}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Empty State */}
        {!task.summary && (!task.claims || task.claims.length === 0) && (
          <div className="bg-white rounded-xl border border-[#E5E7EB] p-8 text-center">
            <p className="text-[14px] text-[#9CA3AF]">
              {isRunning ? "Analysis in progress..." : "No findings yet"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function NavTab({ to, label, end }: { to: string; label: string; end?: boolean }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `px-4 py-2 text-[13px] rounded-lg transition-colors ${
          isActive
            ? "bg-[#00D4AA]/10 text-[#00D4AA] font-medium"
            : "text-[#6B7280] hover:bg-[#F5F5F5]"
        }`
      }
    >
      {label}
    </NavLink>
  );
}

function StatusBadge({ state }: { state?: string }) {
  const config: Record<string, { label: string; bg: string; text: string }> = {
    COMPLETED: { label: "Completed", bg: "bg-[#DCFCE7]", text: "text-[#16A34A]" },
    RUNNING: { label: "Running", bg: "bg-[#DBEAFE]", text: "text-[#2563EB]" },
    PARTIAL: { label: "Partial", bg: "bg-[#FEF3C7]", text: "text-[#D97706]" },
    FAILED: { label: "Failed", bg: "bg-[#FEE2E2]", text: "text-[#DC2626]" },
  };

  const { label, bg, text } = config[state?.toUpperCase() || ""] || {
    label: "Unknown",
    bg: "bg-[#F3F4F6]",
    text: "text-[#6B7280]",
  };

  return (
    <span className={`px-2.5 py-1 text-[12px] font-medium rounded ${bg} ${text}`}>
      {label}
    </span>
  );
}

function ClaimTypeBadge({ type }: { type: string }) {
  const config: Record<string, { label: string; bg: string; text: string }> = {
    FACT: { label: "FACT", bg: "bg-[#DCFCE7]", text: "text-[#16A34A]" },
    INFERENCE: { label: "INFERENCE", bg: "bg-[#DBEAFE]", text: "text-[#2563EB]" },
    QUALIFIED: { label: "QUALIFIED", bg: "bg-[#FEF3C7]", text: "text-[#D97706]" },
  };

  const { label, bg, text } = config[type] || {
    label: type.substring(0, 3).toUpperCase(),
    bg: "bg-[#F3F4F6]",
    text: "text-[#6B7280]",
  };

  return (
    <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${bg} ${text}`}>
      {label}
    </span>
  );
}

function LoadingSpinner() {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-[#00D4AA] border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="bg-white rounded-xl border border-[#E5E7EB] p-6 text-center">
        <p className="text-[14px] text-[#DC2626]">{message}</p>
      </div>
    </div>
  );
}
