"""Tests for the Hermes profile scaffold phase.

Verifies that `ScaffoldPhase.scaffold_hermes_profile()` generates a complete
Hermes agent profile directory from the template, with resolved persona values
and all required config files.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from core.orchestrator.phases.scaffold import (
    HermesProfileResult,
    ScaffoldPhase,
)
from factory.generators.prompt_generator import (
    OnboardingState,
    PersonaConfig,
    PromptConfig,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.unit


@pytest.fixture
def sample_persona() -> PersonaConfig:
    return PersonaConfig(
        name="BidPro",
        essence="A construction estimation veteran who makes bids go right.",
        worldview={
            "core_beliefs": ["Speed wins bids.", "Know your costs, hold your margin."],
            "aesthetic": "A bid that's tight, profitable, and wins.",
            "pet_peeves": "Copy-paste proposals with the wrong client name.",
            "influences": "RSMeans data, lean construction principles.",
        },
        expertise={
            "deep_mastery": ["Construction estimation", "RFQ analysis"],
            "working_knowledge": ["Building codes", "Subcontractor coordination"],
            "curiosity_edges": ["AI in construction"],
            "honest_limits": ["Structural engineering"],
        },
        conversational_style={
            "energy": "Direct, fired up about good bids",
            "when_exploring": "Generative, asks 'what if'",
            "when_sharing_opinions": "Direct, backs it up with numbers",
            "when_teaching": "Uses real job site examples",
            "when_building": "Practical, step-by-step",
            "signature_expressions": ["Here's the thing about bids..."],
        },
        flexibility={"modes": ["brainstorm", "teach", "build", "troubleshoot"]},
    )


@pytest.fixture
def sample_prompt_config(sample_persona: PersonaConfig) -> PromptConfig:
    return PromptConfig(
        vertical_name="Construction RFQ",
        vertical_slug="construction-rfq",
        agent_name="BidPro",
        company_name="{{company_name}}",
        persona=sample_persona,
        onboarding_states=[
            OnboardingState(
                name="greeting",
                next="collect_info",
                message="Hi! I'm BidPro.",
            ),
            OnboardingState(
                name="collect_info",
                next="complete",
                message="Let's get your project details.",
            ),
        ],
        tools=[
            {
                "name": "parse_document",
                "description": "Extract text from PDF/DOCX",
                "input_schema": {
                    "properties": {
                        "file": {"type": "string", "description": "File path"},
                    },
                    "required": ["file"],
                },
            }
        ],
        escalation_triggers=["RFQ total exceeds ${{escalation_threshold}}"],
        custom_variables={
            "one_sentence_essence": "A construction estimation veteran.",
            "welcome_message": "Hey, I'm BidPro.",
            "completion_message": "You're all set!",
            "case_noun": "quote",
        },
    )


@pytest.fixture
def sample_specification() -> dict:
    return {
        "model": {
            "default": "anthropic/claude-sonnet-4.6",
            "provider": "openrouter",
        },
        "client": {
            "company_name": "{{company_name}}",
            "company_specialty": "construction contractor",
            "markup_percentage": "15",
            "labor_rate": "85",
            "overhead_rate": "12",
            "response_time_target": "4 hours",
            "auto_send": "false",
            "escalation_threshold": "50000",
        },
    }


@pytest.fixture
def phase() -> ScaffoldPhase:
    return ScaffoldPhase(config={})


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Temporary output root for profile generation."""
    return tmp_path / "hermes-profiles-output"


