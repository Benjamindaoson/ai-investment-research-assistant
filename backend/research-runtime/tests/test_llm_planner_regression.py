import json

from deepresearch.evaluation.llm_planner_regression import (
    _write_report,
    live_configuration,
    missing_live_configuration,
)


def test_live_configuration_requires_explicit_llm_and_finevidence(monkeypatch) -> None:
    monkeypatch.delenv("DEEPRESEARCH_PLANNER", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("DEEPSEEK_MODEL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("FIN_EVIDENCE_BASE_URL", raising=False)

    missing = missing_live_configuration(live_configuration())

    assert "DEEPRESEARCH_PLANNER=llm" in missing
    assert "LLM API key" in missing
    assert "FIN_EVIDENCE_BASE_URL" in missing


def test_report_writer_persists_json_without_secret_field(tmp_path) -> None:
    secret = "do-not-persist-this"
    path = _write_report(tmp_path / "report.json", {"status": "BLOCKED", "configuration": {"api_key_present": True}})

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["status"] == "BLOCKED"
    assert secret not in path.read_text(encoding="utf-8")
