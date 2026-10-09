"use client";

import { useEffect, useState } from "react";
import { defaultRuntimeActor, isRuntimeActorRole, loadRuntimeActor, saveRuntimeActor, type RuntimeActor, type RuntimeActorRole } from "@/services/runtime-actor";

const roles: Array<[RuntimeActorRole, string]> = [
  ["analyst", "Analyst"],
  ["reviewer", "Reviewer"],
  ["chair", "Chair"],
  ["admin", "Admin"],
];

export function RuntimeActorSelector() {
  const [identity, setIdentity] = useState<RuntimeActor>(() => loadRuntimeActor("reviewer"));

  useEffect(() => {
    function onActorChange(event: Event) {
      const detail = event instanceof CustomEvent ? event.detail as RuntimeActor : null;
      if (detail?.actor && isRuntimeActorRole(detail.role)) setIdentity(detail);
    }
    window.addEventListener("deepresearch-runtime-actor-change", onActorChange);
    return () => window.removeEventListener("deepresearch-runtime-actor-change", onActorChange);
  }, []);

  function update(next: RuntimeActor) {
    setIdentity(next);
    saveRuntimeActor(next);
  }

  return (
    <section className="decision-panel runtime-actor-selector" aria-label="Runtime actor identity">
      <header>
        <div>
          <small>CURRENT ACTOR · REQUEST IDENTITY</small>
          <h2>Runtime write identity</h2>
        </div>
        <span>{identity.role}</span>
      </header>
      <div className="red-team-grid">
        <label htmlFor="runtime-current-actor">
          Actor
          <input
            id="runtime-current-actor"
            className="text-control"
            value={identity.actor}
            onChange={(event) => update({ ...identity, actor: event.target.value })}
            placeholder="reviewer@example.com"
          />
        </label>
        <label htmlFor="runtime-current-role">
          Role
          <select
            id="runtime-current-role"
            className="text-control"
            value={identity.role}
            onChange={(event) => {
              const role = event.target.value;
              if (!isRuntimeActorRole(role)) return;
              const fallback = defaultRuntimeActor(role);
              update({ actor: identity.actor.includes("@") ? identity.actor : fallback.actor, role });
            }}
          >
            {roles.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </label>
      </div>
      <p className="form-note">Review and decision forms use this identity by default. The backend still validates role permissions and actor/body consistency.</p>
    </section>
  );
}
