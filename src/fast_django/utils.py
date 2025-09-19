from __future__ import annotations

from pathlib import Path


def discover_models_modules(start_dir: Path | None = None) -> list[str]:
    base = start_dir or Path.cwd()
    modules: list[str] = []
    for entry in base.iterdir():
        if entry.is_dir() and (entry / "models.py").exists():
            modules.append(f"{entry.name}.models")
    modules.append("aerich.models")
    return modules