class TestHermesScaffoldStructure:
    """Test that scaffold_hermes_profile creates the correct directory structure."""

    def test_creates_profile_directory(
        self,
        phase: ScaffoldPhase,
        sample_prompt_config: PromptConfig,
        sample_specification: dict,
        output_dir: Path,
    ) -> None:
        result = phase.scaffold_hermes_profile(
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
            specification=sample_specification,
            prompt_config=sample_prompt_config,
            output_root=str(output_dir),
        )
        profile_dir = output_dir / "construction-rfq"
        assert profile_dir.is_dir()
        assert result.profile_slug == "construction-rfq"

    def test_creates_all_required_files(
        self,
        phase: ScaffoldPhase,
        sample_prompt_config: PromptConfig,
        sample_specification: dict,
        output_dir: Path,
    ) -> None:
        phase.scaffold_hermes_profile(
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
            specification=sample_specification,
            prompt_config=sample_prompt_config,
            output_root=str(output_dir),
        )
        profile_dir = output_dir / "construction-rfq"
        expected_files = [
            "system-prompt.md",
            "config.yaml",
            "mcp-config.yaml",
            "gateway.yaml",
            "onboarding.yaml",
            "README.md",
        ]
        for fname in expected_files:
            assert (profile_dir / fname).is_file(), f"missing: {fname}"
        # Persona skill
        skill_path = profile_dir / "skills" / "construction-rfq-persona" / "SKILL.md"
        assert skill_path.is_file(), "persona skill SKILL.md missing"

    def test_returns_result_with_files_list(
        self,
        phase: ScaffoldPhase,
        sample_prompt_config: PromptConfig,
        sample_specification: dict,
        output_dir: Path,
    ) -> None:
        result = phase.scaffold_hermes_profile(
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
            specification=sample_specification,
            prompt_config=sample_prompt_config,
            output_root=str(output_dir),
        )
        assert isinstance(result, HermesProfileResult)
        assert len(result.files_created) >= 6
        assert result.output_path.endswith("construction-rfq")


class TestHermesScaffoldContent:
    """Test that scaffold output has correct content with resolved variables."""

    def test_system_prompt_has_resolved_persona(
        self,
        phase: ScaffoldPhase,
        sample_prompt_config: PromptConfig,
        sample_specification: dict,
        output_dir: Path,
    ) -> None:
        phase.scaffold_hermes_profile(
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
            specification=sample_specification,
            prompt_config=sample_prompt_config,
            output_root=str(output_dir),
        )
        prompt = (output_dir / "construction-rfq" / "system-prompt.md").read_text()
        assert "BidPro" in prompt
        assert "Speed wins bids" in prompt
        assert "CONSULTATION MODE" in prompt
        assert "ONBOARDING MODE" in prompt

    def test_config_yaml_has_model_settings(
        self,
        phase: ScaffoldPhase,
        sample_prompt_config: PromptConfig,
        sample_specification: dict,
        output_dir: Path,
    ) -> None:
        phase.scaffold_hermes_profile(
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
            specification=sample_specification,
            prompt_config=sample_prompt_config,
            output_root=str(output_dir),
        )
        config = (output_dir / "construction-rfq" / "config.yaml").read_text()
        assert "anthropic/claude-sonnet-4.6" in config
        assert "openrouter" in config

    def test_mcp_config_has_vertical_slug(
        self,
        phase: ScaffoldPhase,
        sample_prompt_config: PromptConfig,
        sample_specification: dict,
        output_dir: Path,
    ) -> None:
        phase.scaffold_hermes_profile(
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
            specification=sample_specification,
            prompt_config=sample_prompt_config,
            output_root=str(output_dir),
        )
        mcp = (output_dir / "construction-rfq" / "mcp-config.yaml").read_text()
        assert "construction-rfq" in mcp

    def test_persona_skill_has_frontmatter_and_worldview(
        self,
        phase: ScaffoldPhase,
        sample_prompt_config: PromptConfig,
        sample_specification: dict,
        output_dir: Path,
    ) -> None:
        phase.scaffold_hermes_profile(
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
            specification=sample_specification,
            prompt_config=sample_prompt_config,
            output_root=str(output_dir),
        )
        skill = (
            output_dir / "construction-rfq" / "skills" / "construction-rfq-persona" / "SKILL.md"
        ).read_text()
        assert skill.startswith("---")
        assert "BidPro" in skill
        assert "Speed wins bids" in skill

    def test_onboarding_yaml_has_resolved_vars(
        self,
        phase: ScaffoldPhase,
        sample_prompt_config: PromptConfig,
        sample_specification: dict,
        output_dir: Path,
    ) -> None:
        phase.scaffold_hermes_profile(
            vertical_name="Construction RFQ",
            vertical_slug="construction-rfq",
            specification=sample_specification,
            prompt_config=sample_prompt_config,
            output_root=str(output_dir),
        )
        onboarding = (output_dir / "construction-rfq" / "onboarding.yaml").read_text()
        assert "construction-rfq" in onboarding
        assert "BidPro" in onboarding
