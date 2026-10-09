import type { FetchLike } from "./research-runtime-service";

type ActorHeaders = {
  actor: string;
  role: "reviewer" | "chair";
};

function pathFromInput(input: Parameters<FetchLike>[0]): string {
  if (typeof input === "string") {
    return pathname(input);
  }
  if (input instanceof URL) {
    return input.pathname;
  }
  return pathname(input.url);
}

function pathname(value: string): string {
  try {
    return new URL(value).pathname;
  } catch {
    return value;
  }
}

function parseJsonBody(body: BodyInit | null | undefined): Record<string, unknown> | null {
  if (typeof body !== "string") {
    return null;
  }
  try {
    const parsed: unknown = JSON.parse(body);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed as Record<string, unknown> : null;
  } catch {
    return null;
  }
}

function actorHeadersFor(path: string, body: BodyInit | null | undefined): ActorHeaders | null {
  const parsed = parseJsonBody(body);
  if (!parsed) {
    return null;
  }
  if (path.endsWith("/red-team-reviews") || path.endsWith("/ic-reviews")) {
    const reviewer = typeof parsed.reviewer === "string" ? parsed.reviewer.trim() : "";
    return reviewer ? { actor: reviewer, role: "reviewer" } : null;
  }
  if (path.endsWith("/decisions")) {
    const actor = typeof parsed.actor === "string" ? parsed.actor.trim() : "";
    return actor ? { actor, role: "chair" } : null;
  }
  return null;
}

function withActorHeaders(headers: HeadersInit | undefined, actorHeaders: ActorHeaders): Headers {
  const next = new Headers(headers);
  next.set("X-Actor", actorHeaders.actor);
  next.set("X-Actor-Role", actorHeaders.role);
  return next;
}

export function createActorAwareRuntimeFetch(fetchImpl: FetchLike = fetch.bind(globalThis)): FetchLike {
  return async (input, init) => {
    const method = (init?.method ?? (input instanceof Request ? input.method : "GET")).toUpperCase();
    if (method !== "POST") {
      return fetchImpl(input, init);
    }

    const actorHeaders = actorHeadersFor(pathFromInput(input), init?.body ?? null);
    if (!actorHeaders) {
      return fetchImpl(input, init);
    }

    return fetchImpl(input, {
      ...init,
      headers: withActorHeaders(init?.headers, actorHeaders),
    });
  };
}
