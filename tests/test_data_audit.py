import csv
from pathlib import Path

from src.case_bundle.data_audit import run_audit


def test_audit_writes_complete_contract_for_small_fixture(tmp_path: Path):
    raw = tmp_path / "data/raw"
    raw.mkdir(parents=True)
    header = [
        "Name", "Description", "URL", "Created At", "Updated At", "Homepage",
        "Size", "Forks", "Issues", "Language", "License", "Topics",
        "Has Issues", "Has Projects", "Has Downloads", "Has Wiki", "Has Pages",
        "Has Discussions", "Is Fork", "Is Archived", "Is Template", "Default Branch",
    ]
    row = [
        "repo", "description", "https://github.com/org/repo", "2020-01-01T00:00:00Z",
        "2023-01-01T00:00:00Z", "", "1", "0", "0", "Python", "MIT", "[]",
        "True", "True", "True", "True", "False", "False", "False", "False",
        "False", "main",
    ]
    with (raw / "github-repo-data.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header[:7] + ["Stars"] + header[7:])
        writer.writerow(row[:7] + ["1"] + row[7:])
    with (raw / "github-repo-prediction-set.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        prediction = row.copy()
        prediction[0] = "other"
        prediction[2] = "https://github.com/org/other"
        writer.writerow(prediction)
    with (raw / "submission-file.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Name"])
        writer.writerow(["other"])

    run_audit(tmp_path)

    generated = tmp_path / "artifacts/generated"
    expected = {
        "data/file_inventory.csv", "data/schema_audit.csv", "data/data_quality_table.csv",
        "data/target_profile.csv", "data/duplicate_audit.csv", "data/temporal_coverage.csv",
        "data/feature_timing_register.csv", "data/limitations_register.csv",
        "memos/T01_closure_memo.md",
    }
    assert all((generated / item).exists() for item in expected)
    with (generated / "data/feature_timing_register.csv").open(newline="") as handle:
        timing = list(csv.DictReader(handle))
    assert len(timing) == 23
    assert all(row["timing_class"] for row in timing)
    assert "PASS" in (generated / "memos/T01_closure_memo.md").read_text()
