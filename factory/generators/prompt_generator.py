"""
Dual-Mode Prompt Generator
==========================

Assembles complete agent system prompts from:
1. The dual-mode-agent.xml master template
2. Industry-specific persona templates
3. Onboarding state machine patterns
4. Vertical-specific customizations

Output: A complete system prompt ready to deploy with the generated agent.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class OnboardingState:
    """A single state in the onboarding flow"""
    name: str
    next: str
    message: str
    component: dict[str, Any] | None = None
    required: bool = False
    field_type: str = "text"
    options: list[str] | None = None


@dataclass
class PersonaConfig:
    """Configuration for an agent persona"""
    name: str
    essence: str
    worldview: dict[str, Any]
    expertise: dict[str, Any]
    conversational_style: dict[str, Any]
    flexibility: dict[str, Any]


@dataclass
class PromptConfig:
    """Complete configuration for generating a system prompt"""
    vertical_name: str
    vertical_slug: str
    agent_name: str
    company_name: str = "{{COMPANY_NAME}}"  # Runtime variable
    persona: PersonaConfig | None = None
    onboarding_states: list[OnboardingState] = field(default_factory=list)
    tools: list[dict[str, Any]] = field(default_factory=list)
    escalation_triggers: list[str] = field(default_factory=list)
    custom_variables: dict[str, str] = field(default_factory=dict)


class DualModePromptGenerator:
    """
    Generates complete dual-mode system prompts for vertical agents.

    The generator:
    1. Loads the master template (dual-mode-agent.xml)
    2. Loads industry-specific persona configuration
    3. Loads onboarding state patterns
    4. Assembles everything with template variable substitution
    5. Outputs a complete system prompt
    """

    def __init__(self, factory_root: Path | None = None):
        """
        Initialize the generator.

        Args:
            factory_root: Path to the factory root directory.
                         Defaults to the parent of this file's directory.
        """
        if factory_root is None:
            factory_root = Path(__file__).parent.parent.parent
        self.factory_root = factory_root

        self.meta_prompts_dir = factory_root / "core" / "meta-prompts"
        self.personas_dir = self.meta_prompts_dir / "personas"
        self.template_path = self.meta_prompts_dir / "dual-mode-agent.xml"
        self.states_path = self.meta_prompts_dir / "onboarding-states.yaml"

        # Load base resources
        self._load_resources()

    def _load_resources(self):
        """Load the master template and state patterns"""
        # Load master template
        if self.template_path.exists():
            self.master_template = self.template_path.read_text(encoding="utf-8")
        else:
            raise FileNotFoundError(f"Master template not found: {self.template_path}")

        # Load state patterns
        if self.states_path.exists():
            with open(self.states_path, encoding='utf-8') as f:
                self.state_patterns = yaml.safe_load(f)
        else:
            self.state_patterns = {}

    def load_persona(self, vertical_slug: str) -> PersonaConfig | None:
        """
        Load industry-specific persona from YAML file.

        Args:
            vertical_slug: The vertical identifier (e.g., "personal-injury-law")

        Returns:
            PersonaConfig if found, None otherwise
        """
        persona_path = self.personas_dir / f"{vertical_slug}.yaml"

        if not persona_path.exists():
            return None

        with open(persona_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        persona_data = data.get("persona", {})

        return PersonaConfig(
            name=persona_data.get("name", "Assistant"),
            essence=persona_data.get("essence", ""),
            worldview=persona_data.get("worldview", {}),
            expertise=persona_data.get("expertise", {}),
            conversational_style=persona_data.get("conversational_style", {}),
            flexibility=persona_data.get("flexibility", {})
        )

    def build_onboarding_states(
        self,
        flow_name: str,
        custom_options: dict[str, list[str]] | None = None
    ) -> list[OnboardingState]:
        """
        Build onboarding states from a predefined flow pattern.

        Args:
            flow_name: Name of the flow (e.g., "personal_injury_intake")
            custom_options: Override default options for specific fields

        Returns:
            List of OnboardingState objects
        """
        flows = self.state_patterns.get("flows", {})
        base_patterns = self.state_patterns.get("base_patterns", {})
        legal_patterns = self.state_patterns.get("legal_patterns", {})
        service_patterns = self.state_patterns.get("service_patterns", {})
        contractor_patterns = self.state_patterns.get("contractor_patterns", {})

        # Combine all patterns
        all_patterns = {
            **base_patterns,
            **legal_patterns,
            **service_patterns,
            **contractor_patterns
        }

        flow = flows.get(flow_name, {})
        state_names = flow.get("states", [])

        states = []
        for state_name in state_names:
            pattern = all_patterns.get(state_name, {})
            if not pattern:
                continue

            # Apply custom options if provided
            options = pattern.get("options")
            if custom_options and state_name in custom_options:
                options = custom_options[state_name]

            component = pattern.get("component")
            if isinstance(component, dict):
                # Resolve template variables in component options
                if "options" in component and isinstance(component["options"], str):
                    if component["options"].startswith("{{"):
                        var_name = component["options"].strip("{}")
                        if custom_options and var_name in custom_options:
                            component["options"] = custom_options[var_name]

            states.append(OnboardingState(
                name=pattern.get("name", state_name),
                next=pattern.get("next", "complete"),
                message=pattern.get("message", ""),
                component=component,
                required=pattern.get("required", False),
                field_type=pattern.get("field_type", "text"),
                options=options
            ))

        return states

    def _render_onboarding_states_xml(self, states: list[OnboardingState]) -> str:
        """
        Render onboarding states as XML for injection into the template.

        Args:
            states: List of OnboardingState objects

        Returns:
            XML string representing the state machine
        """
        lines = []

        for state in states:
            lines.append(f'      <state name="{state.name}" next="{state.next}">')
            lines.append(f'        <message>{state.message}</message>')

            if state.component:
                lines.append('        <a2ui_component>')
                comp = state.component

                # Handle component as string "none" or as dict
                if isinstance(comp, str):
                    # Simple string value (e.g., "none")
                    lines.append(f'          {comp}')
                else:
                    # Dict-based component
                    comp_type = comp.get("type", "none")

                    if comp_type == "none":
                        lines.append('          none')
                    elif comp_type == "InlineChatForm":
                        lines.append('          <InlineChatForm>')
                        for field_def in comp.get("fields", []):
                            field_attrs = ' '.join([
                                f'{k}="{v}"' for k, v in field_def.items()
                                if k != "options"
                            ])
                            if "options" in field_def:
                                opts = field_def["options"]
                                if isinstance(opts, list):
                                    field_attrs += f" options='{opts}'"
                            lines.append(f'            <field {field_attrs} />')
                        lines.append('          </InlineChatForm>')
                    else:
                        attrs = []
                        for k, v in comp.items():
                            if k == "type":
                                continue
                            if isinstance(v, list):
                                attrs.append(f'{k}=\'{v}\'')
                            elif isinstance(v, dict):
                                attrs.append(f'{k}=\'{v}\'')
                            else:
                                attrs.append(f'{k}="{v}"')
                        attr_str = " ".join(attrs)
                        lines.append(f'          <{comp_type} {attr_str} />')

                lines.append('        </a2ui_component>')
            else:
                lines.append('        <a2ui_component>none</a2ui_component>')

            lines.append(f'        <required>{str(state.required).lower()}</required>')

            if state.name == "complete":
                lines.append('        <action>mark_onboarding_complete</action>')

            lines.append('      </state>')
            lines.append('')

        return '\n'.join(lines)

    def _render_persona_worldview(self, persona: PersonaConfig) -> str:
        """Render persona worldview section"""
        wv = persona.worldview

        lines = [
            '<worldview>',
            '  <core_beliefs>'
        ]

        for belief in wv.get("core_beliefs", []):
            lines.append(f'    <belief>{belief}</belief>')

        lines.append('  </core_beliefs>')
        lines.append(f'  <aesthetic>{wv.get("aesthetic", "")}</aesthetic>')
        lines.append(f'  <pet_peeves>{wv.get("pet_peeves", "")}</pet_peeves>')
        lines.append(f'  <influences>{wv.get("influences", "")}</influences>')
        lines.append('</worldview>')

        return '\n      '.join(lines)

    def _render_persona_expertise(self, persona: PersonaConfig) -> str:
        """Render persona expertise section"""
        exp = persona.expertise

        lines = ['<expertise>']

        for category in ["deep_mastery", "working_knowledge", "curiosity_edges", "honest_limits"]:
            lines.append(f'  <{category}>')
            for item in exp.get(category, []):
                lines.append(f'    <item>{item}</item>')
            lines.append(f'  </{category}>')

        lines.append('</expertise>')

        return '\n      '.join(lines)

    def _render_persona_style(self, persona: PersonaConfig) -> str:
        """Render persona conversational style section"""
        style = persona.conversational_style

        lines = ['<conversational_style>']

        for key in ["energy", "when_exploring", "when_sharing_opinions",
                    "when_teaching", "when_building"]:
            value = style.get(key, "")
            lines.append(f'  <{key}>{value}</{key}>')

        if "signature_expressions" in style:
            lines.append('  <signature_expressions>')
            for expr in style["signature_expressions"]:
                lines.append(f'    <expression>{expr}</expression>')
            lines.append('  </signature_expressions>')

        lines.append('</conversational_style>')

        return '\n      '.join(lines)

    def _render_tools(self, tools: list[dict[str, Any]]) -> str:
        """Render MCP tool definitions"""
        if not tools:
            return "<!-- No tools defined -->"

        lines = []
        for tool in tools:
            lines.append(f'<tool name="{tool.get("name", "")}">')
            lines.append(f'  <description>{tool.get("description", "")}</description>')

            if "input_schema" in tool:
                lines.append('  <input_schema>')
                schema = tool["input_schema"]
                for prop_name, prop_def in schema.get("properties", {}).items():
                    required = prop_name in schema.get("required", [])
                    lines.append(f'    <property name="{prop_name}" '
                               f'type="{prop_def.get("type", "string")}" '
                               f'required="{str(required).lower()}">')
                    lines.append(f'      {prop_def.get("description", "")}')
                    lines.append('    </property>')
                lines.append('  </input_schema>')

            lines.append('</tool>')

        return '\n    '.join(lines)

    def _render_escalation_triggers(self, triggers: list[str]) -> str:
        """Render escalation triggers"""
        lines = ['<vertical_triggers>']
        for trigger in triggers:
            lines.append(f'  <trigger>{trigger}</trigger>')
        lines.append('</vertical_triggers>')

        return '\n      '.join(lines)

    def generate(self, config: PromptConfig) -> str:
        """
        Generate a complete dual-mode system prompt.

        Args:
            config: PromptConfig with all generation parameters

        Returns:
            Complete system prompt string
        """
        prompt = self.master_template

        # Basic substitutions
        prompt = prompt.replace("{{AGENT_NAME}}", config.agent_name)
        prompt = prompt.replace("{{VERTICAL_NAME}}", config.vertical_name)
        prompt = prompt.replace("{{VERTICAL_SLUG}}", config.vertical_slug)
        prompt = prompt.replace("{{COMPANY_NAME}}", config.company_name)

        # Persona substitutions
        if config.persona:
            prompt = prompt.replace(
                "{{ONE_SENTENCE_ESSENCE}}",
                config.persona.essence
            )
            prompt = prompt.replace(
                "{{PERSONA_WORLDVIEW}}",
                self._render_persona_worldview(config.persona)
            )
            prompt = prompt.replace(
                "{{PERSONA_EXPERTISE}}",
                self._render_persona_expertise(config.persona)
            )
            prompt = prompt.replace(
                "{{PERSONA_STYLE}}",
                self._render_persona_style(config.persona)
            )

        # Onboarding states
        if config.onboarding_states:
            prompt = prompt.replace(
                "{{ONBOARDING_STATES}}",
                self._render_onboarding_states_xml(config.onboarding_states)
            )

        # Tools
        prompt = prompt.replace(
            "{{MCP_TOOL_DEFINITIONS}}",
            self._render_tools(config.tools)
        )

        # Escalation triggers
        prompt = prompt.replace(
            "{{ESCALATION_TRIGGERS}}",
            self._render_escalation_triggers(config.escalation_triggers)
        )

        # Custom variables
        for key, value in config.custom_variables.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", value)

        return prompt

    def generate_for_vertical(
        self,
        vertical_slug: str,
        company_name: str = "{{COMPANY_NAME}}",
        tools: list[dict[str, Any]] | None = None,
        custom_options: dict[str, Any] | None = None
    ) -> str:
        """
        High-level method to generate a prompt for a known vertical.

        Args:
            vertical_slug: Vertical identifier (e.g., "personal-injury-law")
            company_name: Client company name (or template var)
            tools: Optional list of tool definitions
            custom_options: Custom options for onboarding fields

        Returns:
            Complete system prompt string
        """
        # Load persona
        persona = self.load_persona(vertical_slug)
        if not persona:
            raise ValueError(f"No persona found for vertical: {vertical_slug}")

        # Map vertical to flow
        flow_mapping = {
            "personal-injury-law": "personal_injury_intake",
            "construction-contractor": "contractor_rfq",
            "veterinary-clinic": "veterinary_appointment",
            "auto-repair-shop": "auto_repair_intake",
        }

        flow_name = flow_mapping.get(vertical_slug, "personal_injury_intake")

        # Load onboarding states
        states = self.build_onboarding_states(flow_name, custom_options)

        # Load escalation triggers from persona file
        persona_path = self.personas_dir / f"{vertical_slug}.yaml"
        escalation_triggers = []
        if persona_path.exists():
            with open(persona_path, encoding='utf-8') as f:
                data = yaml.safe_load(f)
                escalation_triggers = data.get("escalation", {}).get("triggers", [])

        # Build config
        config = PromptConfig(
            vertical_name=vertical_slug.replace("-", " ").title(),
            vertical_slug=vertical_slug,
            agent_name=persona.name,
            company_name=company_name,
            persona=persona,
            onboarding_states=states,
            tools=tools or [],
            escalation_triggers=escalation_triggers
        )

        return self.generate(config)

    # ==================================================================
    # Hermes-native output (Phase 1.7)
    # ==================================================================
    # These methods render the Hermes profile template
    # (hermes-profiles/_template/system-prompt.md) and persona skill
    # (hermes-profiles/_template/skills/persona-template/SKILL.md) using
    # markdown format instead of XML. The dual-mode architecture and
    # persona system are preserved — only the output format changes.

    def _hermes_template_path(self) -> Path:
        return self.factory_root / "hermes-profiles" / "_template" / "system-prompt.md"

    def _hermes_persona_skill_template_path(self) -> Path:
        return (
            self.factory_root
            / "hermes-profiles"
            / "_template"
            / "skills"
            / "persona-template"
            / "SKILL.md"
        )

    def _render_hermes_worldview(self, persona: PersonaConfig) -> str:
        """Render persona worldview as markdown for Hermes output."""
        wv = persona.worldview
        lines: list[str] = ["### Core Beliefs"]
        for belief in wv.get("core_beliefs", []):
            lines.append(f"- {belief}")
        lines.append("")
        lines.append("### What They Find Beautiful")
        lines.append(wv.get("aesthetic", "N/A"))
        lines.append("")
        lines.append("### What Makes Them Cringe")
        lines.append(wv.get("pet_peeves", "N/A"))
        lines.append("")
        lines.append("### Influences")
        lines.append(wv.get("influences", "N/A"))
        return "\n".join(lines)

    def _render_hermes_expertise(self, persona: PersonaConfig) -> str:
        """Render persona expertise as markdown for Hermes output."""
        exp = persona.expertise
        lines: list[str] = ["### Deep Mastery"]
        for item in exp.get("deep_mastery", []):
            lines.append(f"- {item}")
        lines.append("")
        lines.append("### Working Knowledge")
        for item in exp.get("working_knowledge", []):
            lines.append(f"- {item}")
        lines.append("")
        lines.append("### Curiosity Edges")
        for item in exp.get("curiosity_edges", []):
            lines.append(f"- {item}")
        return "\n".join(lines)

    def _render_hermes_style(self, persona: PersonaConfig) -> str:
        """Render conversational style as markdown for Hermes output."""
        style = persona.conversational_style
        lines: list[str] = ["### How They Talk"]
        lines.append(style.get("energy", "N/A"))
        lines.append("")
        lines.append("### Quirks")
        if "signature_expressions" in style:
            for expr in style["signature_expressions"]:
                lines.append(f"- {expr}")
        else:
            lines.append("- (none defined)")
        lines.append("")
        lines.append("### Flexibility")
        lines.append("The agent adapts to user intent:")
        lines.append("- **Brainstorm mode** — generative, exploratory, \"what if\"")
        lines.append("- **Teach mode** — structured explanation, examples, analogies")
        lines.append("- **Build mode** — practical, step-by-step, action-oriented")
        lines.append("- **Troubleshoot mode** — diagnostic, systematic")
        return "\n".join(lines)

    def _render_hermes_onboarding_states(self, states: list[OnboardingState]) -> str:
        """Render onboarding states as markdown for Hermes output."""
        if not states:
            return "(No onboarding states defined)"
        lines: list[str] = []
        for state in states:
            lines.append(f"#### {state.name}")
            lines.append(f"- **Next:** {state.next}")
            lines.append(f"- **Message:** {state.message}")
            if state.required:
                lines.append("- **Required:** yes")
            lines.append("")
        return "\n".join(lines)

    def _render_hermes_tools(self, tools: list[dict[str, Any]]) -> str:
        """Render tool definitions as markdown for Hermes output."""
        if not tools:
            return "(No tools defined)"
        lines: list[str] = []
        for tool in tools:
            lines.append(f"- `{tool.get('name', '')}` — {tool.get('description', '')}")
            if "input_schema" in tool:
                schema = tool["input_schema"]
                props = schema.get("properties", {})
                required = schema.get("required", [])
                for prop_name, prop_def in props.items():
                    req = " (required)" if prop_name in required else ""
                    desc = prop_def.get("description", "")
                    ptype = prop_def.get("type", "string")
                    lines.append(f"  - `{prop_name}` ({ptype}{req}): {desc}")
        return "\n".join(lines)

    def _render_hermes_escalation(self, triggers: list[str]) -> str:
        """Render escalation triggers as markdown for Hermes output."""
        if not triggers:
            return "(No escalation triggers defined)"
        lines: list[str] = []
        for trigger in triggers:
            lines.append(f"- {trigger}")
        return "\n".join(lines)

    def generate_hermes(self, config: PromptConfig) -> str:
        """
        Generate a Hermes-compatible system prompt (markdown format).

        Renders the Hermes profile template
        (hermes-profiles/_template/system-prompt.md) with resolved persona
        values. Preserves the dual-mode architecture. Output is a complete
        system prompt ready for a Hermes agent profile.

        Args:
            config: PromptConfig with all generation parameters.

        Returns:
            Complete Hermes system prompt string (markdown).
        """
        template_path = self._hermes_template_path()
        if not template_path.exists():
            raise FileNotFoundError(f"Hermes template not found: {template_path}")

        prompt = template_path.read_text(encoding="utf-8")

        # Basic substitutions (Hermes template uses lowercase vars)
        prompt = prompt.replace("{{agent_name}}", config.agent_name)
        prompt = prompt.replace("{{vertical_name}}", config.vertical_name)
        prompt = prompt.replace("{{vertical_slug}}", config.vertical_slug)
        # company_name stays as a runtime template variable (per-client)

        # Persona
        if config.persona:
            essence = config.custom_variables.get(
                "one_sentence_essence", config.persona.essence
            )
            prompt = prompt.replace("{{one_sentence_essence}}", essence)
            prompt = prompt.replace(
                "{{persona_worldview_core_beliefs}}",
                self._render_hermes_worldview(config.persona),
            )
            prompt = prompt.replace(
                "{{persona_expertise_deep}}",
                self._render_hermes_expertise(config.persona),
            )
            prompt = prompt.replace(
                "{{persona_style_how_they_talk}}",
                self._render_hermes_style(config.persona),
            )
            # Flatten the persona section placeholders that the template uses
            # as generic markers — replace with rendered sections inline.
            prompt = self._inject_persona_sections(prompt, config.persona)

        # Welcome / completion messages
        welcome = config.custom_variables.get("welcome_message", "")
        prompt = prompt.replace("{{welcome_message}}", welcome)
        completion = config.custom_variables.get("completion_message", "")
        prompt = prompt.replace("{{completion_message}}", completion)

        # Onboarding states
        prompt = prompt.replace(
            "{{onboarding_states}}",
            self._render_hermes_onboarding_states(config.onboarding_states),
        )

        # Tools
        prompt = prompt.replace(
            "{{mcp_tool_definitions}}",
            self._render_hermes_tools(config.tools),
        )

        # Escalation triggers
        prompt = prompt.replace(
            "{{escalation_triggers}}",
            self._render_hermes_escalation(config.escalation_triggers),
        )

        # Case noun
        case_noun = config.custom_variables.get("case_noun", "case")
        prompt = prompt.replace("{{case_noun}}", case_noun)

        return prompt

    def _inject_persona_sections(self, prompt: str, persona: PersonaConfig) -> str:
        """Replace persona section placeholder markers with rendered markdown.

        The template uses three full-block placeholders that each render a
        complete section (including sub-headings):
        - {{persona_worldview_core_beliefs}} → full worldview block
        - {{persona_expertise_deep}}         → full expertise block
        - {{persona_style_how_they_talk}}     → full conversational style block

        Granular placeholders ({{persona_worldview_beautiful}}, etc.) were
        removed from the template to avoid duplicated sub-headings. Any
        leftover granular placeholders are cleaned up for safety.
        """
        replacements = {
            "{{persona_worldview_core_beliefs}}": self._render_hermes_worldview(persona),
            "{{persona_expertise_deep}}": self._render_hermes_expertise(persona),
            "{{persona_style_how_they_talk}}": self._render_hermes_style(persona),
            # Clean up any stale granular placeholders (should not exist in
            # current templates, but prevents partial output if an old template
            # is still in use).
            "{{persona_worldview_beautiful}}": persona.worldview.get("aesthetic", ""),
            "{{persona_worldview_cringe}}": persona.worldview.get("pet_peeves", ""),
            "{{persona_worldview_influences}}": persona.worldview.get("influences", ""),
            "{{persona_expertise_working}}": "\n".join(
                f"- {item}" for item in persona.expertise.get("working_knowledge", [])
            ),
            "{{persona_expertise_curiosity}}": "\n".join(
                f"- {item}" for item in persona.expertise.get("curiosity_edges", [])
            ),
            "{{persona_style_quirks}}": "\n".join(
                f"- {expr}"
                for expr in persona.conversational_style.get(
                    "signature_expressions", []
                )
            ),
            "{{persona_style_flexibility}}": (
                "The agent adapts to user intent: brainstorm, teach, build, troubleshoot."
            ),
        }
        for placeholder, value in replacements.items():
            prompt = prompt.replace(placeholder, value)
        return prompt

    def generate_hermes_persona_skill(self, config: PromptConfig) -> str:
        """
        Generate the persona skill file (SKILL.md) for a Hermes profile.

        Renders the persona skill template
        (hermes-profiles/_template/skills/persona-template/SKILL.md) with
        resolved persona values. This is the crown jewel — the worldview,
        expertise, and conversational style that make the agent a thinking
        partner.

        Args:
            config: PromptConfig with persona and vertical info.

        Returns:
            Complete SKILL.md content string.
        """
        template_path = self._hermes_persona_skill_template_path()
        if not template_path.exists():
            raise FileNotFoundError(
                f"Hermes persona skill template not found: {template_path}"
            )

        skill = template_path.read_text(encoding="utf-8")

        skill = skill.replace("{{vertical_slug}}", config.vertical_slug)
        skill = skill.replace("{{agent_name}}", config.agent_name)
        skill = skill.replace("{{vertical_name}}", config.vertical_name)
        skill = skill.replace("{{company_name}}", config.company_name)

        if config.persona:
            essence = config.custom_variables.get(
                "one_sentence_essence", config.persona.essence
            )
            skill = skill.replace("{{one_sentence_essence}}", essence)
            skill = self._inject_persona_sections(skill, config.persona)

        welcome = config.custom_variables.get("welcome_message", "")
        skill = skill.replace("{{welcome_message}}", welcome)

        return skill


def main():
    """CLI interface for prompt generation"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate dual-mode agent prompts")
    parser.add_argument("vertical", help="Vertical slug (e.g., personal-injury-law)")
    parser.add_argument("--company", default="{{COMPANY_NAME}}", help="Company name")
    parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    generator = DualModePromptGenerator()

    try:
        prompt = generator.generate_for_vertical(
            args.vertical,
            company_name=args.company
        )

        if args.output:
            Path(args.output).write_text(prompt, encoding="utf-8")
            print(f"Prompt written to: {args.output}")
        else:
            print(prompt)

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
