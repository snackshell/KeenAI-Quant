"""
Market Context Builder for KeenAI-Quant
Aggregates data, indicators, and market regime into MarketContext for AI analysis
"""

from typing import List, Optional
from datetime import datetime

from backend.models.trading_models import MarketContext, Candle, Position
from .technical_analysis.indicators import calculate_indicators
from .technical_analysis.market_regime import MarketRegimeDetector
from .data_acquisition import data_acquisition


class ContextBuilder:
    """
    Build MarketContext objects for AI analysis
    Combines price data, indicators, positions, and market regime
    """
    
    @staticmethod
    def build_context(
        pair: str,
        timeframe: str = '5m',
        account_balance: float = 0.0,
        current_positions: Optional[List[Position]] = None
    ) -> Optional[MarketContext]:
        """
        Build complete market context for a trading pair
        
        Args:
            pair: Trading pair (e.g., 'EUR/USD')
            timeframe: Timeframe for analysis (default '5m')
            account_balance: Current account balance
            current_positions: List of open positions
            
        Returns:
            MarketContext object or None if insufficient data
        """
        try:
            # Get recent candles from data acquisition
            candles = data_acquisition.get_recent_candles(pair, timeframe, n=200)
            
            if len(candles) < 50:
                print(f"⚠️ Insufficient data for {pair} {timeframe}: {len(candles)} candles")
                return None
            
            # Calculate technical indicators
            indicators = calculate_indicators(candles)
            
            if not indicators:
                print(f"⚠️ Failed to calculate indicators for {pair}")
                return None
            
            # Detect market regime
            market_context_data = MarketRegimeDetector.get_market_context(candles)
            regime = market_context_data['regime']
            
            # Get current price
            current_price = candles[-1].close
            
            # Filter positions for this pair
            pair_positions = [p for p in (current_positions or []) if p.pair == pair]
            
            # Build MarketContext
            context = MarketContext(
                pair=pair,
                current_price=current_price,
                indicators=indicators,
                recent_candles=candles[-100:],  # Last 100 candles
                current_positions=pair_positions,
                account_balance=account_balance,
                market_regime=regime,
                timestamp=datetime.now()
            )
            
            return context
            
        except Exception as e:
            print(f"❌ Error building context for {pair}: {e}")
            return None
    
    @staticmethod
    def build_contexts_for_all_pairs(
        pairs: List[str],
        timeframe: str = '5m',
        account_balance: float = 0.0,
        current_positions: Optional[List[Position]] = None
    ) -> dict:
        """
        Build market contexts for all trading pairs
        
        Returns:
            Dictionary mapping pair to MarketContext
        """
        contexts = {}
        
        for pair in pairs:
            context = ContextBuilder.build_context(
                pair=pair,
                timeframe=timeframe,
                account_balance=account_balance,
                current_positions=current_positions
            )
            
            if context:
                contexts[pair] = context
        
        return contexts
    
    @staticmethod
    def get_context_summary(context: MarketContext) -> dict:
        """
        Get human-readable summary of market context
        Useful for logging and debugging
        """
        return {
            'pair': context.pair,
            'price': context.current_price,
            'regime': context.market_regime,
            'rsi': context.indicators.get('rsi_14', 0),
            'macd': context.indicators.get('macd', 0),
            'adx': context.indicators.get('adx_14', 0),
            'atr': context.indicators.get('atr_14', 0),
            'positions': len(context.current_positions),
            'timestamp': context.timestamp.isoformat()
        }


# Global instance
context_builder = ContextBuilder()
