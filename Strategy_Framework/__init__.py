"""
Strategy Framework Module for KeenAI-Quant
Implements trading strategies with risk management integration
"""

from .base_strategy import BaseStrategy, StrategyResult, StrategyType
from .trend_following_strategy import TrendFollowingStrategy
from .mean_reversion_strategy import MeanReversionStrategy
from .breakout_strategy import BreakoutStrategy
from .strategy_orchestrator import StrategyOrchestrator

__all__ = [
    'BaseStrategy',
    'StrategyResult',
    'StrategyType',
    'TrendFollowingStrategy',
    'MeanReversionStrategy',
    'BreakoutStrategy',
    'StrategyOrchestrator'
]
