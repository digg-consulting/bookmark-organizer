"""Regression test for install script."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

__all__ = ["test_install_script_installs_cli"]


def test_install_script_installs_cli(tmp_path: Path) -> None:
    """Run install.sh in isolation and verify the installed CLI works."""
    project_root = Path(__file__).resolve().parent.parent
    install_script = project_root / "install.sh"

    # Copy project to a temp workspace to avoid modifying the real repo
    workspace = tmp_path / "workspace"
    shutil.copytree(project_root, workspace)
    # Ensure shell script is executable
    os.chmod(install_script, 0o755)

    # Use an isolated HOME so install artifacts don't pollute the real environment
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    fake_bin = fake_home / ".local" / "bin"
    fake_bin.mkdir(parents=True)

    env = os.environ.copy()
    env["HOME"] = str(fake_home)
    env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")
    env["FORCE_INSTALL"] = "1"
    env["XDG_CONFIG_HOME"] = str(fake_home / ".config")
    env["XDG_CACHE_HOME"] = str(fake_home / ".cache")
    env["XDG_DATA_HOME"] = str(fake_home / ".local" / "share")

    # Run the install script from the copied workspace
    result = subprocess.run(
        ["bash", str(install_script)],
        cwd=workspace,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"install.sh failed:\n{result.stdout}\n{result.stderr}"

    cli_bin = fake_bin / "bookmark-organizer"
    assert cli_bin.exists(), f"CLI binary not found at {cli_bin}"
    assert os.access(cli_bin, os.X_OK), f"CLI binary is not executable: {cli_bin}"

    help_result = subprocess.run(
        [str(cli_bin), "--help"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_result.returncode == 0, f"CLI --help failed:\n{help_result.stdout}\n{help_result.stderr}"
    assert "Usage:" in help_result.stdout or "Usage:" in help_result.stderr
