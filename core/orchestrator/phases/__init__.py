"""
Factory Workflow Phases

Each phase is responsible for a specific part of the agent building workflow:
- Discovery: Research vertical, identify workflows
- Specification: Generate VERTICAL.md, persona, tools
- Scaffold: Build complete Next.js app
- Delivery: Generate dashboards and landing pages
"""

from .discovery import DiscoveryPhase
from .specification import SpecificationPhase
from .scaffold import ScaffoldPhase
from .delivery import DeliveryPhase

__all__ = [
    "DiscoveryPhase",
    "SpecificationPhase",
    "ScaffoldPhase",
    "DeliveryPhase"
]
