"""
Mean Reversion Strategy
RSI + Bollinger Bands for EUR/USD and XAU/USD
"""

from datetime import datetime
from typing import Optional

from backend.models.trading_models import MarketContext, TradingSignal, OrderDirection
from .base_strategy import BaseStrategy, StrategyResult, StrategyType


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy using RSI and Bollinger Bands
    
    Entry Conditions:
    - RSI < 30 AND price touches lower BB → BUY (oversold)
    - RSI > 70 AND price touches upper BB → SELL (overbought)
    
    Exit Conditions:
    - Price returns to middle BB
    - Stop-loss hit
    
    Pairs: EUR/USD, XAU/USD (more stable, range-bound pairs)
    """
    
    def __init__(self):
        super().__init__(
            name="Mean_Reversion_RSI_BB",
            strategy_type=StrategyType.MEAN_REVERSION
        )
        
        # Configuration
        self.supported_pairs = ["EUR/USD", "XAU/USD"]
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.bb_touch_threshold = 0.002  # 0.2% from band
        self.min_confidence_threshold = 0.60
    
    def analyze(self, context: MarketContext) -> StrategyResult:
        """
        Analyze market context for mean reversion signals
        
        Args:
            context: MarketContext with market data and indicators
            
        Returns:
            StrategyResult with trading signal if conditions met
        """
        self.last_analysis = datetime.now()
        
        # Validate context
        if not self.validate_context(context):
            return StrategyResult(
                signal=None,
                confidence=0.0,
                reasoning="Invalid market context or unsupported pair",
                metadata={},
                timestamp=datetime.now()
            )
        
        # Extract indicators
        rsi = context.rsi_14
        bb_upper = context.bb_upper
        bb_middle = context.bb_middle
        bb_lower = context.bb_lower
        current_price = context.current_price
        atr = context.atr_14
        market_regime = context.market_regime
        
        # Initialize metadata
        metadata = {
            'rsi': rsi,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'market_regime': market_regime
        }
        
        # Only trade in ranging markets (mean reversion works best here)
        if market_regime == "trending":
            return StrategyResult(
                signal=None,
                confidence=0.0,
                reasoning=f"Market is trending, mean reversion not suitable",
                metadata=metadata,
                timestamp=datetime.now()
            )
        
        signal = None
        confidence = 0.0
        reasoning = ""
        
        # Calculate distance from bands (normalized)
        dist_to_lower = abs(current_price - bb_lower) / current_price
        dist_to_upper = abs(current_price - bb_upper) / current_price
        
        # Oversold condition: RSI < 30 AND price near lower BB
        if rsi < self.rsi_oversold and dist_to_lower < self.bb_touch_threshold:
            # Calculate confidence based on how oversold
            rsi_confidence = (self.rsi_oversold - rsi) / self.rsi_oversold  # 0 to 1
            bb_confidence = 1.0 - (dist_to_lower / self.bb_touch_threshold)  # Closer = higher
            confidence = (rsi_confidence + bb_confidence) / 2.0
            
            if confidence >= self.min_confidence_threshold:
                # Stop-loss below lower BB
                stop_loss = bb_lower - (1.5 * atr)
                # Take-profit at middle BB
                take_profit = bb_middle
                
                signal = TradingSignal(
                    pair=context.pair,
                    direction=OrderDirection.BUY,
                    confidence=confidence,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    size=0.0,
                    reasoning=f"Oversold: RSI={rsi:.1f}, Price at lower BB",
                    source=self.name,
                    timestamp=datetime.now()
                )
                
                reasoning = f"BUY: Oversold condition (RSI={rsi:.1f}, near lower BB)"
            else:
                reasoning = f"Oversold but confidence too low ({confidence:.2%})"
        
        # Overbought condition: RSI > 70 AND price near upper BB
        elif rsi > self.rsi_overbought and dist_to_upper < self.bb_touch_threshold:
            rsi_confidence = (rsi - self.rsi_overbought) / (100 - self.rsi_overbought)
            bb_confidence = 1.0 - (dist_to_upper / self.bb_touch_threshold)
            confidence = (rsi_confidence + bb_confidence) / 2.0
            
            if confidence >= self.min_confidence_threshold:
                stop_loss = bb_upper + (1.5 * atr)
                take_profit = bb_middle
                
                signal = TradingSignal(
                    pair=context.pair,
                    direction=OrderDirection.SELL,
                    confidence=confidence,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    size=0.0,
                    reasoning=f"Overbought: RSI={rsi:.1f}, Price at upper BB",
                    source=self.name,
                    timestamp=datetime.now()
                )
                
                reasoning = f"SELL: Overbought condition (RSI={rsi:.1f}, near upper BB)"
            else:
                reasoning = f"Overbought but confidence too low ({confidence:.2%})"
        
        else:
            # No signal conditions
            if rsi < self.rsi_oversold:
                reasoning = f"RSI oversold ({rsi:.1f}) but price not at lower BB (dist={dist_to_lower:.4f})"
            elif rsi > self.rsi_overbought:
                reasoning = f"RSI overbought ({rsi:.1f}) but price not at upper BB (dist={dist_to_upper:.4f})"
            else:
                reasoning = f"RSI neutral ({rsi:.1f}), no mean reversion signal"
        
        return StrategyResult(
            signal=signal,
            confidence=confidence,
            reasoning=reasoning,
            metadata=metadata,
            timestamp=datetime.now()
        )
