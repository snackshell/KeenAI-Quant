"""
Ensemble Decision Making for KeenAI-Quant
Combines predictions from the unified KeenAgent
"""

from typing import List, Optional
from datetime import datetime
from backend.models.trading_models import AgentPrediction, OrderDirection, EnsembleDecision


class EnsembleDecisionMaker:
    """
    Makes final trading decisions based on agent predictions
    Simplified for single-agent architecture
    """
    
    def __init__(self, min_confidence: float = 0.6):
        """
        Initialize ensemble decision maker
        
        Args:
            min_confidence: Minimum confidence threshold for trading
        """
        self.min_confidence = min_confidence
    
    def make_decision(self, predictions: List[AgentPrediction]) -> Optional[EnsembleDecision]:
        """
        Make ensemble decision from agent predictions
        
        Args:
            predictions: List of agent predictions
            
        Returns:
            EnsembleDecision or None if no valid decision
        """
        if not predictions:
            return None
        
        # For single agent, use its prediction directly
        if len(predictions) == 1:
            pred = predictions[0]
            if pred.confidence >= self.min_confidence:
                return EnsembleDecision(
                    final_signal=pred.signal,
                    confidence=pred.confidence,
                    predictions=predictions,
                    timestamp=datetime.now()
                )
            return None
        
        # For multiple predictions (future expansion), use voting
        buy_votes = sum(1 for p in predictions if p.signal == OrderDirection.BUY)
        sell_votes = sum(1 for p in predictions if p.signal == OrderDirection.SELL)
        hold_votes = sum(1 for p in predictions if p.signal == OrderDirection.HOLD)
        
        # Calculate weighted confidence
        total_confidence = sum(p.confidence for p in predictions)
        avg_confidence = total_confidence / len(predictions)
        
        # Determine final signal
        if buy_votes > sell_votes and buy_votes > hold_votes:
            final_signal = OrderDirection.BUY
        elif sell_votes > buy_votes and sell_votes > hold_votes:
            final_signal = OrderDirection.SELL
        else:
            final_signal = OrderDirection.HOLD
        
        # Only return decision if confidence is high enough
        if avg_confidence >= self.min_confidence:
            return EnsembleDecision(
                final_signal=final_signal,
                confidence=avg_confidence,
                predictions=predictions,
                timestamp=datetime.now()
            )
        
        return None
