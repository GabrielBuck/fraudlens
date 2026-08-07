from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "backend" / "fraudlens.db",
    ROOT / "backend" / ".coverage",
    ROOT / "backend" / "htmlcov",
    ROOT / "frontend" / ".next",
    ROOT / "frontend" / "coverage",
    ROOT / "frontend" / "playwright-report",
]

for target in TARGETS:
    if target.is_dir():
        shutil.rmtree(target)
    elif target.exists():
        target.unlink()
print("Artefatos locais removidos.")

