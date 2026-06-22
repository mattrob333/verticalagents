"""Tests for the Hermes agent profile template structure.

Validates that `hermes-profiles/_template/` contains all the files and
directories the factory's scaffold phase must produce, and that the YAML
templates parse without errors.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "hermes-profiles" / "_template"


pytestmark = pytest.mark.unit


# Files that must exist at the template root level
EXPECTED_FILES = [
    "README.md",
    "config.yaml",
    "system-prompt.md",
    "onboarding.yaml",
    "mcp-config.yaml",
    "gateway.yaml",
]

# Directories that must exist in the template
EXPECTED_DIRS = [
    "skills",
    "skills/persona-template",
    "cron",
    "migrations",
]


@pytest.fixture(params=EXPECTED_FILES)
def template_file(request: pytest.FixtureRequest) -> Path:
    path = TEMPLATE_DIR / request.param
    if not path.is_file():
        pytest.fail(f"missing template file: {request.param}")
    return path


@pytest.fixture(params=EXPECTED_DIRS)
def template_dir(request: pytest.FixtureRequest) -> Path:
    path = TEMPLATE_DIR / request.param
    if not path.is_dir():
        pytest.fail(f"missing template directory: {request.param}")
    return path


def test_template_root_exists() -> None:
    assert TEMPLATE_DIR.is_dir(), f"template dir missing: {TEMPLATE_DIR}"


def test_template_file_exists(template_file: Path) -> None:
    assert template_file.is_file()
    assert template_file.stat().st_size > 0, f"{template_file.name} is empty"


def test_template_dir_exists(template_dir: Path) -> None:
    assert template_dir.is_dir()


def test_persona_skill_exists() -> None:
    skill = TEMPLATE_DIR / "skills" / "persona-template" / "SKILL.md"
    assert skill.is_file(), "persona-template SKILL.md missing"
    content = skill.read_text()
    assert "Worldview" in content or "worldview" in content.lower()
    assert "Expertise" in content or "expertise" in content.lower()


def test_cron_job_exists() -> None:
    cron = TEMPLATE_DIR / "cron" / "daily-checkin.md"
    assert cron.is_file(), "daily-checkin.md cron job missing"
    content = cron.read_text()
    assert "schedule" in content.lower()


def test_migration_schema_exists() -> None:
    schema = TEMPLATE_DIR / "migrations" / "schema.sql"
    assert schema.is_file(), "schema.sql migration missing"
    content = schema.read_text()
    assert "CREATE TABLE" in content.upper()


def test_config_yaml_parses() -> None:
    config_path = TEMPLATE_DIR / "config.yaml"
    data = yaml.safe_load(config_path.read_text())
    assert isinstance(data, dict)
    assert "model" in data
    assert "agent" in data
    assert "gateway" in data


def test_onboarding_yaml_parses() -> None:
    path = TEMPLATE_DIR / "onboarding.yaml"
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict)
    assert "states" in data
    assert isinstance(data["states"], list)
    assert len(data["states"]) >= 3


def test_mcp_config_yaml_parses() -> None:
    path = TEMPLATE_DIR / "mcp-config.yaml"
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict)
    assert "servers" in data
    assert isinstance(data["servers"], list)
    assert len(data["servers"]) >= 1


def test_gateway_yaml_parses() -> None:
    path = TEMPLATE_DIR / "gateway.yaml"
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict)
    assert "telegram" in data


def test_system_prompt_has_dual_mode() -> None:
    """The crown jewel: dual-mode architecture must be present in the template."""
    path = TEMPLATE_DIR / "system-prompt.md"
    content = path.read_text()
    assert "ONBOARDING MODE" in content, "onboarding mode missing from system prompt"
    assert "CONSULTATION MODE" in content, "consultation mode missing from system prompt"
    assert "Mode Router" in content, "mode router missing from system prompt"


def test_system_prompt_preserves_persona_reference() -> None:
    """The system prompt must reference the persona skill (crown jewel preservation)."""
    path = TEMPLATE_DIR / "system-prompt.md"
    content = path.read_text()
    assert "worldview" in content.lower(), "worldview reference missing"
    assert "expertise" in content.lower(), "expertise reference missing"
