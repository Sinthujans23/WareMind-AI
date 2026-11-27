"""Verify the WareMind submission archive."""

import shutil
import tempfile
import zipfile
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ARCHIVE = PROJECT / "WareMind-AI-Submission.zip"

REQUIRED = (
    "main.py",
    "requirements.txt",
    "README.md",
    "waremind/core.py",
    "waremind/mesa_model.py",
    "waremind/navigation.py",
    "tests/test_deadlock.py",
    "results/advanced_comparison_baseline.csv",
    "results/advanced_comparison_optimized.csv",
    "docs/FINAL_REPORT.md",
)


def main():
    failures = []
    if not ARCHIVE.is_file():
        failures.append("Submission archive is missing")
    else:
        with zipfile.ZipFile(ARCHIVE, "r") as archive:
            names = set(archive.namelist())
            bad = archive.testzip()
            if bad:
                failures.append(f"Corrupt ZIP member: {bad}")
            for required in REQUIRED:
                if required not in names:
                    failures.append(f"Missing required file: {required}")
            prohibited = [
                name for name in names
                if "/.git/" in f"/{name}/"
                or "/.venv/" in f"/{name}/"
                or "__pycache__" in name
            ]
            failures.extend(f"Prohibited path: {name}" for name in prohibited)

            with tempfile.TemporaryDirectory() as temp:
                archive.extractall(temp)
                extracted = Path(temp)
                for required in REQUIRED:
                    if not (extracted / required).is_file():
                        failures.append(f"Extracted file missing: {required}")

    if failures:
        print("Submission verification FAILED")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("Submission verification passed")
    print(f"Archive: {ARCHIVE}")


if __name__ == "__main__":
    main()
