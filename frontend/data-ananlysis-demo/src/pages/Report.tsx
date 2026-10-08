/**
 * Report Page - Export analysis
 */

import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { analysisApi } from "../api/client";

export function ReportPage() {
  const { taskId } = useParams<{ taskId: string }>();

  const { data: task, isLoading } = useQuery({
    queryKey: ["task", taskId],
    queryFn: () => analysisApi.get(taskId!),
    enabled: !!taskId,
  });

  if (isLoading) {
    return <LoadingSpinner />;
  }

  const claims = task?.claims || [];

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-[18px] font-semibold text-[#1A1A2E]">Report</h2>
          <div className="flex gap-2">
            <button className="px-3 py-1.5 text-[12px] border border-[#E5E7EB] rounded-lg hover:bg-[#F5F5F5]">
              Markdown
            </button>
            <button className="px-3 py-1.5 text-[12px] border border-[#E5E7EB] rounded-lg hover:bg-[#F5F5F5]">
              HTML
            </button>
            <button className="px-3 py-1.5 text-[12px] border border-[#E5E7EB] rounded-lg hover:bg-[#F5F5F5]">
              Download
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-xl border border-[#E5E7EB] p-6">
          <h1 className="text-[20px] font-semibold text-[#1A1A2E] mb-2">{task?.question}</h1>
          <p className="text-[12px] text-[#9CA3AF] mb-6">
            Generated {new Date().toLocaleDateString()}
          </p>

          {/* Summary */}
          <div className="mb-6">
            <h2 className="text-[14px] font-semibold text-[#1A1A2E] mb-3">Executive Summary</h2>
            <p className="text-[14px] text-[#6B7280] leading-relaxed">
              {task?.summary || "Analysis completed. See key findings below."}
            </p>
          </div>

          {/* Findings */}
          <div>
            <h2 className="text-[14px] font-semibold text-[#1A1A2E] mb-3">Key Findings</h2>
            {claims.length === 0 ? (
              <p className="text-[14px] text-[#9CA3AF]">No findings available</p>
            ) : (
              <div className="space-y-3">
                {claims.map((claim) => (
                  <div key={claim.id} className="p-4 bg-[#F9FAFB] rounded-lg">
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
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function ClaimTypeBadge({ type }: { type: string }) {
  const config: Record<string, { label: string; bg: string; text: string }> = {
    FACT: { label: "FACT", bg: "bg-[#DCFCE7]", text: "text-[#16A34A]" },
    INFERENCE: { label: "INFERENCE", bg: "bg-[#DBEAFE]", text: "text-[#2563EB]" },
    QUALIFIED: { label: "QUALIFIED", bg: "bg-[#FEF3C7]", text: "text-[#D97706]" },
  };

  const { label, bg, text } = config[type] || {
    label: type,
    bg: "bg-[#F3F4F6]",
    text: "text-[#6B7280]",
  };

  return (
    <span className={`px-2 py-1 text-[10px] font-bold rounded ${bg} ${text}`}>
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
