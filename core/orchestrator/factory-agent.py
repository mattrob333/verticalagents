"""
Vertical Agent Factory - Master Orchestrator

This is the main entry point for the factory system. It orchestrates the 4-phase
workflow for building vertical AI agents:

1. DISCOVERY - Research vertical, identify workflows, get user approval
2. SPECIFICATION - Generate VERTICAL.md, persona, tools, onboarding flows
3. BUILD - Scaffold complete Next.js app with A2UI components
4. DELIVERY - Generate admin dashboard and client landing page

Usage:
    # Via Claude Code conversation
    "Build an agent for personal injury law"

    # Via slash command
    /build-agent personal injury law

    # Via CLI
    python core/orchestrator/factory-agent.py --vertical "personal injury law"
"""

import os
import yaml
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, Generator
from dataclasses import dataclass
from enum import Enum

# Phase imports
from phases.discovery import DiscoveryPhase
from phases.specification import SpecificationPhase
from phases.scaffold import ScaffoldPhase
from phases.delivery import DeliveryPhase


class WorkflowPhase(Enum):
    """Factory workflow phases"""
    DISCOVERY = "discovery"
    SPECIFICATION = "specification"
    BUILD = "build"
    DELIVERY = "delivery"
    COMPLETE = "complete"


@dataclass
class FactoryConfig:
    """Factory configuration loaded from factory.config.yaml"""
    output_dir: str
    persona_engine: str
    agent_model: str
    search_provider: str
    require_approval: bool
    save_artifacts: bool
    artifacts_dir: str

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "FactoryConfig":
        """Load configuration from YAML file"""
        if config_path is None:
            # Default to factory/config/factory.config.yaml
            factory_root = Path(__file__).parent.parent.parent
            config_path = factory_root / "factory" / "config" / "factory.config.yaml"

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        return cls(
            output_dir=os.path.expanduser(config['output']['default_dir']),
            persona_engine=config['generation']['persona_engine'],
            agent_model=config['generation']['agent_model'],
            search_provider=config['discovery']['search_provider'],
            require_approval=config['workflow']['require_approval'],
            save_artifacts=config['workflow']['save_artifacts'],
            artifacts_dir=config['workflow']['artifacts_dir']
        )


@dataclass
class FactoryState:
    """Current state of the factory workflow"""
    vertical_name: str
    vertical_slug: str
    current_phase: WorkflowPhase
    discovery_report: Optional[Dict[str, Any]] = None
    selected_workflow: Optional[str] = None
    specification: Optional[Dict[str, Any]] = None
    output_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vertical_name": self.vertical_name,
            "vertical_slug": self.vertical_slug,
            "current_phase": self.current_phase.value,
            "discovery_report": self.discovery_report,
            "selected_workflow": self.selected_workflow,
            "output_path": self.output_path
        }


