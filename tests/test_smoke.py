"""Smoke tests for the Hermes Vertical Forge repository.

These verify that the project's quality-gate infrastructure is wired up
correctly and that the repo's foundational invariants hold. They are
intentionally lightweight — heavier tests live alongside the code they cover.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


pytestmark = pytest.mark.smoke


def test_repo_root_exists() -> None:
    """The repository root is discoverable and is a directory."""
    assert REPO_ROOT.is_dir(), f"repo root {REPO_ROOT} is not a directory"


def test_quality_gate_files_present() -> None:
    """Core quality-gate infrastructure files exist at the repo root."""
    expected = ["pyproject.toml", "requirements.txt", ".gitignore"]
    missing = [name for name in expected if not (REPO_ROOT / name).is_file()]
    assert not missing, f"missing quality-gate files: {missing}"


def test_factory_directories_present() -> None:
    """The factory's core engine directories are present."""
    expected_dirs = [
        "core/orchestrator",
        "core/orchestrator/phases",
        "factory/generators",
        "tools",
    ]
    missing = [d for d in expected_dirs if not (REPO_ROOT / d).is_dir()]
    assert not missing, f"missing factory directories: {missing}"


def test_pyyaml_importable() -> None:
    """PyYAML — the only runtime third-party dependency — imports cleanly."""
    import yaml  # noqa: F401

    assert hasattr(yaml, "safe_load")


def test_build_state_and_corrections_exist() -> None:
    """The two-tier loop's state files exist and are non-empty."""
    for rel in [".hermes/build-state.md", ".hermes/course-corrections.md"]:
        path = REPO_ROOT / rel
        assert path.is_file(), f"{rel} missing"
        assert path.stat().st_size > 0, f"{rel} is empty"
