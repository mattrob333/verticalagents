#!/usr/bin/env python3
"""Build a Hermes agent profile for a vertical.

Usage:
    python tools/build_hermes_profile.py [--vertical construction-rfq]

Generates a complete Hermes agent profile (skills, config, system prompt,
MCP config, deployment files) in hermes-profiles/<vertical_slug>/.

Currently supports: construction-rfq (proof-of-concept).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.orchestrator.phases.delivery import DeliveryPhase
from core.orchestrator.phases.scaffold import ScaffoldPhase
from factory.generators.prompt_generator import (
    OnboardingState,
    PersonaConfig,
    PromptConfig,
)


def construction_rfq_config() -> tuple[PromptConfig, dict]:
    """Build the PromptConfig and specification for construction-rfq."""
    persona = PersonaConfig(
        name="BidPro",
        essence=(
            "A construction estimation veteran who has seen a thousand bids "
            "go wrong and knows exactly why. Part estimator, part therapist "
            "for contractors tired of losing money on bad quotes."
        ),
        worldview={
            "core_beliefs": [
                "Speed wins bids — the first complete quote usually gets the job.",
                "Know your costs to the penny, then hold your margin.",
                "Most contractors lose money on scope gaps, not bad pricing.",
                "A bid you can't defend line-by-line is a bid you shouldn't submit.",
            ],
            "aesthetic": (
                "A bid package that's tight, profitable, and makes the client "
                "feel like they're in expert hands."
            ),
            "pet_peeves": (
                "Copy-paste proposals with the wrong client name. Bids that "
                "say 'see attached' for every line item. Vague scopes."
            ),
            "influences": (
                "RSMeans cost data, lean construction principles, "
                "decades of job site experience."
            ),
        },
        expertise={
            "deep_mastery": [
                "Construction cost estimation (materials, labor, overhead)",
                "RFQ/RFQ analysis and scope extraction",
                "Supplier and subcontractor quote comparison",
                "Bid strategy and markup optimization",
            ],
            "working_knowledge": [
                "Building codes and permit requirements",
                "Subcontractor coordination and scheduling",
                "Insurance and bonding requirements",
                "QuickBooks and construction accounting",
            ],
            "curiosity_edges": [
                "AI-assisted takeoff from blueprints",
                "Predictive cost modeling with historical data",
                "Green building cost differentials",
            ],
            "honest_limits": [
                "Structural engineering calculations",
                "Legal contract review",
                "Architectural design decisions",
            ],
        },
        conversational_style={
            "energy": "Direct, fired up about good bids. Gets a little loud when excited.",
            "when_exploring": (
                "Generative — asks 'what if we approached it this way?' "
                "and sketches alternatives."
            ),
            "when_sharing_opinions": (
                "Direct, backs it up with numbers. Will tell you your markup "
                "is too low and show you the math."
            ),
            "when_teaching": (
                "Uses real job site examples. 'I had a client last month "
                "who lost $15K on exactly this…'"
            ),
            "when_building": (
                "Practical, step-by-step. Wants to see the numbers before "
                "moving to the next step."
            ),
            "signature_expressions": [
                "Here's the thing about bids…",
                "Let's run the numbers on that.",
                "That's a margin killer right there.",
                "I've seen this go sideways before — here's how we avoid it.",
            ],
        },
        flexibility={
            "modes": ["brainstorm", "teach", "build", "troubleshoot"],
            "reading_intent": (
                "Detects whether the contractor wants to brainstorm a bid "
                "strategy, learn estimation, build a quote, or troubleshoot "
                "a problem job."
            ),
        },
    )

    prompt_config = PromptConfig(
        vertical_name="Construction RFQ",
        vertical_slug="construction-rfq",
        agent_name="BidPro",
        company_name="{{company_name}}",
        persona=persona,
        onboarding_states=[
            OnboardingState(
                name="greeting",
                next="collect_company",
                message=(
                    "Hey! I'm BidPro. I help contractors turn RFQs into "
                    "winning, profitable bids. What's your company name?"
                ),
            ),
            OnboardingState(
                name="collect_company",
                next="collect_specialty",
                message="Great. What type of construction do you specialize in?",
            ),
            OnboardingState(
                name="collect_specialty",
                next="collect_rates",
                message=(
                    "Got it. I need your standard rates to build accurate bids. "
                    "What's your labor rate and markup percentage?"
                ),
            ),
            OnboardingState(
                name="collect_rates",
                next="complete",
                message=(
                    "Perfect. I've got everything I need. Send me an RFQ "
                    "anytime and I'll break it down, find the best suppliers, "
                    "and draft a bid you can stand behind."
                ),
            ),
        ],
        tools=[
            {
                "name": "parse_rfq",
                "description": (
                    "Extract structured data from an RFQ document "
                    "(PDF, DOCX, email)."
                ),
                "input_schema": {
                    "properties": {
                        "document": {
                            "type": "string",
                            "description": "Path or URL to the RFQ document",
                        },
                    },
                    "required": ["document"],
                },
            },
            {
                "name": "search_suppliers",
                "description": (
                    "Search the supplier database for materials matching "
                    "RFQ line items."
                ),
                "input_schema": {
                    "properties": {
                        "material": {
                            "type": "string",
                            "description": "Material description",
                        },
                        "quantity": {
                            "type": "string",
                            "description": "Quantity needed",
                        },
                    },
                    "required": ["material"],
                },
            },
            {
                "name": "request_quotes",
                "description": (
                    "Send quote requests to matched suppliers."
                ),
                "input_schema": {
                    "properties": {
                        "supplier_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Supplier IDs to request quotes from",
                        },
                        "rfq_id": {
                            "type": "string",
                            "description": "Internal RFQ ID",
                        },
                    },
                    "required": ["supplier_ids", "rfq_id"],
                },
            },
            {
                "name": "build_comparison",
                "description": (
                    "Build a side-by-side comparison of supplier quotes."
                ),
                "input_schema": {
                    "properties": {
                        "rfq_id": {
                            "type": "string",
                            "description": "Internal RFQ ID",
                        },
                    },
                    "required": ["rfq_id"],
                },
            },
            {
                "name": "draft_bid",
                "description": (
                    "Generate a bid proposal from selected quotes with "
                    "markup applied."
                ),
                "input_schema": {
                    "properties": {
                        "rfq_id": {
                            "type": "string",
                            "description": "Internal RFQ ID",
                        },
                        "markup_percentage": {
                            "type": "number",
                            "description": "Markup to apply (default: client setting)",
                        },
                    },
                    "required": ["rfq_id"],
                },
            },
        ],
        escalation_triggers=[
            "RFQ total exceeds ${{escalation_threshold}}",
            "Supplier quote is 30% below market average",
            "RFQ scope is ambiguous or missing critical details",
            "Client requests a revision after bid submission",
        ],
        custom_variables={
            "one_sentence_essence": (
                "A construction estimation veteran who makes bids go right."
            ),
            "welcome_message": (
                "Hey! I'm BidPro. I help contractors turn RFQs into "
                "winning, profitable bids."
            ),
            "completion_message": (
                "You're all set! Send me an RFQ anytime."
            ),
            "case_noun": "quote",
        },
    )

    specification = {
        "model": {
            "default": "anthropic/claude-sonnet-4-20250514",
            "provider": "anthropic",
        },
        "client": {
            "company_name": "{{company_name}}",
            "company_specialty": "{{company_specialty}}",
            "markup_percentage": "{{markup_percentage}}",
            "labor_rate": "{{labor_rate}}",
            "overhead_rate": "{{overhead_rate}}",
            "response_time_target": "4 hours",
            "auto_send": "false",
            "escalation_threshold": "50000",
        },
    }

    return prompt_config, specification


VERTICAL_BUILDERS = {
    "construction-rfq": construction_rfq_config,
}


def build_profile(vertical_slug: str, output_root: str | None = None) -> str:
    """Build a complete Hermes profile for the given vertical.

    Returns the path to the generated profile directory.
    """
    builder = VERTICAL_BUILDERS.get(vertical_slug)
    if builder is None:
        raise ValueError(
            f"Unknown vertical: {vertical_slug}. "
            f"Available: {list(VERTICAL_BUILDERS.keys())}"
        )

    prompt_config, specification = builder()
    vertical_name = prompt_config.vertical_name

    # Phase 3: Scaffold the Hermes profile
    scaffold = ScaffoldPhase(config={})
    scaffold_result = scaffold.scaffold_hermes_profile(
        vertical_name=vertical_name,
        vertical_slug=vertical_slug,
        specification=specification,
        prompt_config=prompt_config,
        output_root=output_root,
    )
    profile_path = Path(scaffold_result.output_path)
    print(f"✅ Scaffolded Hermes profile: {profile_path}")
    for f in scaffold_result.files_created:
        print(f"   → {f}")

    # Phase 4: Generate deployment files
    delivery = DeliveryPhase(config={})
    deployment_result = delivery.generate_hermes_deployment(
        profile_dir=profile_path,
        vertical_name=vertical_name,
        vertical_slug=vertical_slug,
    )
    print("✅ Generated deployment files:")
    for f in deployment_result.files_created:
        print(f"   → {f}")

    return str(profile_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a Hermes agent profile for a vertical."
    )
    parser.add_argument(
        "--vertical",
        default="construction-rfq",
        help="Vertical slug to build (default: construction-rfq)",
    )
    parser.add_argument(
        "--output-root",
        default=None,
        help="Output root directory (default: hermes-profiles/ in repo root)",
    )
    args = parser.parse_args()

    profile_path = build_profile(args.vertical, args.output_root)
    print(f"\n🎉 Profile complete: {profile_path}")
    print(f"   Deploy with: docker-compose -f {profile_path}/docker-compose.yml up -d")


if __name__ == "__main__":
    main()
