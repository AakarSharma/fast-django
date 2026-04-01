from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_end_to_end_project_flow(tmp_path: Path) -> None:
    cwd = tmp_path
    env = os.environ.copy()
    cli_bin = str(Path(sys.executable).with_name("fast-django"))

    res = subprocess.run([cli_bin, "startproject", "mysite"], cwd=cwd, check=False)
    assert res.returncode == 0
    project_dir = cwd / "mysite"
    assert (project_dir / "manage.py").exists()
    assert (project_dir / "orm_config.py").exists()

    res = subprocess.run([cli_bin, "startapp", "blog"], cwd=project_dir, check=False)
    assert res.returncode == 0
    assert (project_dir / "blog" / "models.py").exists()
    assert (project_dir / "blog" / "migrations" / "__init__.py").exists()

    res = subprocess.run([cli_bin, "makemigrations", "--app", "blog"], cwd=project_dir, check=False)
    assert res.returncode == 0

    res = subprocess.run([cli_bin, "migrate", "--app", "blog"], cwd=project_dir, check=False)
    assert res.returncode == 0

    env["FD_TEST_MODE"] = "1"
    res = subprocess.run([cli_bin, "runserver"], cwd=project_dir, env=env, check=False)
    assert res.returncode == 0
