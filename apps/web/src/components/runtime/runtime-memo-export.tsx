"use client";

import { memoDownloadFilename, serializeRuntimeMemo } from "@/lib/runtime/memo-markdown";
import type { RuntimeRun } from "@/services/research-runtime-service";

export function RuntimeMemoExport({ run }: { run: Pick<RuntimeRun, "id" | "state" | "memo"> }) {
  const memo = run.memo;
  if (!memo) return null;
  const content = serializeRuntimeMemo({ id: run.id, state: run.state, memo });
  function download() {
    const url = URL.createObjectURL(new Blob([content], { type: "text/markdown;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = memoDownloadFilename(run.id);
    link.click();
    URL.revokeObjectURL(url);
  }
  return <button type="button" className="outline" onClick={download}>Download Markdown memo</button>;
}
