"""
Agent Orchestrator for KeenAI-Quant
Manages the unified KeenAgent with OpenRouter
"""

import asyncio
import os
from typing import Dict, Optional
from datetime import datetime

from backend.models.trading_models import (
    MarketContext, AgentPrediction, OrderDirection
)
from backend.config import config
from .keen_agent import KeenAgent


class AgentOrchestrator:
    """
    Orchestrates the unified KeenAgent
    Simplified single-agent architecture with easy model switching
    """
    
    def __init__(self):
        """Initialize orchestrator with KeenAgent"""
        self.agent: Optional[KeenAgent] = None
        self.initialize_agent()
    
    def initialize_agent(self):
        """Initialize the unified KeenAgent"""
        # Get OpenRouter API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            print("⚠️ No OPENROUTER_API_KEY found in environment")
            print("💡 Set OPENROUTER_API_KEY in your .env file")
            return
        
        # Get model from config or use default
        model = config.get('ai.model', 'deepseek/deepseek-v3.2-exp')
        timeout = config.get('ai.timeout', 5)
        
        try:
            self.agent = KeenAgent(
                api_key=api_key,
                model=model,
                timeout=timeout
            )
            print(f"🤖 KeenAgent ready with model: {model}")
            
        except Exception as e:
            print(f"❌ Failed to initialize KeenAgent: {e}")
    
    async def analyze_market(self, context: MarketContext) -> Optional[AgentPrediction]:
        """
        Analyze market and return prediction from KeenAgent
        This is the main entry point for getting AI trading signals
        
        Args:
            context: MarketContext with all market data
            
        Returns:
            AgentPrediction with trading signal, or None if agent unavailable
        """
        if not self.agent:
            print("⚠️ KeenAgent not available")
            return None
        
        try:
            # Get prediction from unified agent
            prediction = await self.agent.analyze(context)
            
            # Log decision
            if prediction:
                self._log_decision(context, prediction)
            
            return prediction
            
        except Exception as e:
            print(f"❌ Error analyzing market: {e}")
            return None
    
    def _log_decision(self, context: MarketContext, prediction: AgentPrediction):
        """Log agent decision for debugging"""
        print(f"\n🤖 KeenAgent Decision for {context.pair}:")
        print(f"   Signal: {prediction.signal.value}")
        print(f"   Confidence: {prediction.confidence:.2%}")
        if prediction.reasoning:
            print(f"   Reasoning: {prediction.reasoning[:100]}...")
    
    def get_agent_stats(self) -> Dict[str, Dict]:
        """Get statistics for the agent"""
        if not self.agent:
            return {}
        
        return {
            'keen_agent': self.agent.get_stats()
        }
    
    def switch_model(self, model: str) -> bool:
        """
        Switch to a different model
        
        Args:
            model: Model identifier (e.g., 'deepseek/deepseek-v3.2-exp', 'anthropic/claude-3.5-sonnet')
            
        Returns:
            True if successful, False otherwise
        """
        if not self.agent:
            print("⚠️ No agent to switch model for")
            return False
        
        try:
            old_model = self.agent.model
            self.agent.model = model
            print(f"🔄 Switched model: {old_model} → {model}")
            return True
        except Exception as e:
            print(f"❌ Failed to switch model: {e}")
            return False


# Global instance
agent_orchestrator = AgentOrchestrator()
