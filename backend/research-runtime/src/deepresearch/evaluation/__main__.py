import json
import tempfile
from pathlib import Path

from deepresearch.domain.models import ResearchCase
from deepresearch.evaluation.scorer import score_plan, score_run
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import DeterministicEvidenceProvider
from deepresearch.runtime.planner import DeterministicResearchPlanner


def main() -> None:
    case_path = Path(__file__).parents[3] / "evaluation" / "cases" / "basic.json"
    planner_case_path = Path(__file__).parents[3] / "evaluation" / "cases" / "planner.json"
    case = json.loads(case_path.read_text(encoding="utf-8"))
    planner_case = json.loads(planner_case_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="deepresearch-eval-") as directory:
        store = SQLiteStore(Path(directory) / "evaluation.sqlite3")
        planner = DeterministicResearchPlanner()
        research_case = ResearchCase(id=case["case_id"], question=case["title"], target="Synthetic AI infrastructure")
        plan_result = score_plan(planner.plan(research_case.model_copy(update={"id": planner_case["case_id"]})), planner_case)
        engine = ResearchEngine(store, DeterministicEvidenceProvider(), planner=planner)
        run = engine.create_run(research_case)
        run_result = score_run(engine.execute(run.id), case)
        print(json.dumps({"plan_evaluation": plan_result.model_dump(mode="json"), "run_evaluation": run_result.model_dump(mode="json")}, indent=2))


if __name__ == "__main__":
    main()