class VerticalAgentFactory:
    """
    Main factory orchestrator for building vertical AI agents.

    This class coordinates the 4-phase workflow and maintains state
    between phases for approval gates.
    """

    def __init__(self, config: Optional[FactoryConfig] = None):
        self.config = config or FactoryConfig.load()
        self.state: Optional[FactoryState] = None

        # Initialize phase handlers
        self.phases = {
            WorkflowPhase.DISCOVERY: DiscoveryPhase(self.config),
            WorkflowPhase.SPECIFICATION: SpecificationPhase(self.config),
            WorkflowPhase.BUILD: ScaffoldPhase(self.config),
            WorkflowPhase.DELIVERY: DeliveryPhase(self.config)
        }

    def slugify(self, name: str) -> str:
        """Convert vertical name to URL-friendly slug"""
        import re
        slug = name.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug

    def start(self, vertical_name: str, output_dir: Optional[str] = None) -> FactoryState:
        """
        Start the factory workflow for a new vertical.

        Args:
            vertical_name: Human-readable name of the vertical (e.g., "personal injury law")
            output_dir: Override output directory (optional)

        Returns:
            Initial factory state
        """
        self.state = FactoryState(
            vertical_name=vertical_name,
            vertical_slug=self.slugify(vertical_name),
            current_phase=WorkflowPhase.DISCOVERY,
            output_path=output_dir or os.path.join(
                self.config.output_dir,
                self.slugify(vertical_name)
            )
        )
        return self.state

    async def run_discovery(self) -> Dict[str, Any]:
        """
        Run the discovery phase.

        Returns:
            Discovery report with workflow options for user approval
        """
        if self.state is None:
            raise ValueError("Factory not started. Call start() first.")

        phase = self.phases[WorkflowPhase.DISCOVERY]
        report = await phase.execute(
            vertical_name=self.state.vertical_name,
            vertical_slug=self.state.vertical_slug
        )

        self.state.discovery_report = report
        return report

    def approve_discovery(self, selected_workflow: str) -> bool:
        """
        User approves discovery and selects a workflow.

        Args:
            selected_workflow: Name of the workflow to build

        Returns:
            True if approval successful
        """
        if self.state is None or self.state.discovery_report is None:
            raise ValueError("No discovery report to approve")

        self.state.selected_workflow = selected_workflow
        self.state.current_phase = WorkflowPhase.SPECIFICATION
        return True

    async def run_specification(self) -> Dict[str, Any]:
        """
        Run the specification phase.

        Returns:
            Generated specification artifacts
        """
        if self.state is None or self.state.selected_workflow is None:
            raise ValueError("Workflow not selected. Approve discovery first.")

        phase = self.phases[WorkflowPhase.SPECIFICATION]
        spec = await phase.execute(
            vertical_name=self.state.vertical_name,
            vertical_slug=self.state.vertical_slug,
            workflow=self.state.selected_workflow,
            discovery_report=self.state.discovery_report
        )

        self.state.specification = spec
        return spec

    def approve_specification(self) -> bool:
        """
        User approves specification to proceed to build.

        Returns:
            True if approval successful
        """
        if self.state is None or self.state.specification is None:
            raise ValueError("No specification to approve")

        self.state.current_phase = WorkflowPhase.BUILD
        return True

    async def run_build(self) -> str:
        """
        Run the build phase - scaffold the complete app.

        Returns:
            Path to the generated app
        """
        if self.state is None or self.state.specification is None:
            raise ValueError("Specification not approved. Approve specification first.")

        phase = self.phases[WorkflowPhase.BUILD]
        output_path = await phase.execute(
            vertical_name=self.state.vertical_name,
            vertical_slug=self.state.vertical_slug,
            specification=self.state.specification,
            output_path=self.state.output_path
        )

        self.state.current_phase = WorkflowPhase.DELIVERY
        return output_path

    async def run_delivery(self) -> Dict[str, Any]:
        """
        Run the delivery phase - generate dashboards and landing pages.

        Returns:
            Delivery summary with paths to generated files
        """
        if self.state is None:
            raise ValueError("Build not complete")

        phase = self.phases[WorkflowPhase.DELIVERY]
        result = await phase.execute(
            vertical_name=self.state.vertical_name,
            vertical_slug=self.state.vertical_slug,
            specification=self.state.specification,
            output_path=self.state.output_path
        )

        self.state.current_phase = WorkflowPhase.COMPLETE
        return result

    async def run_full_workflow(
        self,
        vertical_name: str,
        output_dir: Optional[str] = None,
        auto_approve: bool = False
    ) -> Generator[Dict[str, Any], str, Dict[str, Any]]:
        """
        Run the complete factory workflow with approval gates.

        This is a generator that yields results at each phase and
        expects approval input via send() before proceeding.

        Args:
            vertical_name: Name of the vertical to build
            output_dir: Override output directory
            auto_approve: Skip approval gates (for testing)

        Yields:
            Phase results requiring approval

        Returns:
            Final delivery summary
        """
        # Initialize
        self.start(vertical_name, output_dir)

        # Phase 1: Discovery
        discovery_report = await self.run_discovery()
        if not auto_approve:
            selected = yield {
                "phase": "discovery",
                "status": "awaiting_approval",
                "report": discovery_report
            }
            self.approve_discovery(selected)
        else:
            # Auto-select first recommended workflow
            workflows = discovery_report.get("workflow_options", [])
            recommended = next((w for w in workflows if w.get("recommended")), workflows[0])
            self.approve_discovery(recommended["name"])

        # Phase 2: Specification
        specification = await self.run_specification()
        if not auto_approve:
            yield {
                "phase": "specification",
                "status": "awaiting_approval",
                "specification": specification
            }
            self.approve_specification()
        else:
            self.approve_specification()

        # Phase 3: Build
        output_path = await self.run_build()
        yield {
            "phase": "build",
            "status": "complete",
            "output_path": output_path
        }

        # Phase 4: Delivery
        delivery = await self.run_delivery()

        return {
            "phase": "delivery",
            "status": "complete",
            "vertical": self.state.vertical_name,
            "output_path": self.state.output_path,
            "summary": delivery
        }


