/**
 * Evaluation Page - AI answer quality
 */

import { useQuery, useMutation } from "@tanstack/react-query";
import { evaluationApi } from "../api/client";

export function EvaluationPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["evaluation"],
    queryFn: evaluationApi.get,
  });

  const runMutation = useMutation({
    mutationFn: () => evaluationApi.run(),
    onSuccess: () => window.location.reload(),
  });

  const latestRun = data?.latest_run;
  const results = latestRun?.results || [];
  const passRate = latestRun && latestRun.passed + latestRun.failed > 0
    ? Math.round((latestRun.passed / (latestRun.passed + latestRun.failed)) * 100)
    : 0;

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-[20px] font-semibold text-[#1A1A2E]">AI Answer Evaluation</h1>
            <p className="text-[14px] text-[#6B7280]">Verify AI analysis accuracy</p>
          </div>
          <button
            onClick={() => runMutation.mutate()}
            disabled={runMutation.isPending}
            className="px-4 py-2 bg-[#00D4AA] text-white text-[14px] font-medium rounded-lg hover:bg-[#00B894] disabled:opacity-50"
          >
            {runMutation.isPending ? "Running..." : "Run Evaluation"}
          </button>
        </div>

        {isLoading ? (
          <LoadingSpinner />
        ) : (
          <>
            {/* Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <StatCard label="Suite Version" value={data?.suite_version || "—"} />
              <StatCard label="Test Cases" value={data?.case_count?.toString() || "0"} />
              <StatCard label="Passed" value={latestRun?.passed?.toString() || "—"} highlight />
              <StatCard label="Failed" value={latestRun?.failed?.toString() || "—"} danger />
            </div>

            {/* Pass Rate */}
            {latestRun && (
              <div className="bg-white rounded-xl border border-[#E5E7EB] p-5 mb-6">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-[14px] font-medium text-[#1A1A2E]">Overall Pass Rate</span>
                  <span className="text-[20px] font-bold text-[#00D4AA]">{passRate}%</span>
                </div>
                <div className="h-2 bg-[#E5E7EB] rounded-full overflow-hidden">
                  <div className="h-full bg-[#00D4AA] rounded-full" style={{ width: `${passRate}%` }} />
                </div>
              </div>
            )}

            {/* Results */}
            <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
              <div className="px-5 py-4 border-b border-[#E5E7EB]">
                <h2 className="text-[14px] font-semibold text-[#1A1A2E]">Test Results</h2>
              </div>
              {results.length === 0 ? (
                <div className="p-8 text-center text-[13px] text-[#9CA3AF]">
                  No test results. Click "Run Evaluation" to generate results.
                </div>
              ) : (
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-[11px] text-[#6B7280] uppercase border-b border-[#E5E7EB] bg-[#F9FAFB]">
                      <th className="px-5 py-3 font-semibold">Case ID</th>
                      <th className="px-4 py-3 font-semibold w-24">Result</th>
                      <th className="px-4 py-3 font-semibold">Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((result, i) => (
                      <tr key={i} className="border-b border-[#F3F4F6] hover:bg-[#F9FAFB]">
                        <td className="px-5 py-4 text-[13px] text-[#1A1A2E]">{result.case_id}</td>
                        <td className="px-4 py-4">
                          <span className={`px-2 py-1 text-[10px] font-medium rounded ${
                            result.passed ? "bg-[#DCFCE7] text-[#16A34A]" : "bg-[#FEE2E2] text-[#DC2626]"
                          }`}>
                            {result.passed ? "PASS" : "FAIL"}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-[12px] text-[#9CA3AF]">{result.details || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, highlight, danger }: { label: string; value: string; highlight?: boolean; danger?: boolean }) {
  return (
    <div className="bg-white rounded-xl border border-[#E5E7EB] p-5">
      <p className="text-[11px] text-[#9CA3AF] uppercase mb-2">{label}</p>
      <p className={`text-[24px] font-bold ${danger ? "text-[#DC2626]" : highlight ? "text-[#00D4AA]" : "text-[#1A1A2E]"}`}>
        {value}
      </p>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div className="h-64 flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-[#00D4AA] border-t-transparent rounded-full animate-spin" />
    </div>
  );
}
