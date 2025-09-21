from __future__ import annotations

import os
import subprocess
from pathlib import Path


def test_end_to_end_project_flow(tmp_path: Path) -> None:
    cwd = tmp_path
    env = os.environ.copy()
    # 1) startproject
    res = subprocess.run(["fast-django", "startproject", "mysite"], cwd=cwd, check=False)
    assert res.returncode == 0
    project_dir = cwd / "mysite"
    assert (project_dir / "manage.py").exists()
    assert (project_dir / "orm_config.py").exists()

    # 2) startapp blog
    res = subprocess.run(["python", "manage.py", "startapp", "blog"], cwd=project_dir, check=False)
    assert res.returncode == 0
    assert (project_dir / "blog" / "models.py").exists()
    assert (project_dir / "blog" / "migrations" / "__init__.py").exists()

    # 3) makemigrations (scoped to app)
    res = subprocess.run(
        ["python", "manage.py", "makemigrations", "--app", "blog"], cwd=project_dir, check=False
    )
    assert res.returncode == 0

    # 4) migrate
    res = subprocess.run(["python", "manage.py", "migrate"], cwd=project_dir, check=False)
    assert res.returncode == 0

    # 5) runserver (test mode so it doesn't block)
    env["FD_TEST_MODE"] = "1"
    res = subprocess.run(
        ["python", "manage.py", "runserver"], cwd=project_dir, env=env, check=False
    )
    assert res.returncode == 0
