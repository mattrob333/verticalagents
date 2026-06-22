"""Tests for the Hermes-compatible prompt generator.

Verifies that `DualModePromptGenerator` can output Hermes-native system
prompts (markdown format) from the profile template, preserving the
dual-mode architecture and persona system.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from factory.generators.prompt_generator import (
    DualModePromptGenerator,
    OnboardingState,
    PersonaConfig,
    PromptConfig,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
HERMES_TEMPLATE = REPO_ROOT / "hermes-profiles" / "_template" / "system-prompt.md"


pytestmark = pytest.mark.unit


@pytest.fixture
def generator() -> DualModePromptGenerator:
    return DualModePromptGenerator(factory_root=REPO_ROOT)


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
        flexibility={
            "modes": ["brainstorm", "teach", "build", "troubleshoot"],
        },
    )


@pytest.fixture
def sample_config(sample_persona: PersonaConfig) -> PromptConfig:
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
                message="Hi! I'm BidPro. Ready to get started?",
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
        escalation_triggers=[
            "RFQ total exceeds ${{escalation_threshold}}",
            "Deadline is less than 24 hours away",
        ],
        custom_variables={
            "one_sentence_essence": "A construction estimation veteran.",
            "welcome_message": "Hey, I'm BidPro.",
            "completion_message": "You're all set!",
            "case_noun": "quote",
        },
    )


class TestHermesPromptGeneration:
    """Test the generate_hermes method — Hermes-native markdown output."""

    def test_hermes_template_exists(self, generator: DualModePromptGenerator) -> None:
        assert HERMES_TEMPLATE.is_file()

    def test_generate_hermes_returns_string(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        result = generator.generate_hermes(sample_config)
        assert isinstance(result, str)
        assert len(result) > 100

    def test_generate_hermes_resolves_agent_name(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        result = generator.generate_hermes(sample_config)
        assert "BidPro" in result
        assert "{{agent_name}}" not in result

    def test_generate_hermes_resolves_vertical_name(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        result = generator.generate_hermes(sample_config)
        assert "Construction RFQ" in result
        assert "{{vertical_name}}" not in result

    def test_generate_hermes_preserves_dual_mode(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        """The crown jewel: dual-mode architecture must be present in output."""
        result = generator.generate_hermes(sample_config)
        assert "ONBOARDING MODE" in result
        assert "CONSULTATION MODE" in result
        assert "Mode Router" in result

    def test_generate_hermes_includes_persona_worldview(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        result = generator.generate_hermes(sample_config)
        assert "Speed wins bids" in result
        assert "Know your costs" in result

    def test_generate_hermes_includes_persona_expertise(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        result = generator.generate_hermes(sample_config)
        assert "Construction estimation" in result
        assert "Building codes" in result

    def test_generate_hermes_includes_escalation_triggers(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        result = generator.generate_hermes(sample_config)
        assert "Deadline is less than 24 hours" in result

    def test_generate_hermes_includes_tools(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        result = generator.generate_hermes(sample_config)
        assert "parse_document" in result
        assert "Extract text from PDF" in result

    def test_generate_hermes_includes_onboarding_states(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        result = generator.generate_hermes(sample_config)
        assert "greeting" in result
        assert "collect_info" in result

    def test_generate_hermes_no_unresolved_placeholders(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        """All template variables that have values should be resolved."""
        result = generator.generate_hermes(sample_config)
        # These should all be resolved
        assert "{{agent_name}}" not in result
        assert "{{vertical_name}}" not in result
        assert "{{vertical_slug}}" not in result
        assert "{{one_sentence_essence}}" not in result
        # Company name stays as a runtime template variable (per-client)
        assert "{{company_name}}" in result

    def test_generate_hermes_renders_persona_as_markdown_not_xml(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        """Hermes output uses markdown, not XML like the old format."""
        result = generator.generate_hermes(sample_config)
        # Should NOT contain XML tags from the old renderer
        assert "<worldview>" not in result
        assert "<core_beliefs>" not in result
        assert "<expertise>" not in result


class TestHermesPersonaSkillGeneration:
    """Test generating the persona skill file (SKILL.md) for Hermes profiles."""

    def test_generate_persona_skill_returns_string(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        result = generator.generate_hermes_persona_skill(sample_config)
        assert isinstance(result, str)
        assert len(result) > 100

    def test_persona_skill_has_frontmatter(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        result = generator.generate_hermes_persona_skill(sample_config)
        assert result.startswith("---")
        assert "name:" in result

    def test_persona_skill_contains_worldview(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        result = generator.generate_hermes_persona_skill(sample_config)
        assert "Worldview" in result or "worldview" in result.lower()
        assert "Speed wins bids" in result

    def test_persona_skill_contains_expertise(
        self, generator: DualModePromptGenerator, sample_config: PromptConfig
    ) -> None:
        result = generator.generate_hermes_persona_skill(sample_config)
        assert "Expertise" in result or "expertise" in result.lower()
        assert "Construction estimation" in result

    @pytest.mark.parametrize(
        "heading",
        [
            "### Core Beliefs",
            "### What They Find Beautiful",
            "### What Makes Them Cringe",
            "### Influences",
            "### Deep Mastery",
            "### Working Knowledge",
            "### Curiosity Edges",
            "### How They Talk",
            "### Quirks",
            "### Flexibility",
        ],
    )
    def test_persona_skill_no_duplicate_subsection_headings(
        self,
        generator: DualModePromptGenerator,
        sample_config: PromptConfig,
        heading: str,
    ) -> None:
        """Regression: each persona subsection heading must appear exactly once.

        Previously the template had both full-block placeholders (rendered with
        sub-headings) AND hardcoded sub-headings with granular placeholders,
        causing every heading to appear twice.
        """
        result = generator.generate_hermes_persona_skill(sample_config)
        assert result.count(heading) == 1, (
            f"Expected '{heading}' to appear exactly once, "
            f"found {result.count(heading)} times"
        )
