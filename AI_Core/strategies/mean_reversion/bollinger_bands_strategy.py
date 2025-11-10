"""Bollinger Bands Mean Reversion Strategy"""
from typing import Optional
from datetime import datetime
from backend.models.trading_models import MarketContext, TradingSignal, OrderDirection
from AI_Core.strategies.base_strategy import BaseStrategy

class BollingerBandsStrategy(BaseStrategy):
    def __init__(self, enabled: bool = True):
        super().__init__(name="BB_MeanReversion", enabled=enabled)
    
    async def analyze(self, context: MarketContext) -> Optional[TradingSignal]:
        if not self.enabled:
            return None
        price = context.current_price
        bb_lower = context.indicators.get('bb_lower', 0)
        bb_upper = context.indicators.get('bb_upper', 0)
        if price < bb_lower:
            return TradingSignal(
                pair=context.pair, direction=OrderDirection.BUY,
                confidence=0.65, entry_price=price,
                timestamp=datetime.now(), reasoning="Price below BB lower - mean reversion",
                indicators=context.indicators
            )
        elif price > bb_upper:
            return TradingSignal(
                pair=context.pair, direction=OrderDirection.SELL,
                confidence=0.65, entry_price=price,
                timestamp=datetime.now(), reasoning="Price above BB upper - mean reversion",
                indicators=context.indicators
            )
        return None
    
    def get_required_indicators(self) -> list[str]:
        return ['bb_upper', 'bb_middle', 'bb_lower']
