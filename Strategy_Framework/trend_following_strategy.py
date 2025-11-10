"""
Trend Following Strategy
EMA crossover with ADX filter for all 4 pairs
"""

from datetime import datetime
from typing import Optional

from backend.models.trading_models import MarketContext, TradingSignal, OrderDirection
from .base_strategy import BaseStrategy, StrategyResult, StrategyType


class TrendFollowingStrategy(BaseStrategy):
    """
    Trend Following Strategy using EMA crossover with ADX filter
    
    Entry Conditions:
    - Fast EMA crosses above Slow EMA + ADX > 25 → BUY
    - Fast EMA crosses below Slow EMA + ADX > 25 → SELL
    
    Exit Conditions:
    - Opposite crossover
    - Trailing stop based on ATR
    
    Pairs: All 4 (EUR/USD, XAU/USD, BTC/USD, ETH/USD)
    """
    
    def __init__(self):
        super().__init__(
            name="Trend_Following_EMA_ADX",
            strategy_type=StrategyType.TREND_FOLLOWING
        )
        
        # Configuration
        self.supported_pairs = ["EUR/USD", "XAU/USD", "BTC/USD", "ETH/USD"]
        self.fast_ema_period = 9
        self.slow_ema_period = 21
        self.adx_threshold = 25
        self.min_confidence_threshold = 0.65
        
        # Track previous state for crossover detection
        self.previous_fast_ema = {}
        self.previous_slow_ema = {}
    
    def analyze(self, context: MarketContext) -> StrategyResult:
        """
        Analyze market context for trend following signals
        
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
        fast_ema = context.ema_9
        slow_ema = context.ema_21
        adx = context.adx_14
        atr = context.atr_14
        current_price = context.current_price
        trend = context.trend
        
        # Check if we have previous values for crossover detection
        pair = context.pair
        has_previous = pair in self.previous_fast_ema and pair in self.previous_slow_ema
        
        # Initialize metadata
        metadata = {
            'fast_ema': fast_ema,
            'slow_ema': slow_ema,
            'adx': adx,
            'atr': atr,
            'trend': trend
        }
        
        # Check ADX threshold (must be trending market)
        if adx < self.adx_threshold:
            self.previous_fast_ema[pair] = fast_ema
            self.previous_slow_ema[pair] = slow_ema
            return StrategyResult(
                signal=None,
                confidence=0.0,
                reasoning=f"ADX too low ({adx:.1f} < {self.adx_threshold}), market not trending",
                metadata=metadata,
                timestamp=datetime.now()
            )
        
        # Detect crossover
        signal = None
        confidence = 0.0
        reasoning = ""
        
        if has_previous:
            prev_fast = self.previous_fast_ema[pair]
            prev_slow = self.previous_slow_ema[pair]
            
            # Bullish crossover: fast crosses above slow
            if prev_fast <= prev_slow and fast_ema > slow_ema:
                # Calculate confidence based on ADX strength and trend alignment
                adx_confidence = min(adx / 50.0, 1.0)  # Normalize ADX (50+ is very strong)
                trend_confidence = 1.0 if trend == "bullish" else 0.7
                confidence = (adx_confidence + trend_confidence) / 2.0
                
                if confidence >= self.min_confidence_threshold:
                    # Calculate stop-loss and take-profit
                    stop_loss = current_price - (2.0 * atr)
                    take_profit = current_price + (3.0 * atr)  # 1:1.5 risk-reward
                    
                    signal = TradingSignal(
                        pair=pair,
                        direction=OrderDirection.BUY,
                        confidence=confidence,
                        entry_price=current_price,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        size=0.0,  # Will be calculated by risk management
                        reasoning=f"Bullish EMA crossover with strong ADX ({adx:.1f})",
                        source=self.name,
                        timestamp=datetime.now()
                    )
                    
                    reasoning = f"BUY: Fast EMA crossed above Slow EMA, ADX={adx:.1f}, Trend={trend}"
                else:
                    reasoning = f"Bullish crossover but confidence too low ({confidence:.2%})"
            
            # Bearish crossover: fast crosses below slow
            elif prev_fast >= prev_slow and fast_ema < slow_ema:
                adx_confidence = min(adx / 50.0, 1.0)
                trend_confidence = 1.0 if trend == "bearish" else 0.7
                confidence = (adx_confidence + trend_confidence) / 2.0
                
                if confidence >= self.min_confidence_threshold:
                    stop_loss = current_price + (2.0 * atr)
                    take_profit = current_price - (3.0 * atr)
                    
                    signal = TradingSignal(
                        pair=pair,
                        direction=OrderDirection.SELL,
                        confidence=confidence,
                        entry_price=current_price,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        size=0.0,
                        reasoning=f"Bearish EMA crossover with strong ADX ({adx:.1f})",
                        source=self.name,
                        timestamp=datetime.now()
                    )
                    
                    reasoning = f"SELL: Fast EMA crossed below Slow EMA, ADX={adx:.1f}, Trend={trend}"
                else:
                    reasoning = f"Bearish crossover but confidence too low ({confidence:.2%})"
            else:
                reasoning = f"No crossover detected, Fast EMA {'above' if fast_ema > slow_ema else 'below'} Slow EMA"
        else:
            reasoning = "Waiting for previous values to detect crossover"
        
        # Update previous values
        self.previous_fast_ema[pair] = fast_ema
        self.previous_slow_ema[pair] = slow_ema
        
        return StrategyResult(
            signal=signal,
            confidence=confidence,
            reasoning=reasoning,
            metadata=metadata,
            timestamp=datetime.now()
        )
