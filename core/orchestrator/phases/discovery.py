"""
Discovery Phase - Research vertical markets and identify automation opportunities.

This phase:
1. Searches the web for industry data, pain points, and existing solutions
2. Cross-references with existing playbook examples
3. Identifies 2-3 workflow options ranked by automation potential
4. Presents findings for user approval
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class WorkflowOption:
    """A potential workflow to automate"""
    name: str
    description: str
    automation_potential: float  # 0-100
    time_savings: str  # e.g., "15 hrs/week"
    integration_requirements: List[str]
    recommended: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "automation_potential": f"{self.automation_potential}%",
            "time_savings": self.time_savings,
            "integration_requirements": self.integration_requirements,
            "recommended": self.recommended
        }


@dataclass
class MarketData:
    """Market research data for a vertical"""
    smb_count: str
    avg_revenue: str
    tech_adoption: str  # Low, Medium, High
    key_pain_points: List[str]
    existing_solutions: List[Dict[str, str]]
    pricing_benchmark: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "smb_count": self.smb_count,
            "avg_revenue": self.avg_revenue,
            "tech_adoption": self.tech_adoption,
            "key_pain_points": self.key_pain_points,
            "existing_solutions": self.existing_solutions,
            "pricing_benchmark": self.pricing_benchmark
        }


class DiscoveryPhase:
    """
    Discovery Phase Handler

    Researches a vertical market to identify the best automation opportunities.
    Uses web search and existing playbook examples to generate a discovery report.
    """

    def __init__(self, config):
        self.config = config
        self.factory_root = Path(__file__).parent.parent.parent.parent

    async def execute(
        self,
        vertical_name: str,
        vertical_slug: str
    ) -> Dict[str, Any]:
        """
        Execute the discovery phase.

        Args:
            vertical_name: Human-readable vertical name
            vertical_slug: URL-friendly slug

        Returns:
            Discovery report with workflow options
        """
        # Step 1: Check existing playbooks
        playbook_data = self._check_existing_playbooks(vertical_slug)

        # Step 2: Research market (web search)
        market_data = await self._research_market(vertical_name)

        # Step 3: Identify workflow options
        workflow_options = await self._identify_workflows(
            vertical_name,
            market_data,
            playbook_data
        )

        # Step 4: Generate pricing recommendation
        pricing = self._calculate_pricing(workflow_options, market_data)

        # Compile discovery report
        report = {
            "vertical": vertical_name,
            "vertical_slug": vertical_slug,
            "research_date": self._get_date(),
            "confidence": self._calculate_confidence(playbook_data, market_data),
            "market_data": market_data.to_dict() if market_data else None,
            "workflow_options": [w.to_dict() for w in workflow_options],
            "pricing_recommendation": pricing,
            "playbook_reference": playbook_data.get("reference") if playbook_data else None
        }

        return report

    def _check_existing_playbooks(self, vertical_slug: str) -> Optional[Dict[str, Any]]:
        """Check if we have an existing playbook for this vertical"""
        # Check verticals directory
        verticals_dir = self.factory_root / "verticals"
        vertical_path = verticals_dir / vertical_slug / "VERTICAL.md"

        if vertical_path.exists():
            return {
                "exists": True,
                "reference": str(vertical_path),
                "type": "vertical_spec"
            }

        # Check knowledge base
        knowledge_dir = self.factory_root / "knowledge" / "industry-playbooks"
        if knowledge_dir.exists():
            for playbook in knowledge_dir.glob("*.md"):
                if vertical_slug in playbook.stem.lower():
                    return {
                        "exists": True,
                        "reference": str(playbook),
                        "type": "playbook"
                    }

        return None

    async def _research_market(self, vertical_name: str) -> MarketData:
        """
        Research market data for the vertical.

        In production, this would use web search (Firecrawl/Exa).
        For now, returns structured placeholder that will be filled by Claude.
        """
        # This is a template that Claude will populate during conversation
        # The actual research happens in the Claude Code session

        return MarketData(
            smb_count="[Research: Number of SMBs in this vertical in US]",
            avg_revenue="[Research: Average revenue range]",
            tech_adoption="[Research: Low/Medium/High tech adoption]",
            key_pain_points=[
                "[Research: Pain point 1]",
                "[Research: Pain point 2]",
                "[Research: Pain point 3]"
            ],
            existing_solutions=[
                {"name": "[Competitor 1]", "price": "[Price]", "gap": "[Gap]"},
                {"name": "[Competitor 2]", "price": "[Price]", "gap": "[Gap]"}
            ],
            pricing_benchmark="[Research: What they currently pay for similar solutions]"
        )

    async def _identify_workflows(
        self,
        vertical_name: str,
        market_data: MarketData,
        playbook_data: Optional[Dict[str, Any]]
    ) -> List[WorkflowOption]:
        """
        Identify potential workflows to automate.

        Returns 2-3 options ranked by automation potential.
        """
        # Template workflow options that Claude will populate
        workflows = [
            WorkflowOption(
                name="[Primary Workflow - Most Common Pain Point]",
                description="[Description of what this workflow does]",
                automation_potential=0.0,
                time_savings="[X] hrs/week",
                integration_requirements=["[Integration 1]", "[Integration 2]"],
                recommended=True
            ),
            WorkflowOption(
                name="[Secondary Workflow - High Value]",
                description="[Description of what this workflow does]",
                automation_potential=0.0,
                time_savings="[X] hrs/week",
                integration_requirements=["[Integration 1]"]
            ),
            WorkflowOption(
                name="[Tertiary Workflow - Nice to Have]",
                description="[Description of what this workflow does]",
                automation_potential=0.0,
                time_savings="[X] hrs/week",
                integration_requirements=["[Integration 1]"]
            )
        ]

        return workflows

    def _calculate_pricing(
        self,
        workflows: List[WorkflowOption],
        market_data: MarketData
    ) -> Dict[str, Any]:
        """Calculate pricing recommendation based on value delivered"""
        return {
            "base_monthly": "[Calculate: Based on time saved x hourly rate]",
            "base_annual": "[Calculate: Monthly x 12 with discount]",
            "justification": "[Explain ROI: X hrs/week x $Y/hr = $Z/month value]",
            "tiers": [
                {"name": "Starter", "price": "$[X]/month", "features": ["Core automation"]},
                {"name": "Pro", "price": "$[X]/month", "features": ["+ Integrations", "+ Priority support"]},
                {"name": "Enterprise", "price": "Custom", "features": ["+ Multi-location", "+ API access"]}
            ]
        }

    def _calculate_confidence(
        self,
        playbook_data: Optional[Dict[str, Any]],
        market_data: MarketData
    ) -> str:
        """Calculate confidence level for this vertical"""
        if playbook_data and playbook_data.get("exists"):
            return "high"
        elif market_data:
            return "medium"
        else:
            return "low"

    def _get_date(self) -> str:
        """Get current date in ISO format"""
        from datetime import date
        return date.today().isoformat()


# Discovery prompts for Claude to use during research
DISCOVERY_PROMPTS = {
    "market_size": """
Research the {vertical} industry:
- How many SMBs operate in this vertical in the US?
- What's the typical revenue range?
- What's the average team size?
- What's the tech adoption level (Low/Medium/High)?
""",

    "pain_points": """
Research pain points for {vertical}:
- What are the top 3-5 administrative pain points?
- How many hours per week are spent on each?
- What's the cost when things go wrong?
- What do owners complain about on forums/Reddit?
""",

    "competition": """
Research existing solutions for {vertical}:
- What software do they currently use?
- What are the top 3 competitors?
- What do they charge?
- What are the main complaints in reviews?
- What gaps exist in current solutions?
""",

    "workflow_analysis": """
For the {workflow} workflow in {vertical}:
- What triggers this workflow?
- Who handles it currently?
- What steps are involved?
- What tools are used?
- What's the automation potential (0-100%)?
- What integrations would be needed?
"""
}
