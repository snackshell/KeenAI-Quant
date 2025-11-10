"""
Trading Strategies Module for KeenAI-Quant
Collection of algorithmic trading strategies
"""

from .base_strategy import BaseStrategy
from .strategy_orchestrator import strategy_orchestrator, StrategyOrchestrator

# Trend Following Strategies
from .trend_following.momentum_strategy import MomentumStrategy
from .trend_following.adx_trend_strategy import ADXTrendStrategy
from .trend_following.breakout_strategy import BreakoutStrategy
from .trend_following.moving_average_strategy import MovingAverageStrategy

# Mean Reversion Strategies
from .mean_reversion.bollinger_bands_strategy import BollingerBandsStrategy
from .mean_reversion.rsi_mean_reversion import RSIMeanReversionStrategy

__all__ = [
    # Base
    'BaseStrategy',
    'strategy_orchestrator',
    'StrategyOrchestrator',
    # Trend Following
    'MomentumStrategy',
    'ADXTrendStrategy',
    'BreakoutStrategy',
    'MovingAverageStrategy',
    # Mean Reversion
    'BollingerBandsStrategy',
    'RSIMeanReversionStrategy'
]
