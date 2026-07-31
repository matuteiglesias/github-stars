from pathlib import Path

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "CODEX_PROMPT.md",
    "docs/problem_statement.md",
    "docs/methodological_guardrails.md",
    "docs/business_decision.md",
    "docs/feature_timing.md",
    "plans/execution_plan.md",
    "plans/artifact_contract.md",
    "plans/stage_gates.md",
    "tasks/T00_problem_definition.md",
    "tasks/T01_data_audit.md",
    "tasks/T02_hypothesis_eda.md",
    "tasks/T03_modeling.md",
    "tasks/T04_business_policy.md",
    "tasks/T05_handoff.md",
    "memos/T00_closure_memo.md",
    "memos/decision_log.md",
    "artifacts/artifact_registry.csv",
]

def test_required_bundle_files_exist():
    root = Path(__file__).resolve().parents[1]
    missing = [path for path in REQUIRED_FILES if not (root / path).exists()]
    assert not missing, f"Missing required bundle files: {missing}"

def test_problem_definition_precedes_analysis_tasks():
    root = Path(__file__).resolve().parents[1]
    t00 = (root / "tasks/T00_problem_definition.md").read_text(encoding="utf-8")
    assert "Prediction timing" in t00
    assert "Leakage risks" in t00
    assert "Gate 00 passes" in t00