# Claude Agent SDK tool definitions
FACTORY_TOOLS = """
## Factory Tools

The following tools are available for the factory workflow:

### research_vertical
Research a vertical market for AI agent opportunities.
- Input: vertical_name (str), focus_workflow (str, optional)
- Output: Discovery report with workflow options

### generate_specification
Generate complete VERTICAL.md specification from discovery.
- Input: vertical_slug (str), workflow (str), discovery_report (dict)
- Output: Specification artifacts (VERTICAL.md, persona, tools, flows)

### scaffold_app
Scaffold complete Next.js app from specification.
- Input: vertical_slug (str), specification (dict), output_path (str)
- Output: Path to generated app

### generate_dashboards
Generate admin dashboard and client landing page.
- Input: vertical_slug (str), specification (dict), output_path (str)
- Output: Delivery summary
"""


FACTORY_SYSTEM_PROMPT = """
You are the Vertical Agent Factory orchestrator. Your job is to guide users through
building complete AI agents for SMB verticals.

## Your Capabilities

You can build vertical AI agents that include:
- Admin Dashboard (NotebookLM-style 3-panel interface)
- Client-Facing Landing Page with "Start Onboarding" CTA
- Inline Chat with A2UI form components (buttons, dropdowns, sliders)
- Complete backend with Claude Agent SDK integration

## Workflow Phases

1. **DISCOVERY**: Research the vertical, identify 2-3 workflow options, present for approval
2. **SPECIFICATION**: Generate VERTICAL.md, persona (via Prometheus), tools, onboarding flows
3. **BUILD**: Scaffold complete Next.js app to OUTPUT_DIR
4. **DELIVERY**: Generate dashboards, wire up complete flow

## Key Principles

- Factory repo stays CLEAN - all output goes to ~/VerticalAgents/[slug]/
- Each phase requires explicit user approval before proceeding
- Generated agents include inline A2UI form components in chat
- Two-tier dashboard: Admin (for client) + Client-facing (for end-users)

## Trigger Phrases

- "build an agent for [vertical]" -> Start full workflow
- "research [vertical]" -> Discovery phase only
- "what verticals can you build?" -> List playbook examples

## Phase Approval

After each phase, present results and ask:
- Discovery: "Which workflow would you like to build?"
- Specification: "Does this specification look correct? Ready to build?"

Never proceed to the next phase without explicit approval.
"""


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Vertical Agent Factory - Build AI agents for SMB verticals"
    )
    parser.add_argument(
        "--vertical", "-v",
        type=str,
        required=True,
        help="Name of the vertical (e.g., 'personal injury law')"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        help="Override output directory"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Skip approval gates (for testing)"
    )
    parser.add_argument(
        "--phase",
        type=str,
        choices=["discovery", "specification", "build", "delivery", "all"],
        default="all",
        help="Run specific phase or all phases"
    )

    args = parser.parse_args()

    # Create factory and run
    factory = VerticalAgentFactory()

    print(f"\n🏭 Vertical Agent Factory")
    print(f"Building agent for: {args.vertical}")
    print(f"Output directory: {args.output_dir or factory.config.output_dir}")
    print("-" * 50)

    # TODO: Implement async CLI runner
    print("\n⚠️  CLI execution not yet implemented.")
    print("Use Claude Code conversation or /build-agent command instead.")


if __name__ == "__main__":
    main()
