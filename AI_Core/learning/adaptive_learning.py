"""
Adaptive Learning System for KeenAI-Quant
Learns from trading performance and adapts strategies
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque


class AdaptiveLearner:
    """
    Learns from trading outcomes and adapts decision-making
    Tracks performance patterns and adjusts confidence thresholds
    """
    
    def __init__(self, learning_rate: float = 0.1, memory_size: int = 1000):
        """
        Initialize adaptive learner
        
        Args:
            learning_rate: How quickly to adapt (0-1)
            memory_size: Number of trades to remember
        """
        self.learning_rate = learning_rate
        self.memory = deque(maxlen=memory_size)
        self.performance_by_pair: Dict[str, List[float]] = {}
        self.performance_by_signal: Dict[str, List[float]] = {}
        self.confidence_adjustments: Dict[str, float] = {}
    
    def record_trade_outcome(
        self,
        pair: str,
        signal: str,
        predicted_confidence: float,
        actual_pnl: float,
        duration_hours: float
    ):
        """
        Record a trade outcome for learning
        
        Args:
            pair: Trading pair
            signal: BUY or SELL
            predicted_confidence: AI's confidence level
            actual_pnl: Actual profit/loss percentage
            duration_hours: How long trade was open
        """
        outcome = {
            'pair': pair,
            'signal': signal,
            'confidence': predicted_confidence,
            'pnl': actual_pnl,
            'duration': duration_hours,
            'timestamp': datetime.now()
        }
        
        self.memory.append(outcome)
        
        # Update performance tracking
        if pair not in self.performance_by_pair:
            self.performance_by_pair[pair] = []
        self.performance_by_pair[pair].append(actual_pnl)
        
        if signal not in self.performance_by_signal:
            self.performance_by_signal[signal] = []
        self.performance_by_signal[signal].append(actual_pnl)
        
        # Adapt confidence thresholds
        self._adapt_confidence(pair, signal, predicted_confidence, actual_pnl)
    
    def _adapt_confidence(self, pair: str, signal: str, confidence: float, pnl: float):
        """Adapt confidence thresholds based on outcomes"""
        key = f"{pair}_{signal}"
        
        # If trade was profitable, slightly lower threshold
        # If trade was loss, slightly raise threshold
        adjustment = -self.learning_rate if pnl > 0 else self.learning_rate
        
        if key not in self.confidence_adjustments:
            self.confidence_adjustments[key] = 0.0
        
        self.confidence_adjustments[key] += adjustment
        
        # Clamp adjustments to reasonable range
        self.confidence_adjustments[key] = max(-0.2, min(0.2, self.confidence_adjustments[key]))
    
    def get_adjusted_confidence(self, pair: str, signal: str, base_confidence: float) -> float:
        """
        Get confidence adjusted by learning
        
        Args:
            pair: Trading pair
            signal: BUY or SELL
            base_confidence: Original confidence from AI
            
        Returns:
            Adjusted confidence level
        """
        key = f"{pair}_{signal}"
        adjustment = self.confidence_adjustments.get(key, 0.0)
        
        adjusted = base_confidence + adjustment
        return max(0.0, min(1.0, adjusted))
    
    def get_pair_performance(self, pair: str, days: int = 30) -> Dict[str, float]:
        """
        Get performance statistics for a trading pair
        
        Args:
            pair: Trading pair
            days: Number of days to analyze
            
        Returns:
            Performance statistics
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_trades = [
            t for t in self.memory
            if t['pair'] == pair and t['timestamp'] > cutoff
        ]
        
        if not recent_trades:
            return {'win_rate': 0.0, 'avg_pnl': 0.0, 'trade_count': 0}
        
        wins = sum(1 for t in recent_trades if t['pnl'] > 0)
        total_pnl = sum(t['pnl'] for t in recent_trades)
        
        return {
            'win_rate': wins / len(recent_trades),
            'avg_pnl': total_pnl / len(recent_trades),
            'trade_count': len(recent_trades)
        }
    
    def get_learning_stats(self) -> Dict:
        """Get overall learning statistics"""
        return {
            'total_trades': len(self.memory),
            'pairs_tracked': len(self.performance_by_pair),
            'confidence_adjustments': self.confidence_adjustments.copy(),
            'learning_rate': self.learning_rate
        }


# Global adaptive learner instance
adaptive_learner = AdaptiveLearner()
