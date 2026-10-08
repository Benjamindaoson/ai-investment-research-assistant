/**
 * Evidence Page - Evidence library
 */

import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { analysisApi } from "../api/client";

export function EvidencePage() {
  const { taskId } = useParams<{ taskId: string }>();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState("ALL");

  const { data, isLoading } = useQuery({
    queryKey: ["evidence", taskId],
    queryFn: () => analysisApi.evidence(taskId!),
    enabled: !!taskId,
  });

  const evidence = data?.items || [];
  const filtered = evidence.filter((e) => typeFilter === "ALL" || e.type === typeFilter);
  const selected = evidence.find((e) => e.evidence_id === selectedId);

  return (
    <div className="h-full flex">
      {/* List */}
      <div className="w-1/2 border-r border-[#E5E7EB] overflow-y-auto bg-white">
        <div className="p-4 border-b border-[#E5E7EB] sticky top-0 bg-white">
          <h2 className="text-[14px] font-semibold text-[#1A1A2E] mb-3">Evidence Library</h2>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-3 py-2 text-[13px] border border-[#E5E7EB] rounded-lg outline-none focus:border-[#00D4AA]"
          >
            <option value="ALL">All types</option>
            <option value="observation">Observation</option>
            <option value="query">Query</option>
            <option value="computation">Computation</option>
            <option value="external">External</option>
          </select>
        </div>

        {isLoading ? (
          <div className="p-4"><div className="h-16 bg-[#F5F5F5] rounded animate-pulse" /></div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center text-[13px] text-[#9CA3AF]">No evidence available</div>
        ) : (
          <div className="divide-y divide-[#F3F4F6]">
            {filtered.map((item) => (
              <button
                key={item.evidence_id}
                onClick={() => setSelectedId(item.evidence_id)}
                className={`w-full text-left p-4 transition-colors ${
                  selectedId === item.evidence_id ? "bg-[#00D4AA]/5" : "hover:bg-[#F9FAFB]"
                }`}
              >
                <div className="flex items-start gap-3">
                  <TypeBadge type={item.type} />
                  <div className="flex-1 min-w-0">
                    <p className="text-[13px] text-[#1A1A2E] truncate">{item.description}</p>
                    <p className="text-[11px] text-[#9CA3AF] mt-1">{item.source}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Detail */}
      <div className="w-1/2 overflow-y-auto bg-[#F5F5F5]">
        {selected ? (
          <div className="p-6">
            <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
              <div className="px-5 py-4 border-b border-[#E5E7EB]">
                <TypeBadge type={selected.type} />
              </div>
              <div className="p-5 space-y-4">
                <div>
                  <p className="text-[11px] text-[#9CA3AF] uppercase mb-1">Description</p>
                  <p className="text-[14px] text-[#1A1A2E]">{selected.description}</p>
                </div>
                <div>
                  <p className="text-[11px] text-[#9CA3AF] uppercase mb-1">Source</p>
                  <p className="text-[13px] text-[#6B7280]">{selected.source}</p>
                </div>

                {selected.validation && (
                  <div>
                    <p className="text-[11px] text-[#9CA3AF] uppercase mb-2">Validation</p>
                    <div className="grid grid-cols-2 gap-2">
                      {[
                        { key: "metric", label: "Metric" },
                        { key: "time", label: "Time" },
                        { key: "join", label: "Join" },
                        { key: "reconciliation", label: "Reconciliation" },
                        { key: "freshness", label: "Freshness" },
                      ].map(({ key, label }) => (
                        <div key={key} className="flex items-center gap-2 p-2 bg-[#F9FAFB] rounded">
                          {selected.validation[key as keyof typeof selected.validation] ? (
                            <svg className="w-4 h-4 text-[#16A34A]" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                            </svg>
                          ) : (
                            <svg className="w-4 h-4 text-[#DC2626]" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"/>
                            </svg>
                          )}
                          <span className="text-[12px] text-[#6B7280]">{label}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="h-full flex items-center justify-center">
            <p className="text-[13px] text-[#9CA3AF]">Select evidence to view details</p>
          </div>
        )}
      </div>
    </div>
  );
}

function TypeBadge({ type }: { type: string }) {
  const config: Record<string, { label: string; bg: string; text: string }> = {
    observation: { label: "Observation", bg: "bg-[#DCFCE7]", text: "text-[#16A34A]" },
    query: { label: "Query", bg: "bg-[#DBEAFE]", text: "text-[#2563EB]" },
    computation: { label: "Computation", bg: "bg-[#FEF3C7]", text: "text-[#D97706]" },
    external: { label: "External", bg: "bg-[#EDE9FE]", text: "text-[#7C3AED]" },
  };

  const { label, bg, text } = config[type] || {
    label: type,
    bg: "bg-[#F3F4F6]",
    text: "text-[#6B7280]",
  };

  return (
    <span className={`px-2 py-1 text-[10px] font-medium rounded ${bg} ${text}`}>
      {label}
    </span>
  );
}
