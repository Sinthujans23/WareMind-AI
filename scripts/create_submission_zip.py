"""Create a reproducible WareMind submission archive."""

import shutil
import zipfile
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT / "WareMind-AI-Submission.zip"

INCLUDE_DIRS = ("waremind", "tests", "scripts", "results", "docs")
INCLUDE_FILES = (
    "main.py",
    "requirements.txt",
    "README.md",
    ".gitignore",
)


def should_include(relative):
    parts = relative.parts
    if any(part in {".git", ".venv", "__pycache__", ".pytest_cache"} for part in parts):
        return False
    if relative.suffix in {".pyc", ".bak"}:
        return False
    if relative.name == OUTPUT.name:
        return False
    return True


def main():
    if OUTPUT.exists():
        OUTPUT.unlink()

    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in INCLUDE_FILES:
            path = PROJECT / name
            if path.is_file():
                archive.write(path, name)

        for name in INCLUDE_DIRS:
            directory = PROJECT / name
            if not directory.exists():
                continue
            for path in directory.rglob("*"):
                if not path.is_file():
                    continue
                relative = path.relative_to(PROJECT)
                if should_include(relative):
                    archive.write(path, relative.as_posix())

    print(f"Submission archive created: {OUTPUT}")


if __name__ == "__main__":
    main()
