/**
 * Today Page - Home with AI Query Interface
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { homeApi, analysisApi, ApiError } from "../api/client";

export function TodayPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [question, setQuestion] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: homeData } = useQuery({
    queryKey: ["home"],
    queryFn: homeApi.get,
    refetchInterval: 30000,
  });

  const { data: analysesData } = useQuery({
    queryKey: ["analyses"],
    queryFn: analysisApi.list,
    refetchInterval: 10000,
  });

  const createAnalysis = useMutation({
    mutationFn: (q: string) => analysisApi.create({ question: q }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["analyses"] });
      navigate(`/analyses/${data.id}`);
    },
    onError: (err: ApiError) => {
      setError(err.message || "Failed to create analysis");
      setIsSubmitting(false);
    },
  });

  const handleSubmit = () => {
    if (!question.trim()) return;
    setError(null);
    setIsSubmitting(true);
    createAnalysis.mutate(question.trim());
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuestion(suggestion);
    setIsSubmitting(true);
    createAnalysis.mutate(suggestion);
  };

  const recentAnalyses = (analysesData?.items || []).slice(0, 5);
  const dataset = homeData?.dataset;
  const metrics = homeData?.metrics || [];

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-5xl mx-auto">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-[24px] font-semibold text-[#1A1A2E] mb-1">
            Enterprise Intelligence
          </h1>
          <p className="text-[14px] text-[#6B7280]">
            Ask questions about your data in natural language
          </p>
        </div>

        {/* Query Input Card */}
        <div className="bg-white rounded-xl border border-[#E5E7EB] p-6 mb-6 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-[#00D4AA]/10 rounded-lg flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 2L3 6v6l7 4 7-4V6l-7-4z" stroke="#00D4AA" strokeWidth="1.5"/>
                <path d="M10 10v4M7 8l7 4M13 8l-7 4" stroke="#00D4AA" strokeWidth="1.5"/>
              </svg>
            </div>
            <div>
              <h2 className="text-[16px] font-semibold text-[#1A1A2E]">Ask a Question</h2>
              <p className="text-[12px] text-[#9CA3AF]">Get AI-powered analysis of your business data</p>
            </div>
          </div>

          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
            placeholder="e.g., Compare July 2026 sales with June 2026..."
            rows={3}
            disabled={isSubmitting}
            className="w-full px-4 py-3 text-[14px] border border-[#E5E7EB] rounded-lg resize-none outline-none focus:border-[#00D4AA] focus:ring-2 focus:ring-[#00D4AA]/20 disabled:opacity-50"
          />

          {/* Quick Suggestions */}
          <div className="flex flex-wrap gap-2 mt-4">
            {metrics.slice(0, 4).map((m) => (
              <button
                key={m.id}
                onClick={() => setQuestion(`Show ${m.label?.toLowerCase() || 'data'} trends`)}
                className="px-3 py-1.5 text-[12px] bg-[#F5F5F5] text-[#1A1A2E] rounded-full hover:bg-[#E5E7EB] transition-colors"
              >
                {m.label || 'Metric'}
              </button>
            ))}
          </div>

          {error && (
            <div className="mt-4 p-3 bg-[#FEE2E2] border border-[#FECACA] rounded-lg text-[13px] text-[#DC2626]">
              {error}
            </div>
          )}

          <div className="flex items-center justify-between mt-4 pt-4 border-t border-[#E5E7EB]">
            <span className="text-[12px] text-[#9CA3AF]">
              Press Enter to submit
            </span>
            <button
              onClick={handleSubmit}
              disabled={!question.trim() || isSubmitting}
              className="px-6 py-2.5 bg-[#00D4AA] text-white text-[14px] font-medium rounded-lg hover:bg-[#00B894] disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isSubmitting ? "Analyzing..." : "Ask AI"}
            </button>
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Analyses */}
          <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
            <div className="px-5 py-4 border-b border-[#E5E7EB] flex items-center justify-between">
              <h3 className="text-[14px] font-semibold text-[#1A1A2E]">Recent Analyses</h3>
              <button
                onClick={() => navigate("/analyses")}
                className="text-[12px] text-[#00D4AA] hover:underline"
              >
                View all
              </button>
            </div>
            <div className="divide-y divide-[#F3F4F6]">
              {recentAnalyses.length === 0 ? (
                <div className="p-8 text-center text-[13px] text-[#9CA3AF]">
                  No analyses yet. Ask a question above to get started.
                </div>
              ) : (
                recentAnalyses.map((analysis) => (
                  <button
                    key={analysis.id}
                    onClick={() => navigate(`/analyses/${analysis.id}`)}
                    className="w-full text-left px-5 py-3 hover:bg-[#F9FAFB] transition-colors"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[13px] text-[#1A1A2E] truncate flex-1 mr-4">
                        {analysis.question || 'Untitled analysis'}
                      </span>
                      <StatusBadge state={analysis.state || analysis.status} />
                    </div>
                    <span className="text-[11px] text-[#9CA3AF]">
                      {analysis.createdAt ? new Date(analysis.createdAt).toLocaleDateString() : '—'}
                    </span>
                  </button>
                ))
              )}
            </div>
          </div>

          {/* System Status */}
          <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
            <div className="px-5 py-4 border-b border-[#E5E7EB]">
              <h3 className="text-[14px] font-semibold text-[#1A1A2E]">System Status</h3>
            </div>
            <div className="p-5 space-y-4">
              <StatusRow
                label="Dataset"
                value={dataset?.available ? "Loaded" : "Not loaded"}
                status={dataset?.available ? "success" : "warning"}
              />
              <StatusRow
                label="Snapshot"
                value={dataset?.snapshot_id || "—"}
                status="neutral"
              />
              <StatusRow
                label="Records"
                value={dataset?.measured_row_count?.toLocaleString() || "—"}
                status="neutral"
              />
              <StatusRow
                label="Date Range"
                value={dataset?.measured_business_date_min && dataset?.measured_business_date_max
                  ? `${dataset.measured_business_date_min} - ${dataset.measured_business_date_max}`
                  : "—"}
                status="neutral"
              />
              <StatusRow
                label="Metrics Available"
                value={metrics.length.toString()}
                status="success"
              />

              {!dataset?.available && (
                <div className="mt-4 p-3 bg-[#FEF3C7] rounded-lg text-[12px] text-[#92400E]">
                  Run <code className="bg-[#FEF3C7] px-1 rounded">make data</code> to load the dataset
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Available Metrics */}
        <div className="mt-6 bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
          <div className="px-5 py-4 border-b border-[#E5E7EB]">
            <h3 className="text-[14px] font-semibold text-[#1A1A2E]">Available Metrics</h3>
          </div>
          <div className="p-5">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {metrics.map((m) => (
                <div key={m.id} className="p-3 bg-[#F9FAFB] rounded-lg">
                  <p className="text-[13px] font-medium text-[#1A1A2E]">{m.label || 'Unknown'}</p>
                  {m.unit && (
                    <p className="text-[11px] text-[#9CA3AF]">{m.unit}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ state }: { state?: string }) {
  const config: Record<string, { label: string; bg: string; text: string }> = {
    COMPLETED: { label: "Done", bg: "bg-[#DCFCE7]", text: "text-[#16A34A]" },
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
    <span className={`px-2 py-0.5 text-[10px] font-medium rounded ${bg} ${text}`}>
      {label}
    </span>
  );
}

function StatusRow({ label, value, status }: { label: string; value: string; status: "success" | "warning" | "neutral" }) {
  const dotColors = {
    success: "bg-[#16A34A]",
    warning: "bg-[#D97706]",
    neutral: "bg-[#9CA3AF]",
  };

  return (
    <div className="flex items-center justify-between">
      <span className="text-[13px] text-[#6B7280]">{label}</span>
      <div className="flex items-center gap-2">
        <span className={`w-1.5 h-1.5 rounded-full ${dotColors[status]}`} />
        <span className="text-[13px] text-[#1A1A2E]">{value}</span>
      </div>
    </div>
  );
}
