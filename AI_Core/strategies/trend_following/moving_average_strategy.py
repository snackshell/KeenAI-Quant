"""Moving Average Crossover Strategy"""
from typing import Optional
from datetime import datetime
from backend.models.trading_models import MarketContext, TradingSignal, OrderDirection
from AI_Core.strategies.base_strategy import BaseStrategy

class MovingAverageStrategy(BaseStrategy):
    def __init__(self, enabled: bool = True):
        super().__init__(name="MA_Crossover", enabled=enabled)
    
    async def analyze(self, context: MarketContext) -> Optional[TradingSignal]:
        if not self.enabled:
            return None
        ema_9 = context.indicators.get('ema_9', 0)
        ema_21 = context.indicators.get('ema_21', 0)
        if ema_9 > ema_21:
            return TradingSignal(
                pair=context.pair, direction=OrderDirection.BUY,
                confidence=0.6, entry_price=context.current_price,
                timestamp=datetime.now(), reasoning="EMA 9/21 bullish crossover",
                indicators=context.indicators
            )
        return None
    
    def get_required_indicators(self) -> list[str]:
        return ['ema_9', 'ema_21']
