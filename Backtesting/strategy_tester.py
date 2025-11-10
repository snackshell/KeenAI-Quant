"""
Strategy Tester for KeenAI-Quant
Tests trading strategies against historical data
"""

from typing import List, Dict, Optional
from datetime import datetime
from backend.models.trading_models import Candle, TradingSignal, Position
from Backtesting.backtest_engine import BacktestEngine, BacktestConfig
from Backtesting.performance_analyzer import PerformanceAnalyzer


class StrategyTester:
    """
    Tests trading strategies with historical data
    Provides comprehensive performance metrics
    """
    
    def __init__(self):
        """Initialize strategy tester"""
        self.backtest_engine = BacktestEngine()
        self.performance_analyzer = PerformanceAnalyzer()
    
    def test_strategy(
        self,
        strategy_name: str,
        historical_data: List[Candle],
        initial_balance: float = 10000.0,
        risk_per_trade: float = 0.02
    ) -> Dict:
        """
        Test a strategy against historical data
        
        Args:
            strategy_name: Name of strategy being tested
            historical_data: Historical candle data
            initial_balance: Starting capital
            risk_per_trade: Risk percentage per trade
            
        Returns:
            Dictionary with test results
        """
        # Create backtest configuration
        config = BacktestConfig(
            initial_balance=initial_balance,
            risk_per_trade=risk_per_trade,
            max_position_size=0.25,
            use_stop_loss=True,
            use_take_profit=True
        )
        
        # Run backtest
        result = self.backtest_engine.run(config, historical_data)
        
        # Analyze performance
        metrics = self.performance_analyzer.calculate_metrics(
            result.trades,
            result.equity_curve,
            initial_balance
        )
        
        return {
            'strategy_name': strategy_name,
            'test_period': {
                'start': historical_data[0].timestamp if historical_data else None,
                'end': historical_data[-1].timestamp if historical_data else None,
                'candles': len(historical_data)
            },
            'performance': metrics.to_dict(),
            'trades': len(result.trades),
            'final_balance': result.final_balance,
            'total_return': ((result.final_balance - initial_balance) / initial_balance) * 100
        }
    
    def compare_strategies(
        self,
        strategies: List[str],
        historical_data: List[Candle],
        initial_balance: float = 10000.0
    ) -> Dict:
        """
        Compare multiple strategies
        
        Args:
            strategies: List of strategy names
            historical_data: Historical data
            initial_balance: Starting capital
            
        Returns:
            Comparison results
        """
        results = {}
        
        for strategy in strategies:
            results[strategy] = self.test_strategy(
                strategy,
                historical_data,
                initial_balance
            )
        
        # Find best strategy
        best_strategy = max(
            results.items(),
            key=lambda x: x[1]['performance']['sharpe_ratio']
        )
        
        return {
            'strategies': results,
            'best_strategy': best_strategy[0],
            'comparison': {
                'by_return': sorted(
                    results.items(),
                    key=lambda x: x[1]['total_return'],
                    reverse=True
                ),
                'by_sharpe': sorted(
                    results.items(),
                    key=lambda x: x[1]['performance']['sharpe_ratio'],
                    reverse=True
                )
            }
        }
