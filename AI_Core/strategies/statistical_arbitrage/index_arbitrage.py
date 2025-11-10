"""Index Arbitrage - Placeholder"""
from typing import Optional
from backend.models.trading_models import MarketContext, TradingSignal
from AI_Core.strategies.base_strategy import BaseStrategy

class IndexArbitrageStrategy(BaseStrategy):
    def __init__(self, enabled: bool = False):
        super().__init__(name="IndexArb", enabled=enabled)
    
    async def analyze(self, context: MarketContext) -> Optional[TradingSignal]:
        return None
    
    def get_required_indicators(self) -> list[str]:
        return []
