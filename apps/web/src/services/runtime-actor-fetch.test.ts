import { describe, expect, it } from "vitest";

import type { FetchLike } from "./research-runtime-service";
import { createActorAwareRuntimeFetch } from "./runtime-actor-fetch";

function captureFetch() {
  const calls: Array<{ input: Parameters<FetchLike>[0]; init?: RequestInit }> = [];
  const fetchImpl: FetchLike = async (input, init) => {
    calls.push({ input, init });
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  };
  return { calls, fetchImpl };
}

describe("createActorAwareRuntimeFetch", () => {
  it("adds reviewer actor headers for red-team review writes", async () => {
    const { calls, fetchImpl } = captureFetch();
    const runtimeFetch = createActorAwareRuntimeFetch(fetchImpl);

    await runtimeFetch("http://runtime.test/api/v1/research-runs/run-1/red-team-reviews", {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify({ reviewer: "reviewer@example.com", challenge: "risk" }),
    });

    const headers = new Headers(calls[0]?.init?.headers);
    expect(headers.get("X-Actor")).toBe("reviewer@example.com");
    expect(headers.get("X-Actor-Role")).toBe("reviewer");
  });

  it("adds chair actor headers for decision writes", async () => {
    const { calls, fetchImpl } = captureFetch();
    const runtimeFetch = createActorAwareRuntimeFetch(fetchImpl);

    await runtimeFetch("http://runtime.test/api/v1/research-runs/run-1/decisions", {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify({ actor: "chair@example.com", action: "APPROVE_THESIS" }),
    });

    const headers = new Headers(calls[0]?.init?.headers);
    expect(headers.get("X-Actor")).toBe("chair@example.com");
    expect(headers.get("X-Actor-Role")).toBe("chair");
  });

  it("does not add actor headers to unrelated writes", async () => {
    const { calls, fetchImpl } = captureFetch();
    const runtimeFetch = createActorAwareRuntimeFetch(fetchImpl);

    await runtimeFetch("http://runtime.test/api/v1/research-cases", {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify({ question: "Assess ACME", target: "ACME" }),
    });

    const headers = new Headers(calls[0]?.init?.headers);
    expect(headers.has("X-Actor")).toBe(false);
    expect(headers.has("X-Actor-Role")).toBe(false);
  });
});
