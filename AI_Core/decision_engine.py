"""
Decision Engine for KeenAI-Quant
Coordinates AI analysis and trading decisions
"""

from typing import Optional
from datetime import datetime

from backend.models.trading_models import MarketContext, TradingSignal, OrderDirection
from AI_Core.agents.agent_orchestrator import agent_orchestrator
from AI_Core.models.ensemble_decision import EnsembleDecisionMaker


class DecisionEngine:
    """
    Main decision engine that coordinates:
    - AI agent analysis
    - Ensemble decision making
    - Signal generation
    """
    
    def __init__(self, min_confidence: float = 0.6):
        """
        Initialize decision engine
        
        Args:
            min_confidence: Minimum confidence threshold for trading
        """
        self.ensemble = EnsembleDecisionMaker(min_confidence=min_confidence)
        self.min_confidence = min_confidence
    
    async def analyze_and_decide(self, context: MarketContext) -> Optional[TradingSignal]:
        """
        Analyze market and generate trading signal
        
        Args:
            context: MarketContext with all market data
            
        Returns:
            TradingSignal or None if no valid signal
        """
        # Get AI prediction
        prediction = await agent_orchestrator.analyze_market(context)
        
        if not prediction:
            return None
        
        # Make ensemble decision (currently single agent)
        decision = self.ensemble.make_decision([prediction])
        
        if not decision:
            return None
        
        # Generate trading signal
        if decision.final_signal == OrderDirection.HOLD:
            return None
        
        signal = TradingSignal(
            pair=context.pair,
            direction=decision.final_signal,
            confidence=decision.confidence,
            entry_price=context.current_price,
            timestamp=datetime.now(),
            reasoning=prediction.reasoning,
            indicators=context.indicators
        )
        
        return signal
    
    def get_stats(self):
        """Get decision engine statistics"""
        return {
            'agent_stats': agent_orchestrator.get_agent_stats(),
            'min_confidence': self.min_confidence
        }


# Global decision engine instance
decision_engine = DecisionEngine()
