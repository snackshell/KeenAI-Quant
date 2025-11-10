"""
Momentum Trading Strategy
Trades based on momentum indicators (RSI, MACD, ADX)
"""

from typing import Optional
from datetime import datetime

from backend.models.trading_models import MarketContext, TradingSignal, OrderDirection
from AI_Core.strategies.base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """
    Momentum-based trading strategy
    Uses RSI, MACD, and ADX to identify strong momentum
    """
    
    def __init__(self, enabled: bool = True):
        super().__init__(name="Momentum", enabled=enabled)
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.adx_threshold = 25
    
    async def analyze(self, context: MarketContext) -> Optional[TradingSignal]:
        """Analyze market for momentum signals"""
        if not self.enabled or not self.validate_context(context):
            return None
        
        indicators = context.indicators
        rsi = indicators.get('rsi_14', 50)
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        adx = indicators.get('adx_14', 0)
        
        # Strong trend required
        if adx < self.adx_threshold:
            return None
        
        # Buy signal: RSI oversold + MACD bullish crossover
        if rsi < self.rsi_oversold and macd > macd_signal:
            signal = TradingSignal(
                pair=context.pair,
                direction=OrderDirection.BUY,
                confidence=0.7,
                entry_price=context.current_price,
                timestamp=datetime.now(),
                reasoning=f"Momentum: RSI oversold ({rsi:.1f}), MACD bullish, strong trend (ADX {adx:.1f})",
                indicators=indicators
            )
            self.record_signal(signal)
            return signal
        
        # Sell signal: RSI overbought + MACD bearish crossover
        if rsi > self.rsi_overbought and macd < macd_signal:
            signal = TradingSignal(
                pair=context.pair,
                direction=OrderDirection.SELL,
                confidence=0.7,
                entry_price=context.current_price,
                timestamp=datetime.now(),
                reasoning=f"Momentum: RSI overbought ({rsi:.1f}), MACD bearish, strong trend (ADX {adx:.1f})",
                indicators=indicators
            )
            self.record_signal(signal)
            return signal
        
        return None
    
    def get_required_indicators(self) -> list[str]:
        return ['rsi_14', 'macd', 'macd_signal', 'adx_14']
