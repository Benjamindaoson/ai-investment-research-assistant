import type { RuntimeHealth } from "@/services/research-runtime-service";

const modeLabels: Record<RuntimeHealth["evidence_mode"], string> = {
  LIVE_EXTERNAL: "Live external evidence",
  DETERMINISTIC_FIXTURE: "Deterministic fixture",
  CUSTOM: "Custom provider",
};

export function RuntimeProviderReadiness({ health, isPending, error }: { health: RuntimeHealth | undefined; isPending: boolean; error: Error | null }) {
  return <section className="decision-panel runtime-provider-readiness" aria-labelledby="runtime-provider-readiness-heading">
    <header><div><small>RUNTIME BOUNDARY · READ-ONLY</small><h2 id="runtime-provider-readiness-heading">Provider readiness</h2></div><span>{health ? modeLabels[health.evidence_mode] : "Unknown"}</span></header>
    {isPending && <p className="form-note">Checking configured runtime providers…</p>}
    {error && <p className="form-error" role="alert">Runtime readiness unavailable: {error.message}</p>}
    {!isPending && !error && health && <><div className="company-section-grid"><article className="company-section"><header><h3>Evidence</h3></header><p>{health.evidence_provider}</p></article><article className="company-section"><header><h3>Planning</h3></header><p>{health.planner}</p></article><article className="company-section"><header><h3>Synthesis</h3></header><p>{health.synthesizer}</p></article><article className="company-section"><header><h3>Registered tools</h3></header><p>{health.tools.join(" · ") || "None registered"}</p></article></div><small>Health confirms process configuration only; it is not evidence quality, model quality, or investment advice.</small></>}
  </section>;
}
