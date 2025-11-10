"""News Sentiment Strategy - Placeholder (requires news API)"""
from typing import Optional
from backend.models.trading_models import MarketContext, TradingSignal
from AI_Core.strategies.base_strategy import BaseStrategy

class NewsSentimentStrategy(BaseStrategy):
    def __init__(self, enabled: bool = False):
        super().__init__(name="NewsSentiment", enabled=enabled)
    
    async def analyze(self, context: MarketContext) -> Optional[TradingSignal]:
        return None
    
    def get_required_indicators(self) -> list[str]:
        return []
