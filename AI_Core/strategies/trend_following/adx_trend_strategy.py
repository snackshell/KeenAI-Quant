"""ADX Trend Following Strategy"""
from typing import Optional
from datetime import datetime
from backend.models.trading_models import MarketContext, TradingSignal, OrderDirection
from AI_Core.strategies.base_strategy import BaseStrategy

class ADXTrendStrategy(BaseStrategy):
    def __init__(self, enabled: bool = True):
        super().__init__(name="ADX_Trend", enabled=enabled)
    
    async def analyze(self, context: MarketContext) -> Optional[TradingSignal]:
        if not self.enabled:
            return None
        adx = context.indicators.get('adx_14', 0)
        if adx > 25:  # Strong trend
            ema_9 = context.indicators.get('ema_9', 0)
            ema_21 = context.indicators.get('ema_21', 0)
            if ema_9 > ema_21:
                return TradingSignal(
                    pair=context.pair, direction=OrderDirection.BUY,
                    confidence=0.65, entry_price=context.current_price,
                    timestamp=datetime.now(), reasoning="ADX strong uptrend",
                    indicators=context.indicators
                )
        return None
    
    def get_required_indicators(self) -> list[str]:
        return ['adx_14', 'ema_9', 'ema_21']
