/**
 * Settings Page - Configuration
 */

import { useQuery } from "@tanstack/react-query";
import { settingsApi, semanticApi } from "../api/client";

export function SettingsPage() {
  const { data: settings, isLoading: settingsLoading } = useQuery({
    queryKey: ["settings"],
    queryFn: settingsApi.get,
  });

  const { data: semantic, isLoading: semanticLoading } = useQuery({
    queryKey: ["semantic"],
    queryFn: semanticApi.get,
  });

  const isLoading = settingsLoading || semanticLoading;

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-6">
          <h1 className="text-[20px] font-semibold text-[#1A1A2E]">Settings</h1>
          <p className="text-[14px] text-[#6B7280]">System configuration and runtime status</p>
        </div>

        {/* Model Provider */}
        <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden mb-6">
          <div className="px-5 py-4 border-b border-[#E5E7EB]">
            <h2 className="text-[14px] font-semibold text-[#1A1A2E]">Model Provider</h2>
          </div>
          <div className="p-5 grid grid-cols-2 gap-6">
            <SettingRow label="Active Provider" value={settings?.provider || "—"} />
            <SettingRow
              label="Credentials"
              value={settings?.credential_configured ? "Configured" : "Not configured"}
              valueColor={settings?.credential_configured ? "#16A34A" : "#D97706"}
            />
          </div>
        </div>

        {/* Data & Semantics */}
        <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden mb-6">
          <div className="px-5 py-4 border-b border-[#E5E7EB]">
            <h2 className="text-[14px] font-semibold text-[#1A1A2E]">Data & Semantics</h2>
          </div>
          <div className="p-5 grid grid-cols-2 gap-6">
            <SettingRow label="Dataset Version" value={settings?.dataset_version || "—"} />
            <SettingRow label="Semantic Version" value={settings?.semantic_version || "—"} />
          </div>
        </div>

        {/* Analysis Budget */}
        <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden mb-6">
          <div className="px-5 py-4 border-b border-[#E5E7EB]">
            <h2 className="text-[14px] font-semibold text-[#1A1A2E]">Analysis Budget</h2>
          </div>
          <div className="p-5 grid grid-cols-2 gap-6">
            <SettingRow label="Max Queries" value={settings?.analysis_budget?.max_queries?.toString() || "—"} />
            <SettingRow label="Max Tool Calls" value={settings?.analysis_budget?.max_tool_calls?.toString() || "—"} />
            <SettingRow label="Max Depth" value={settings?.analysis_budget?.max_investigation_depth?.toString() || "—"} />
            <SettingRow label="Max Result Rows" value={settings?.analysis_budget?.max_result_rows?.toString() || "—"} />
          </div>
        </div>

        {/* Semantic Package */}
        <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
          <div className="px-5 py-4 border-b border-[#E5E7EB]">
            <h2 className="text-[14px] font-semibold text-[#1A1A2E]">Semantic Package</h2>
          </div>
          <div className="p-5">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${semantic?.status === "loaded" ? "bg-[#16A34A]" : "bg-[#D97706]"}`} />
              <span className="text-[14px] text-[#1A1A2E]">
                {semantic?.status === "loaded" ? "Loaded" : "Not loaded"}
              </span>
              {semantic?.version && (
                <span className="text-[12px] text-[#9CA3AF]">v{semantic.version}</span>
              )}
            </div>
            {semantic?.metrics && (
              <p className="text-[12px] text-[#9CA3AF] mt-2">{semantic.metrics.length} metrics defined</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SettingRow({ label, value, valueColor }: { label: string; value: string; valueColor?: string }) {
  return (
    <div>
      <p className="text-[11px] text-[#9CA3AF] uppercase mb-1">{label}</p>
      <p className="text-[14px] text-[#1A1A2E]" style={valueColor ? { color: valueColor } : undefined}>{value}</p>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-[#00D4AA] border-t-transparent rounded-full animate-spin" />
    </div>
  );
}
