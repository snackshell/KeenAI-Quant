"""RSI Mean Reversion Strategy"""
from typing import Optional
from datetime import datetime
from backend.models.trading_models import MarketContext, TradingSignal, OrderDirection
from AI_Core.strategies.base_strategy import BaseStrategy

class RSIMeanReversionStrategy(BaseStrategy):
    def __init__(self, enabled: bool = True):
        super().__init__(name="RSI_MeanReversion", enabled=enabled)
    
    async def analyze(self, context: MarketContext) -> Optional[TradingSignal]:
        if not self.enabled:
            return None
        rsi = context.indicators.get('rsi_14', 50)
        if rsi < 30:
            return TradingSignal(
                pair=context.pair, direction=OrderDirection.BUY,
                confidence=0.7, entry_price=context.current_price,
                timestamp=datetime.now(), reasoning=f"RSI oversold at {rsi:.1f}",
                indicators=context.indicators
            )
        elif rsi > 70:
            return TradingSignal(
                pair=context.pair, direction=OrderDirection.SELL,
                confidence=0.7, entry_price=context.current_price,
                timestamp=datetime.now(), reasoning=f"RSI overbought at {rsi:.1f}",
                indicators=context.indicators
            )
        return None
    
    def get_required_indicators(self) -> list[str]:
        return ['rsi_14']
