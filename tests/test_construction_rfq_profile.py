"""End-to-end test for building a complete Hermes vertical agent profile.

Verifies that the build_hermes_profile script produces a deployable profile
with all required files, persona content, and deployment artifacts.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.build_hermes_profile import build_profile  # noqa: E402

pytestmark = pytest.mark.integration


@pytest.fixture
def built_profile(tmp_path: Path) -> Path:
    """Build the construction-rfq profile into a temp directory."""
    profile_path = build_profile("construction-rfq", output_root=str(tmp_path))
    return Path(profile_path)


class TestConstructionRfqProfile:
    """Test the construction-rfq proof-of-concept profile."""

    def test_profile_directory_exists(self, built_profile: Path) -> None:
        assert built_profile.is_dir()
        assert built_profile.name == "construction-rfq"

    def test_has_all_required_files(self, built_profile: Path) -> None:
        required = [
            "config.yaml",
            "mcp-config.yaml",
            "gateway.yaml",
            "onboarding.yaml",
            "system-prompt.md",
            "README.md",
            "DEPLOY.md",
            "Dockerfile",
            "docker-compose.yml",
            ".env.example",
            "cron/daily-checkin.md",
            "migrations/schema.sql",
            "skills/construction-rfq-persona/SKILL.md",
        ]
        for fname in required:
            fpath = built_profile / fname
            assert fpath.is_file(), f"Missing required file: {fname}"

    def test_system_prompt_has_dual_mode(self, built_profile: Path) -> None:
        content = (built_profile / "system-prompt.md").read_text()
        # Dual-mode architecture markers
        assert "ONBOARDING" in content.upper() or "onboarding" in content.lower()
        assert "Mode Router" in content or "mode" in content.lower()
        # Persona identity
        assert "BidPro" in content

    def test_persona_skill_has_worldview(self, built_profile: Path) -> None:
        content = (
            built_profile / "skills" / "construction-rfq-persona" / "SKILL.md"
        ).read_text()
        # Crown jewel: worldview must be preserved
        assert "worldview" in content.lower() or "Worldview" in content
        assert "BidPro" in content
        # Core beliefs present
        assert "belief" in content.lower() or "Belief" in content

    def test_persona_skill_has_expertise(self, built_profile: Path) -> None:
        content = (
            built_profile / "skills" / "construction-rfq-persona" / "SKILL.md"
        ).read_text()
        assert "expertise" in content.lower() or "Expertise" in content
        assert "deep" in content.lower() or "mastery" in content.lower()

    def test_persona_skill_has_conversational_style(self, built_profile: Path) -> None:
        content = (
            built_profile / "skills" / "construction-rfq-persona" / "SKILL.md"
        ).read_text()
        assert "style" in content.lower() or "Style" in content
        # Conversational style includes energy/directness/modes
        assert "direct" in content.lower() or "energy" in content.lower()

    def test_config_yaml_has_model(self, built_profile: Path) -> None:
        content = (built_profile / "config.yaml").read_text()
        assert "model" in content.lower() or "claude" in content.lower()

    def test_mcp_config_has_tools(self, built_profile: Path) -> None:
        content = (built_profile / "mcp-config.yaml").read_text()
        assert "mcp" in content.lower() or "server" in content.lower()

    def test_env_example_has_required_keys(self, built_profile: Path) -> None:
        content = (built_profile / ".env.example").read_text()
        assert "TELEGRAM_BOT_TOKEN" in content
        assert "SENDGRID_API_KEY" in content
        assert "DATABASE_URL" in content

    def test_dockerfile_uses_python(self, built_profile: Path) -> None:
        content = (built_profile / "Dockerfile").read_text()
        assert "python" in content.lower()
        assert "hermes" in content.lower()

    def test_deploy_readme_mentions_vertical(self, built_profile: Path) -> None:
        content = (built_profile / "DEPLOY.md").read_text()
        assert "construction-rfq" in content.lower()
        assert "hermes" in content.lower()

    def test_onboarding_yaml_has_states(self, built_profile: Path) -> None:
        content = (built_profile / "onboarding.yaml").read_text()
        assert "greeting" in content.lower() or "collect" in content.lower()
