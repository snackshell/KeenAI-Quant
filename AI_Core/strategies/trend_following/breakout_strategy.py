"""Breakout Strategy"""
from typing import Optional
from datetime import datetime
from backend.models.trading_models import MarketContext, TradingSignal, OrderDirection
from AI_Core.strategies.base_strategy import BaseStrategy

class BreakoutStrategy(BaseStrategy):
    def __init__(self, enabled: bool = True):
        super().__init__(name="Breakout", enabled=enabled)
    
    async def analyze(self, context: MarketContext) -> Optional[TradingSignal]:
        if not self.enabled:
            return None
        price = context.current_price
        bb_upper = context.indicators.get('bb_upper', 0)
        bb_lower = context.indicators.get('bb_lower', 0)
        if price > bb_upper:
            return TradingSignal(
                pair=context.pair, direction=OrderDirection.BUY,
                confidence=0.7, entry_price=price,
                timestamp=datetime.now(), reasoning="Breakout above Bollinger upper",
                indicators=context.indicators
            )
        return None
    
    def get_required_indicators(self) -> list[str]:
        return ['bb_upper', 'bb_lower']
