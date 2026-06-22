"""Tests for the Hermes deployment generation in delivery.py.

Verifies that `DeliveryPhase.generate_hermes_deployment()` creates
deployment-ready configuration files for a Hermes agent profile.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from core.orchestrator.phases.delivery import (
    DeliveryPhase,
    HermesDeploymentResult,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.unit


@pytest.fixture
def phase() -> DeliveryPhase:
    return DeliveryPhase(config={})


@pytest.fixture
def profile_dir(tmp_path: Path) -> Path:
    """Simulated Hermes profile directory."""
    d = tmp_path / "construction-rfq"
    d.mkdir(parents=True)
    (d / "config.yaml").write_text("# Hermes config")
    (d / "system-prompt.md").write_text("# Prompt")
    return d


class TestHermesDeploymentStructure:
    """Test that generate_hermes_deployment creates the correct files."""

    def test_creates_deployment_files(
        self,
        phase: DeliveryPhase,
        profile_dir: Path,
    ) -> None:
        result = phase.generate_hermes_deployment(
            profile_dir=profile_dir,
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
        )
        assert isinstance(result, HermesDeploymentResult)
        # Should create at least: Dockerfile, docker-compose, .env.example, README
        assert len(result.files_created) >= 4
        for fpath in result.files_created:
            assert Path(fpath).exists(), f"file not created: {fpath}"

    def test_creates_dockerfile(
        self,
        phase: DeliveryPhase,
        profile_dir: Path,
    ) -> None:
        phase.generate_hermes_deployment(
            profile_dir=profile_dir,
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
        )
        dockerfile = profile_dir / "Dockerfile"
        assert dockerfile.is_file()
        content = dockerfile.read_text()
        assert "hermes" in content.lower()

    def test_creates_docker_compose(
        self,
        phase: DeliveryPhase,
        profile_dir: Path,
    ) -> None:
        phase.generate_hermes_deployment(
            profile_dir=profile_dir,
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
        )
        compose = profile_dir / "docker-compose.yml"
        assert compose.is_file()
        content = compose.read_text()
        assert "hermes" in content.lower()

    def test_creates_env_example(
        self,
        phase: DeliveryPhase,
        profile_dir: Path,
    ) -> None:
        phase.generate_hermes_deployment(
            profile_dir=profile_dir,
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
        )
        env = profile_dir / ".env.example"
        assert env.is_file()
        content = env.read_text()
        assert "TELEGRAM_BOT_TOKEN" in content

    def test_creates_deployment_readme(
        self,
        phase: DeliveryPhase,
        profile_dir: Path,
    ) -> None:
        phase.generate_hermes_deployment(
            profile_dir=profile_dir,
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
        )
        readme = profile_dir / "DEPLOY.md"
        assert readme.is_file()
        content = readme.read_text()
        assert "construction-rfq" in content.lower()
        assert "hermes" in content.lower()


class TestHermesDeploymentContent:
    """Test that deployment content is correct."""

    def test_env_has_mcp_keys(
        self,
        phase: DeliveryPhase,
        profile_dir: Path,
    ) -> None:
        phase.generate_hermes_deployment(
            profile_dir=profile_dir,
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
        )
        content = (profile_dir / ".env.example").read_text()
        # MCP-related env vars referenced in mcp-config.yaml template
        assert "SENDGRID_API_KEY" in content
        assert "DATABASE_URL" in content

    def test_dockerfile_uses_python(
        self,
        phase: DeliveryPhase,
        profile_dir: Path,
    ) -> None:
        phase.generate_hermes_deployment(
            profile_dir=profile_dir,
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
        )
        content = (profile_dir / "Dockerfile").read_text()
        # Hermes runs on Python
        assert "python" in content.lower()

    def test_result_has_profile_path(
        self,
        phase: DeliveryPhase,
        profile_dir: Path,
    ) -> None:
        result = phase.generate_hermes_deployment(
            profile_dir=profile_dir,
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
        )
        assert result.profile_path == str(profile_dir)
        assert result.vertical_slug == "construction-rfq"
