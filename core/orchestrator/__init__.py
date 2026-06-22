"""
Vertical Agent Factory Orchestrator

This package contains the core orchestration logic for building vertical AI agents.
"""

# factory-agent.py uses a hyphen in its filename (historical), so it can't be
# imported with a normal `from .factory_agent import ...`. Try importlib.util
# to load it; if it fails (missing deps), the submodules are still usable.
import importlib.util
from pathlib import Path

try:
    _spec = importlib.util.spec_from_file_location(
        "factory_agent",
        str(Path(__file__).parent / "factory-agent.py"),
    )
    if _spec and _spec.loader:
        _module = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_module)
        VerticalAgentFactory = _module.VerticalAgentFactory
        FactoryConfig = _module.FactoryConfig
        FactoryState = _module.FactoryState
        WorkflowPhase = _module.WorkflowPhase
        FACTORY_SYSTEM_PROMPT = _module.FACTORY_SYSTEM_PROMPT
        FACTORY_TOOLS = _module.FACTORY_TOOLS
    else:
        raise ImportError("Could not load factory-agent.py")
except Exception:
    # factory-agent.py may have dependencies not installed in all environments.
    # The submodules (phases/, etc.) are still importable independently.
    VerticalAgentFactory = None
    FactoryConfig = None
    FactoryState = None
    WorkflowPhase = None
    FACTORY_SYSTEM_PROMPT = None
    FACTORY_TOOLS = None

__all__ = [
    "VerticalAgentFactory",
    "FactoryConfig",
    "FactoryState",
    "WorkflowPhase",
    "FACTORY_SYSTEM_PROMPT",
    "FACTORY_TOOLS"
]
