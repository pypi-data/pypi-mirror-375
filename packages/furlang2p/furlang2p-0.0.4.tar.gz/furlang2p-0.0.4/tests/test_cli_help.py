"""Ensure that the CLI entry point prints help."""

from __future__ import annotations

import shutil
import subprocess


def test_cli_help_runs() -> None:
    exe = shutil.which("furlang2p")
    assert exe is not None
    proc = subprocess.run([exe, "--help"], capture_output=True, text=True)
    assert proc.returncode == 0
    assert "FurlanG2P" in proc.stdout or "Usage" in proc.stdout
