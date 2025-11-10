"""
AI Core Module for KeenAI-Quant
Unified AI system using OpenRouter for trading decisions
"""

from .agents import (
    agent_orchestrator,
    AgentOrchestrator,
    performance_tracker,
    AgentPerformanceTracker,
    BaseAgent,
    KeenAgent,
    create_keen_agent
)

from .decision_engine import decision_engine, DecisionEngine
from .models.ensemble_decision import EnsembleDecisionMaker
from .models.model_registry import model_registry, ModelRegistry

__all__ = [
    # Agents
    'agent_orchestrator',
    'AgentOrchestrator',
    'performance_tracker',
    'AgentPerformanceTracker',
    'BaseAgent',
    'KeenAgent',
    'create_keen_agent',
    # Decision Engine
    'decision_engine',
    'DecisionEngine',
    # Models
    'EnsembleDecisionMaker',
    'model_registry',
    'ModelRegistry'
]
