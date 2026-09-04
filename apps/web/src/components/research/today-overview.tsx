import { CheckCircle2, Clock3, FileText, Target } from "lucide-react";
import type { TodayOverview as TodayOverviewModel } from "@/domain/research";

const icons = { research: FileText, progress: Clock3, review: Target, completed: CheckCircle2 };

export function TodayOverview({ overview }: { overview: TodayOverviewModel }) {
  return <><div className="context-heading"><b>Today overview</b><span>{overview.updatedAtLabel}</span></div><div className="quick-stats">{overview.stats.map((stat) => { const Icon = icons[stat.kind]; return <Stat key={stat.label} label={stat.label} value={String(stat.value)} icon={<Icon />} />; })}</div><Bars title="Research coverage" items={overview.coverage} /><Bars title="Trigger distribution" items={overview.triggers} /><section className="today-changes"><b>What changed</b>{overview.changes.map((change) => <article key={change.id}><span className={`materiality ${change.materiality}`}>{change.materiality}</span><div><b>{change.label}</b><p>{change.summary}</p></div></article>)}</section><section className="today-recent"><b>Recent research</b>{overview.recent.map((item) => <a href={item.status === "in-research" ? "/research/case-value-pools" : item.status === "awaiting-review" ? "/review" : "/brief"} key={item.id}><span>{item.title}</span><small>{item.updatedAtLabel}</small></a>)}</section></>;
}
function Stat({ label, value, icon }: { label: string; value: string; icon: React.ReactNode }) { return <div className="stat"><span>{label}</span><b>{value}</b><i>{icon}</i></div>; }
function Bars({ title, items }: { title: string; items: { label: string; value: number }[] }) { return <section className="bars"><b>{title}</b>{items.map(({ label, value }) => <div key={label}><span>{label}</span><i><em style={{ width: `${value}%` }} /></i><small>{value}%</small></div>)}</section>; }
