"""
Strategy Orchestrator
Manages multiple strategies and resolves conflicts
"""

from typing import List, Dict, Optional
from datetime import datetime

from backend.models.trading_models import MarketContext, TradingSignal, OrderDirection
from .base_strategy import BaseStrategy, StrategyResult
from .trend_following_strategy import TrendFollowingStrategy
from .mean_reversion_strategy import MeanReversionStrategy
from .breakout_strategy import BreakoutStrategy


class StrategyOrchestrator:
    """
    Orchestrates multiple trading strategies
    
    Responsibilities:
    - Run multiple strategies in parallel
    - Resolve conflicting signals
    - Track strategy performance
    - Enable/disable strategies dynamically
    """
    
    def __init__(self):
        """Initialize strategy orchestrator with all strategies"""
        self.strategies: List[BaseStrategy] = []
        
        # Initialize all strategies
        self.trend_following = TrendFollowingStrategy()
        self.mean_reversion = MeanReversionStrategy()
        self.breakout = BreakoutStrategy()
        
        # Register strategies
        self.register_strategy(self.trend_following)
        self.register_strategy(self.mean_reversion)
        self.register_strategy(self.breakout)
        
        print(f"🎯 Strategy Orchestrator initialized with {len(self.strategies)} strategies")
    
    def register_strategy(self, strategy: BaseStrategy) -> None:
        """
        Register a new strategy
        
        Args:
            strategy: BaseStrategy instance to register
        """
        self.strategies.append(strategy)
        print(f"   ✅ Registered: {strategy.name}")
    
    def run_strategies(self, context: MarketContext) -> List[StrategyResult]:
        """
        Run all enabled strategies for given market context
        
        Args:
            context: MarketContext with market data
            
        Returns:
            List of StrategyResult from all strategies
        """
        results = []
        
        for strategy in self.strategies:
            # Check if strategy should trade this pair
            if not strategy.should_trade(context.pair, datetime.now()):
                continue
            
            try:
                result = strategy.analyze(context)
                results.append(result)
            except Exception as e:
                print(f"❌ Error in {strategy.name}: {str(e)}")
                continue
        
        return results
    
    def resolve_conflicts(self, results: List[StrategyResult]) -> Optional[TradingSignal]:
        """
        Resolve conflicting signals from multiple strategies
        
        Conflict Resolution Rules:
        1. Same pair, opposite directions → No trade (cancel out)
        2. Same pair, same direction → Combine (use highest confidence)
        3. No signals → No trade
        4. Single signal → Use it
        
        Args:
            results: List of StrategyResult from strategies
            
        Returns:
            Single TradingSignal or None
        """
        # Filter results with actual signals
        signals_with_results = [(r.signal, r.confidence, r.reasoning) for r in results if r.signal is not None]
        
        if not signals_with_results:
            return None
        
        # If only one signal, use it
        if len(signals_with_results) == 1:
            signal, confidence, reasoning = signals_with_results[0]
            print(f"✅ Single signal: {signal.direction.value} {signal.pair} (confidence={confidence:.2%})")
            return signal
        
        # Multiple signals - check for conflicts
        buy_signals = [(s, c, r) for s, c, r in signals_with_results if s.direction == OrderDirection.BUY]
        sell_signals = [(s, c, r) for s, c, r in signals_with_results if s.direction == OrderDirection.SELL]
        
        # Opposite directions → Cancel out
        if buy_signals and sell_signals:
            print(f"⚠️ Conflicting signals: {len(buy_signals)} BUY vs {len(sell_signals)} SELL → No trade")
            return None
        
        # Same direction → Use highest confidence
        if buy_signals:
            best_signal, best_confidence, best_reasoning = max(buy_signals, key=lambda x: x[1])
            print(f"✅ Multiple BUY signals, using highest confidence: {best_confidence:.2%}")
            return best_signal
        
        if sell_signals:
            best_signal, best_confidence, best_reasoning = max(sell_signals, key=lambda x: x[1])
            print(f"✅ Multiple SELL signals, using highest confidence: {best_confidence:.2%}")
            return best_signal
        
        return None
    
    def analyze_market(self, context: MarketContext) -> Optional[TradingSignal]:
        """
        Analyze market with all strategies and return final signal
        
        Args:
            context: MarketContext with market data
            
        Returns:
            Final TradingSignal after conflict resolution, or None
        """
        # Run all strategies
        results = self.run_strategies(context)
        
        if not results:
            return None
        
        # Log results
        print(f"\n📊 Strategy Analysis for {context.pair}:")
        for result in results:
            if result.signal:
                print(f"   {result.signal.source}: {result.signal.direction.value} (confidence={result.confidence:.2%})")
                print(f"      Reasoning: {result.reasoning}")
            else:
                print(f"   {result.reasoning}")
        
        # Resolve conflicts and return final signal
        final_signal = self.resolve_conflicts(results)
        
        if final_signal:
            print(f"\n✅ Final Signal: {final_signal.direction.value} {final_signal.pair}")
            print(f"   Entry: {final_signal.entry_price:.5f}")
            print(f"   Stop Loss: {final_signal.stop_loss:.5f}")
            print(f"   Take Profit: {final_signal.take_profit:.5f}")
        else:
            print(f"\n⏸️ No final signal generated")
        
        return final_signal
    
    def get_strategy_by_name(self, name: str) -> Optional[BaseStrategy]:
        """Get strategy by name"""
        for strategy in self.strategies:
            if strategy.name == name:
                return strategy
        return None
    
    def enable_strategy(self, name: str) -> bool:
        """Enable a strategy by name"""
        strategy = self.get_strategy_by_name(name)
        if strategy:
            strategy.enable()
            return True
        return False
    
    def disable_strategy(self, name: str) -> bool:
        """Disable a strategy by name"""
        strategy = self.get_strategy_by_name(name)
        if strategy:
            strategy.disable()
            return True
        return False
    
    def get_all_performance_metrics(self) -> Dict[str, Dict]:
        """Get performance metrics for all strategies"""
        return {
            strategy.name: strategy.get_performance_metrics()
            for strategy in self.strategies
        }
    
    def get_enabled_strategies(self) -> List[str]:
        """Get list of enabled strategy names"""
        return [s.name for s in self.strategies if s.enabled]
    
    def get_strategies_for_pair(self, pair: str) -> List[str]:
        """Get list of strategies that support given pair"""
        return [s.name for s in self.strategies if pair in s.supported_pairs]


# Global instance
strategy_orchestrator = StrategyOrchestrator()
