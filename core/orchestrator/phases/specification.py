"""
Specification Phase - Generate complete agent specifications.

This phase:
1. Generates VERTICAL.md specification from discovery
2. Creates dual-mode system prompt (onboarding + consultation)
3. Defines tools in MCP format
4. Creates onboarding flow with A2UI component mappings
5. Saves artifacts to verticals/[slug]/
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import date

# Add factory directory to path for imports
factory_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(factory_root))

from factory.generators.prompt_generator import (
    DualModePromptGenerator,
    PromptConfig,
    PersonaConfig,
    OnboardingState
)


@dataclass
class ToolDefinition:
    """MCP-format tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    returns: str

    def to_mcp(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "returns": self.returns
        }


@dataclass
class OnboardingStep:
    """A step in the onboarding flow"""
    id: str
    title: str
    description: str
    fields: List[Dict[str, Any]]
    validation: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "fields": self.fields,
            "validation": self.validation
        }


class SpecificationPhase:
    """
    Specification Phase Handler

    Generates complete agent specification from discovery report.
    Creates all artifacts needed for the build phase.
    """

    def __init__(self, config):
        self.config = config
        self.factory_root = Path(__file__).parent.parent.parent.parent

    async def execute(
        self,
        vertical_name: str,
        vertical_slug: str,
        workflow: str,
        discovery_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the specification phase.

        Args:
            vertical_name: Human-readable vertical name
            vertical_slug: URL-friendly slug
            workflow: Selected workflow to automate
            discovery_report: Output from discovery phase

        Returns:
            Specification with all generated artifacts
        """
        # Step 1: Generate VERTICAL.md
        vertical_spec = await self._generate_vertical_spec(
            vertical_name,
            vertical_slug,
            workflow,
            discovery_report
        )

        # Step 2: Define tools (needed for persona generation)
        tools = await self._define_tools(
            workflow,
            discovery_report
        )

        # Step 3: Generate dual-mode system prompt
        # This now uses the DualModePromptGenerator which creates both
        # onboarding controller (deterministic) and consultation persona (flexible)
        system_prompt = await self._generate_persona(
            vertical_name,
            vertical_slug,
            workflow,
            discovery_report,
            tools  # Pass tools for injection into system prompt
        )

        # Step 4: Create onboarding flow (for reference/external use)
        # Note: The onboarding states are now embedded in the system prompt,
        # but we also create a standalone flow.yaml for tooling/UI purposes
        onboarding = await self._create_onboarding_flow(
            vertical_name,
            workflow,
            tools
        )

        # Step 5: Save artifacts (if configured)
        if self.config.save_artifacts:
            await self._save_artifacts(
                vertical_slug,
                vertical_spec,
                system_prompt,
                tools,
                onboarding
            )

        return {
            "vertical_spec": vertical_spec,
            "system_prompt": system_prompt,  # Dual-mode system prompt (replaces persona)
            "tools": [t.to_mcp() for t in tools],
            "onboarding": [s.to_dict() for s in onboarding],
            "artifacts_saved": self.config.save_artifacts,
            "artifacts_path": str(self.factory_root / "verticals" / vertical_slug),
            "prompt_engine": "dual-mode"  # Indicator of which engine was used
        }

    async def _generate_vertical_spec(
        self,
        vertical_name: str,
        vertical_slug: str,
        workflow: str,
        discovery: Dict[str, Any]
    ) -> str:
        """Generate VERTICAL.md specification"""

        # Load template
        template_path = self.factory_root / "verticals" / "_template" / "VERTICAL.md"
        if template_path.exists():
            template = template_path.read_text()
        else:
            template = self._get_default_template()

        # This will be populated by Claude during the conversation
        # The template provides structure, Claude fills in the content
        spec = f"""---
vertical: {vertical_slug}
status: specification
created: {date.today().isoformat()}
confidence: {discovery.get('confidence', 'medium')}
workflow: {workflow}
---

# {vertical_name} Vertical Spec

## Market Overview

{self._format_market_data(discovery.get('market_data', {}))}

## Target Workflow: {workflow}

### Current State

**Process Description:**
[To be filled based on discovery research]

**Who Does It:**
[Role/title of person handling this]

**Time Investment:**
- Hours per week: [X]
- Frequency: [daily/weekly/per-event]

**Current Tools:**
[List from discovery]

**Pain Points:**
{self._format_pain_points(discovery.get('market_data', {}).get('key_pain_points', []))}

### Desired State

**What "Solved" Looks Like:**
[Describe the ideal end state with this agent]

**Success Metrics:**
- [ ] Time saved: [X] hrs/week
- [ ] Error reduction: [X]%
- [ ] Customer satisfaction: [X]%

### Agent Scope

**Primary Function:**
This agent [one sentence description].

**Core Capabilities:**
1. [Capability 1]: [What it does, why it matters]
2. [Capability 2]: [What it does, why it matters]
3. [Capability 3]: [What it does, why it matters]
4. [Capability 4]: [What it does, why it matters]
5. [Capability 5]: [What it does, why it matters]

**Out of Scope:**
- [Thing the agent does NOT do]
- [Another exclusion]

### Integration Requirements

| System | Purpose | API Available? | Complexity |
|--------|---------|----------------|------------|
| [System 1] | [Why needed] | Yes/No | Low/Med/High |
| [System 2] | [Why needed] | Yes/No | Low/Med/High |

### Pricing Model

{self._format_pricing(discovery.get('pricing_recommendation', {}))}

### Competition

{self._format_competition(discovery.get('market_data', {}).get('existing_solutions', []))}

## Recommendation

**Decision:** [X] GO / [ ] NO-GO

**Confidence Level:** {discovery.get('confidence', 'Medium')}

**Key Reasons:**
1. [Reason 1]
2. [Reason 2]
3. [Reason 3]
"""
        return spec

    async def _generate_persona(
        self,
        vertical_name: str,
        vertical_slug: str,
        workflow: str,
        discovery: Dict[str, Any],
        tools: Optional[List[ToolDefinition]] = None
    ) -> str:
        """
        Generate dual-mode agent system prompt.

        Uses the DualModePromptGenerator to create a complete system prompt
        with both ONBOARDING_CONTROLLER (deterministic) and CONSULTATION_PERSONA
        (flexible thinking partner) modes.

        Returns complete XML system prompt ready for deployment.
        """
        # Initialize the dual-mode generator
        generator = DualModePromptGenerator(self.factory_root)

        # Check if we have a pre-built persona for this vertical
        persona = generator.load_persona(vertical_slug)

        if persona:
            # Use the existing persona template
            try:
                # Convert tools to the expected format
                tool_defs = []
                if tools:
                    tool_defs = [t.to_mcp() for t in tools]

                # Generate using the vertical's persona
                system_prompt = generator.generate_for_vertical(
                    vertical_slug=vertical_slug,
                    company_name="{{COMPANY_NAME}}",
                    tools=tool_defs
                )
                return system_prompt
            except Exception as e:
                # Fall back to custom generation if persona generation fails
                pass

        # If no pre-built persona, generate a custom one
        # This creates a template that can be customized
        custom_persona = self._generate_custom_persona(
            vertical_name,
            vertical_slug,
            workflow,
            discovery
        )

        # Build custom onboarding states based on workflow
        custom_states = self._build_custom_onboarding_states(
            workflow,
            discovery
        )

        # Convert tools to expected format
        tool_defs = []
        if tools:
            tool_defs = [t.to_mcp() for t in tools]

        # Create configuration
        config = PromptConfig(
            vertical_name=vertical_name,
            vertical_slug=vertical_slug,
            agent_name=custom_persona.name,
            company_name="{{COMPANY_NAME}}",
            persona=custom_persona,
            onboarding_states=custom_states,
            tools=tool_defs,
            escalation_triggers=self._get_escalation_triggers(vertical_slug, discovery)
        )

        return generator.generate(config)

    def _generate_custom_persona(
        self,
        vertical_name: str,
        vertical_slug: str,
        workflow: str,
        discovery: Dict[str, Any]
    ) -> PersonaConfig:
        """
        Generate a custom persona configuration for verticals without
        pre-built persona templates.

        This creates a reasonable default that can be customized.
        """
        # Extract industry context from discovery
        market_data = discovery.get('market_data', {})
        pain_points = market_data.get('key_pain_points', [])

        # Build persona based on workflow type
        workflow_lower = workflow.lower()

        # Determine appropriate tone/style based on industry
        if any(term in vertical_slug for term in ['law', 'legal', 'attorney']):
            energy = "calm, reassuring, professional"
            essence = f"Compassionate advocate who guides clients through {workflow} with empathy and clarity"
        elif any(term in vertical_slug for term in ['construction', 'contractor', 'trade']):
            energy = "direct, efficient, confident"
            essence = f"No-nonsense professional who respects your time and delivers accurate {workflow} results"
        elif any(term in vertical_slug for term in ['vet', 'pet', 'animal', 'clinic']):
            energy = "warm, caring, patient"
            essence = f"Caring professional who treats every interaction with compassion during {workflow}"
        elif any(term in vertical_slug for term in ['auto', 'repair', 'mechanic']):
            energy = "helpful, straightforward, knowledgeable"
            essence = f"Trusted expert who explains {workflow} clearly without the runaround"
        else:
            energy = "professional, helpful, attentive"
            essence = f"Dedicated specialist who makes {workflow} simple and stress-free"

        return PersonaConfig(
            name=f"{vertical_name.title()} Assistant",
            essence=essence,
            worldview={
                "core_beliefs": [
                    f"Every client deserves clear, honest communication about {workflow}",
                    "Efficiency and empathy aren't mutually exclusive",
                    "The best service anticipates needs before they're expressed",
                    f"Trust is built through transparency in {workflow}",
                ],
                "aesthetic": f"Clear communication, no jargon, {energy} tone",
                "pet_peeves": "Making clients feel rushed, confused, or unimportant",
                "influences": "Best practices from hospitality, healthcare communication, and customer service excellence"
            },
            expertise={
                "deep_mastery": [
                    f"{workflow} processes and best practices",
                    f"{vertical_name} industry knowledge",
                    "Client communication and expectation management",
                    "Data collection and validation"
                ],
                "working_knowledge": [
                    f"Common {vertical_name.lower()} terminology",
                    "General business processes",
                    "Customer relationship management"
                ],
                "curiosity_edges": [
                    "Emerging industry trends",
                    "New communication technologies",
                    "Process improvement methods"
                ],
                "honest_limits": [
                    "Specific professional advice (requires licensed expert)",
                    "Decisions that require human judgment",
                    "Complex situations requiring escalation"
                ]
            },
            conversational_style={
                "energy": energy,
                "when_exploring": f"Ask clarifying questions to understand the client's {workflow} needs fully",
                "when_sharing_opinions": "Frame as professional perspective with reasoning, not absolutes",
                "when_teaching": "Use plain language with relatable examples, check for understanding",
                "when_building": "Focus on actionable next steps, confirm understanding before proceeding",
                "signature_expressions": [
                    "Validates concerns before moving to solutions",
                    f"Breaks down {workflow} into simple, clear steps",
                    "Offers reassurance with specific next actions"
                ]
            },
            flexibility={
                "reading_intent": {
                    "exploring": "Engage curiously, help them think through options",
                    "seeking_opinion": "Share professional perspective with reasoning",
                    "learning": "Patient explanation with practical examples",
                    "action_request": "Shift to efficient execution mode",
                    "venting": "Acknowledge feelings first, then gently redirect",
                    "urgent": "Prioritize immediately, be decisive",
                    "casual": "Warm and natural, don't force business"
                }
            }
        )

    def _build_custom_onboarding_states(
        self,
        workflow: str,
        discovery: Dict[str, Any]
    ) -> List[OnboardingState]:
        """
        Build custom onboarding states for workflows without pre-built flows.

        Returns a reasonable default flow structure.
        """
        states = [
            OnboardingState(
                name="welcome",
                next="contact_info",
                message="Hi! I'm here to help you get started. Let me collect some information to serve you better.",
                required=False
            ),
            OnboardingState(
                name="contact_info",
                next="situation_type",
                message="First, could you share your contact information?",
                component={
                    "type": "InlineChatForm",
                    "fields": [
                        {"name": "full_name", "type": "text", "label": "Your Name", "required": True},
                        {"name": "email", "type": "email", "label": "Email", "required": True},
                        {"name": "phone", "type": "phone", "label": "Phone", "required": True}
                    ]
                },
                required=True
            ),
            OnboardingState(
                name="situation_type",
                next="details",
                message="What brings you in today?",
                component={
                    "type": "InlineButtons",
                    "name": "situation_type",
                    "options": ["General Inquiry", "New Request", "Follow-up", "Emergency", "Other"]
                },
                required=True,
                field_type="select"
            ),
            OnboardingState(
                name="details",
                next="urgency",
                message="Can you tell me more about your situation?",
                component={
                    "type": "InlineTextarea",
                    "name": "details",
                    "placeholder": "Please describe your situation..."
                },
                required=True,
                field_type="text"
            ),
            OnboardingState(
                name="urgency",
                next="complete",
                message="How urgent is this matter?",
                component={
                    "type": "InlineSlider",
                    "name": "urgency",
                    "min": 1,
                    "max": 10,
                    "labels": {"1": "Not urgent", "10": "Very urgent"}
                },
                required=True,
                field_type="slider"
            ),
            OnboardingState(
                name="complete",
                next="consultation_mode",
                message="Thank you! I have all the information I need. How can I help you further?",
                required=False
            )
        ]

        return states

    def _get_escalation_triggers(
        self,
        vertical_slug: str,
        discovery: Dict[str, Any]
    ) -> List[str]:
        """Get escalation triggers based on vertical type"""

        # Common triggers for all verticals
        common_triggers = [
            "User expresses severe distress or mentions self-harm",
            "Request requires professional licensing or certification",
            "Situation involves legal liability or compliance concerns",
            "User explicitly requests to speak with a human",
            "Complex situation that exceeds agent knowledge boundaries"
        ]

        # Add vertical-specific triggers
        if 'law' in vertical_slug or 'legal' in vertical_slug:
            common_triggers.extend([
                "Statute of limitations may be expiring soon",
                "User mentions existing legal representation",
                "Criminal charges are involved"
            ])
        elif 'vet' in vertical_slug or 'pet' in vertical_slug:
            common_triggers.extend([
                "Symptoms suggest medical emergency",
                "Questions about euthanasia or end-of-life care",
                "Suspected animal abuse situation"
            ])
        elif 'construction' in vertical_slug or 'contractor' in vertical_slug:
            common_triggers.extend([
                "Project requires licenses we don't hold",
                "Unrealistic timeline for scope",
                "Safety or insurance concerns raised"
            ])

        return common_triggers

    async def _define_tools(
        self,
        workflow: str,
        discovery: Dict[str, Any]
    ) -> List[ToolDefinition]:
        """Define MCP-format tools for the agent"""

        # Common tools all agents need
        common_tools = [
            ToolDefinition(
                name="save_intake_data",
                description="Save collected intake data to the database",
                parameters={
                    "type": "object",
                    "properties": {
                        "data": {"type": "object", "description": "Intake data to save"},
                        "stage": {"type": "string", "description": "Current stage of intake"}
                    },
                    "required": ["data", "stage"]
                },
                returns="Confirmation of saved data with record ID"
            ),
            ToolDefinition(
                name="get_user_progress",
                description="Get the user's current progress in the onboarding flow",
                parameters={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User identifier"}
                    },
                    "required": ["user_id"]
                },
                returns="Current stage and completed data"
            ),
            ToolDefinition(
                name="notify_human",
                description="Notify a human team member for review or escalation",
                parameters={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Notification message"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                        "context": {"type": "object", "description": "Relevant context data"}
                    },
                    "required": ["message", "priority"]
                },
                returns="Notification confirmation"
            ),
            ToolDefinition(
                name="schedule_followup",
                description="Schedule a follow-up action or reminder",
                parameters={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "What action to take"},
                        "when": {"type": "string", "description": "When to take action (ISO date or relative)"},
                        "user_id": {"type": "string", "description": "User to follow up with"}
                    },
                    "required": ["action", "when"]
                },
                returns="Scheduled follow-up confirmation"
            )
        ]

        # Workflow-specific tools will be added by Claude during conversation
        # based on the specific workflow requirements

        return common_tools

    async def _create_onboarding_flow(
        self,
        vertical_name: str,
        workflow: str,
        tools: List[ToolDefinition]
    ) -> List[OnboardingStep]:
        """Create onboarding flow for end-user data collection"""

        # Standard 5-step onboarding structure
        steps = [
            OnboardingStep(
                id="welcome",
                title="Welcome",
                description=f"Welcome to {vertical_name} - let's get started",
                fields=[
                    {
                        "type": "display",
                        "content": "[Welcome message explaining what will happen]"
                    },
                    {
                        "type": "button",
                        "label": "Start Onboarding",
                        "action": "next"
                    }
                ]
            ),
            OnboardingStep(
                id="basic_info",
                title="Basic Information",
                description="Tell us about yourself",
                fields=[
                    {"type": "text", "name": "full_name", "label": "Your Name", "required": True},
                    {"type": "email", "name": "email", "label": "Email Address", "required": True},
                    {"type": "phone", "name": "phone", "label": "Phone Number", "required": True}
                ]
            ),
            OnboardingStep(
                id="situation",
                title="Your Situation",
                description="Help us understand your needs",
                fields=[
                    {
                        "type": "inline_select",
                        "name": "situation_type",
                        "label": "[Workflow-specific question]",
                        "options": ["[Option 1]", "[Option 2]", "[Option 3]", "[Other]"],
                        "required": True
                    },
                    {
                        "type": "inline_slider",
                        "name": "urgency",
                        "label": "How urgent is this?",
                        "min": 1,
                        "max": 10,
                        "default": 5
                    },
                    {
                        "type": "textarea",
                        "name": "description",
                        "label": "Tell us more",
                        "placeholder": "Describe your situation in a few sentences..."
                    }
                ]
            ),
            OnboardingStep(
                id="details",
                title="Additional Details",
                description="A few more questions to help us help you",
                fields=[
                    {
                        "type": "inline_buttons",
                        "name": "timeline",
                        "label": "When did this happen?",
                        "options": ["Today", "This week", "This month", "Longer ago"]
                    },
                    {
                        "type": "file_upload",
                        "name": "documents",
                        "label": "Upload any relevant documents (optional)",
                        "accept": [".pdf", ".jpg", ".png", ".doc", ".docx"],
                        "multiple": True,
                        "required": False
                    }
                ]
            ),
            OnboardingStep(
                id="confirmation",
                title="All Set!",
                description="We've got everything we need",
                fields=[
                    {
                        "type": "display",
                        "content": "[Summary of collected information]"
                    },
                    {
                        "type": "display",
                        "content": "[Next steps - what happens now]"
                    },
                    {
                        "type": "button",
                        "label": "Submit",
                        "action": "submit"
                    }
                ]
            )
        ]

        return steps

    async def _save_artifacts(
        self,
        vertical_slug: str,
        vertical_spec: str,
        system_prompt: str,
        tools: List[ToolDefinition],
        onboarding: List[OnboardingStep]
    ) -> None:
        """Save generated artifacts to the factory repo for reference"""
        import json
        import yaml

        artifacts_dir = self.factory_root / "verticals" / vertical_slug
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Save VERTICAL.md
        (artifacts_dir / "VERTICAL.md").write_text(vertical_spec, encoding="utf-8")

        # Save dual-mode system prompt (replaces old persona.xml)
        (artifacts_dir / "system-prompt.xml").write_text(system_prompt, encoding="utf-8")

        # Save tools
        tools_dir = artifacts_dir / "tools"
        tools_dir.mkdir(exist_ok=True)
        tools_data = [t.to_mcp() for t in tools]
        (tools_dir / "tools.json").write_text(json.dumps(tools_data, indent=2), encoding="utf-8")

        # Save onboarding flow
        onboarding_dir = artifacts_dir / "onboarding"
        onboarding_dir.mkdir(exist_ok=True)
        onboarding_data = {"steps": [s.to_dict() for s in onboarding]}
        (onboarding_dir / "flow.yaml").write_text(
            yaml.dump(onboarding_data, default_flow_style=False),
            encoding="utf-8"
        )

    def _format_market_data(self, market_data: Dict[str, Any]) -> str:
        """Format market data for VERTICAL.md"""
        if not market_data:
            return "[To be filled based on discovery research]"

        return f"""
- **SMB Count**: {market_data.get('smb_count', '[Research needed]')}
- **Average Revenue**: {market_data.get('avg_revenue', '[Research needed]')}
- **Tech Adoption**: {market_data.get('tech_adoption', '[Research needed]')}
"""

    def _format_pain_points(self, pain_points: List[str]) -> str:
        """Format pain points as numbered list"""
        if not pain_points:
            return "1. [Pain point 1]\n2. [Pain point 2]\n3. [Pain point 3]"

        return "\n".join(f"{i+1}. {p}" for i, p in enumerate(pain_points))

    def _format_pricing(self, pricing: Dict[str, Any]) -> str:
        """Format pricing recommendation"""
        if not pricing:
            return "**Base Price:** $[X]/year\n\n**Justification:** [ROI calculation]"

        tiers = pricing.get('tiers', [])
        tiers_text = "\n".join(
            f"| {t['name']} | {t['price']} | {', '.join(t.get('features', []))} |"
            for t in tiers
        )

        return f"""
**Base Price:** {pricing.get('base_monthly', '$[X]/month')} ({pricing.get('base_annual', '$[X]/year')})

**Justification:**
{pricing.get('justification', '[ROI calculation]')}

**Pricing Tiers:**

| Tier | Price | Includes |
|------|-------|----------|
{tiers_text}
"""

    def _format_competition(self, solutions: List[Dict[str, str]]) -> str:
        """Format competition analysis"""
        if not solutions:
            return "| Competitor | Price | Gap |\n|------------|-------|-----|\n| [Competitor 1] | $[X] | [Gap] |"

        rows = "\n".join(
            f"| {s.get('name', '[Name]')} | {s.get('price', '[Price]')} | {s.get('gap', '[Gap]')} |"
            for s in solutions
        )

        return f"""| Competitor | Price | Gap |
|------------|-------|-----|
{rows}
"""

    def _get_default_template(self) -> str:
        """Get default VERTICAL.md template if file not found"""
        return """---
vertical: [slug]
status: template
created: [date]
---

# [Industry] Vertical Spec

## Market Overview
[Market data here]

## Target Workflow
[Workflow details here]
"""
