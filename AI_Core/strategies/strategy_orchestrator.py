"""
Strategy Orchestrator for KeenAI-Quant
Manages multiple trading strategies and combines their signals
"""

from typing import List, Optional, Dict
from datetime import datetime

from backend.models.trading_models import MarketContext, TradingSignal, OrderDirection
from .base_strategy import BaseStrategy


class StrategyOrchestrator:
    """
    Orchestrates multiple trading strategies
    Combines signals and manages strategy lifecycle
    """
    
    def __init__(self):
        """Initialize strategy orchestrator"""
        self.strategies: List[BaseStrategy] = []
        self.strategy_weights: Dict[str, float] = {}
    
    def register_strategy(self, strategy: BaseStrategy, weight: float = 1.0):
        """
        Register a trading strategy
        
        Args:
            strategy: Strategy instance
            weight: Strategy weight for signal combination
        """
        self.strategies.append(strategy)
        self.strategy_weights[strategy.name] = weight
        print(f"✅ Registered strategy: {strategy.name} (weight: {weight})")
    
    def unregister_strategy(self, strategy_name: str):
        """
        Unregister a strategy
        
        Args:
            strategy_name: Name of strategy to remove
        """
        self.strategies = [s for s in self.strategies if s.name != strategy_name]
        if strategy_name in self.strategy_weights:
            del self.strategy_weights[strategy_name]
    
    async def analyze_all(self, context: MarketContext) -> List[TradingSignal]:
        """
        Run all enabled strategies
        
        Args:
            context: Market context
            
        Returns:
            List of signals from all strategies
        """
        signals = []
        
        for strategy in self.strategies:
            if not strategy.enabled:
                continue
            
            try:
                signal = await strategy.analyze(context)
                if signal:
                    signals.append(signal)
                    strategy.record_signal(signal)
            except Exception as e:
                print(f"❌ Error in strategy {strategy.name}: {e}")
        
        return signals
    
    def combine_signals(self, signals: List[TradingSignal]) -> Optional[TradingSignal]:
        """
        Combine multiple signals into one
        
        Args:
            signals: List of signals from strategies
            
        Returns:
            Combined signal or None
        """
        if not signals:
            return None
        
        # If only one signal, return it
        if len(signals) == 1:
            return signals[0]
        
        # Weighted voting
        buy_score = 0.0
        sell_score = 0.0
        total_weight = 0.0
        
        for signal in signals:
            weight = self.strategy_weights.get(signal.reasoning.split(':')[0], 1.0)
            
            if signal.direction == OrderDirection.BUY:
                buy_score += signal.confidence * weight
            elif signal.direction == OrderDirection.SELL:
                sell_score += signal.confidence * weight
            
            total_weight += weight
        
        # Normalize scores
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
        
        # Determine final signal
        if buy_score > sell_score and buy_score > 0.5:
            direction = OrderDirection.BUY
            confidence = buy_score
        elif sell_score > buy_score and sell_score > 0.5:
            direction = OrderDirection.SELL
            confidence = sell_score
        else:
            return None  # No clear signal
        
        # Create combined signal
        combined = TradingSignal(
            pair=signals[0].pair,
            direction=direction,
            confidence=confidence,
            entry_price=signals[0].entry_price,
            timestamp=datetime.now(),
            reasoning=f"Combined from {len(signals)} strategies",
            indicators=signals[0].indicators
        )
        
        return combined
    
    def get_strategy_stats(self) -> Dict[str, Dict]:
        """Get statistics for all strategies"""
        return {
            strategy.name: strategy.get_stats()
            for strategy in self.strategies
        }
    
    def enable_strategy(self, strategy_name: str):
        """Enable a strategy by name"""
        for strategy in self.strategies:
            if strategy.name == strategy_name:
                strategy.enable()
                print(f"✅ Enabled strategy: {strategy_name}")
                return
    
    def disable_strategy(self, strategy_name: str):
        """Disable a strategy by name"""
        for strategy in self.strategies:
            if strategy.name == strategy_name:
                strategy.disable()
                print(f"⏸️ Disabled strategy: {strategy_name}")
                return


# Global strategy orchestrator instance
strategy_orchestrator = StrategyOrchestrator()
