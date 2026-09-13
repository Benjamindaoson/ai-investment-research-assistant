import json
import tempfile
from pathlib import Path

from deepresearch.domain.models import ResearchCase
from deepresearch.evaluation.scorer import score_run
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import DeterministicEvidenceProvider


def main() -> None:
    case_path = Path(__file__).parents[3] / "evaluation" / "cases" / "basic.json"
    case = json.loads(case_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="deepresearch-eval-") as directory:
        store = SQLiteStore(Path(directory) / "evaluation.sqlite3")
        engine = ResearchEngine(store, DeterministicEvidenceProvider())
        research_case = ResearchCase(id=case["case_id"], question=case["title"], target="Synthetic AI infrastructure")
        run = engine.create_run(research_case)
        result = score_run(engine.execute(run.id), case)
        print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
