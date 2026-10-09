export type RuntimeActorRole = "analyst" | "reviewer" | "chair" | "admin";

export type RuntimeActor = {
  actor: string;
  role: RuntimeActorRole;
};

export const RUNTIME_ACTOR_STORAGE_KEY = "deepresearch.runtime.actor";

const fallbackActors: Record<RuntimeActorRole, RuntimeActor> = {
  analyst: { actor: "analyst@example.com", role: "analyst" },
  reviewer: { actor: "reviewer@example.com", role: "reviewer" },
  chair: { actor: "chair@example.com", role: "chair" },
  admin: { actor: "admin@example.com", role: "admin" },
};

function parseActor(value: string | null): RuntimeActor | null {
  if (!value) return null;
  try {
    const parsed: unknown = JSON.parse(value);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return null;
    const actor = "actor" in parsed && typeof parsed.actor === "string" ? parsed.actor.trim() : "";
    const role = "role" in parsed && typeof parsed.role === "string" ? parsed.role.trim() : "";
    if (!actor || !isRuntimeActorRole(role)) return null;
    return { actor, role };
  } catch {
    return null;
  }
}

export function isRuntimeActorRole(value: string): value is RuntimeActorRole {
  return value === "analyst" || value === "reviewer" || value === "chair" || value === "admin";
}

export function defaultRuntimeActor(role: RuntimeActorRole = "reviewer"): RuntimeActor {
  return fallbackActors[role];
}

export function loadRuntimeActor(role: RuntimeActorRole = "reviewer"): RuntimeActor {
  if (typeof window === "undefined") return defaultRuntimeActor(role);
  return parseActor(window.localStorage.getItem(RUNTIME_ACTOR_STORAGE_KEY)) ?? defaultRuntimeActor(role);
}

export function saveRuntimeActor(actor: RuntimeActor): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(RUNTIME_ACTOR_STORAGE_KEY, JSON.stringify(actor));
  window.dispatchEvent(new CustomEvent<RuntimeActor>("deepresearch-runtime-actor-change", { detail: actor }));
}
