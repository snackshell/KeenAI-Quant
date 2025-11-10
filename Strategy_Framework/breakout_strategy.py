"""
Breakout Strategy
Donchian Channel breakouts for BTC/USD and ETH/USD
Based on resources/mcpst-main/donchian.py
"""

from datetime import datetime
from typing import Optional, Dict
import numpy as np

from backend.models.trading_models import MarketContext, TradingSignal, OrderDirection
from .base_strategy import BaseStrategy, StrategyResult, StrategyType


class BreakoutStrategy(BaseStrategy):
    """
    Breakout Strategy using Donchian Channels
    
    Entry Conditions:
    - Price breaks above upper channel (highest high) → BUY
    - Price breaks below lower channel (lowest low) → SELL
    - Volume confirmation (optional enhancement)
    
    Exit Conditions:
    - Opposite breakout
    - Trailing stop based on ATR
    
    Pairs: BTC/USD, ETH/USD (volatile, breakout-prone pairs)
    
    Based on Donchian breakout strategy from resources
    """
    
    def __init__(self, lookback: int = 20):
        super().__init__(
            name="Breakout_Donchian",
            strategy_type=StrategyType.BREAKOUT
        )
        
        # Configuration
        self.supported_pairs = ["BTC/USD", "ETH/USD"]
        self.lookback = lookback  # Donchian channel period
        self.min_confidence_threshold = 0.65
        
        # Track price history for channel calculation
        self.price_history: Dict[str, list] = {}
        self.max_history_size = 200  # Keep last 200 bars
        
        # Track previous position to detect breakouts
        self.previous_position: Dict[str, Optional[str]] = {}  # 'long', 'short', None
    
    def _update_price_history(self, pair: str, price: float) -> None:
        """Update price history for channel calculation"""
        if pair not in self.price_history:
            self.price_history[pair] = []
        
        self.price_history[pair].append(price)
        
        # Keep only recent history
        if len(self.price_history[pair]) > self.max_history_size:
            self.price_history[pair] = self.price_history[pair][-self.max_history_size:]
    
    def _calculate_donchian_channels(self, pair: str) -> tuple:
        """
        Calculate Donchian channel upper and lower bounds
        
        Returns:
            (upper_channel, lower_channel) or (None, None) if insufficient data
        """
        if pair not in self.price_history:
            return None, None
        
        prices = self.price_history[pair]
        
        if len(prices) < self.lookback:
            return None, None
        
        # Get last lookback-1 prices (excluding current)
        recent_prices = prices[-(self.lookback):-1]
        
        upper_channel = max(recent_prices)
        lower_channel = min(recent_prices)
        
        return upper_channel, lower_channel
    
    def analyze(self, context: MarketContext) -> StrategyResult:
        """
        Analyze market context for breakout signals
        
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
        
        pair = context.pair
        current_price = context.current_price
        atr = context.atr_14
        volatility_percentile = context.volatility_percentile
        
        # Update price history
        self._update_price_history(pair, current_price)
        
        # Calculate Donchian channels
        upper_channel, lower_channel = self._calculate_donchian_channels(pair)
        
        # Initialize metadata
        metadata = {
            'upper_channel': upper_channel,
            'lower_channel': lower_channel,
            'lookback': self.lookback,
            'volatility_percentile': volatility_percentile,
            'price_history_size': len(self.price_history.get(pair, []))
        }
        
        # Need sufficient data
        if upper_channel is None or lower_channel is None:
            return StrategyResult(
                signal=None,
                confidence=0.0,
                reasoning=f"Insufficient price history ({len(self.price_history.get(pair, []))} < {self.lookback})",
                metadata=metadata,
                timestamp=datetime.now()
            )
        
        signal = None
        confidence = 0.0
        reasoning = ""
        
        # Get previous position
        prev_position = self.previous_position.get(pair)
        
        # Bullish breakout: price breaks above upper channel
        if current_price > upper_channel:
            # Calculate breakout strength
            channel_range = upper_channel - lower_channel
            breakout_distance = current_price - upper_channel
            breakout_strength = min(breakout_distance / channel_range, 1.0) if channel_range > 0 else 0.5
            
            # Higher volatility = more reliable breakout for crypto
            volatility_confidence = min(volatility_percentile / 80.0, 1.0)
            
            confidence = (breakout_strength + volatility_confidence) / 2.0
            
            # Only signal if we weren't already long
            if prev_position != 'long' and confidence >= self.min_confidence_threshold:
                stop_loss = lower_channel  # Stop at opposite channel
                take_profit = current_price + (2.0 * (current_price - stop_loss))  # 1:2 RR
                
                signal = TradingSignal(
                    pair=pair,
                    direction=OrderDirection.BUY,
                    confidence=confidence,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    size=0.0,
                    reasoning=f"Bullish breakout above {self.lookback}-period high",
                    source=self.name,
                    timestamp=datetime.now()
                )
                
                self.previous_position[pair] = 'long'
                reasoning = f"BUY: Breakout above upper channel ({upper_channel:.2f}), strength={breakout_strength:.2%}"
            else:
                if prev_position == 'long':
                    reasoning = f"Already long, price above upper channel"
                else:
                    reasoning = f"Breakout but confidence too low ({confidence:.2%})"
        
        # Bearish breakout: price breaks below lower channel
        elif current_price < lower_channel:
            channel_range = upper_channel - lower_channel
            breakout_distance = lower_channel - current_price
            breakout_strength = min(breakout_distance / channel_range, 1.0) if channel_range > 0 else 0.5
            
            volatility_confidence = min(volatility_percentile / 80.0, 1.0)
            confidence = (breakout_strength + volatility_confidence) / 2.0
            
            if prev_position != 'short' and confidence >= self.min_confidence_threshold:
                stop_loss = upper_channel
                take_profit = current_price - (2.0 * (stop_loss - current_price))
                
                signal = TradingSignal(
                    pair=pair,
                    direction=OrderDirection.SELL,
                    confidence=confidence,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    size=0.0,
                    reasoning=f"Bearish breakout below {self.lookback}-period low",
                    source=self.name,
                    timestamp=datetime.now()
                )
                
                self.previous_position[pair] = 'short'
                reasoning = f"SELL: Breakout below lower channel ({lower_channel:.2f}), strength={breakout_strength:.2%}"
            else:
                if prev_position == 'short':
                    reasoning = f"Already short, price below lower channel"
                else:
                    reasoning = f"Breakout but confidence too low ({confidence:.2%})"
        
        # Inside channel - consolidation
        else:
            self.previous_position[pair] = None
            channel_position = (current_price - lower_channel) / (upper_channel - lower_channel) if (upper_channel - lower_channel) > 0 else 0.5
            reasoning = f"Price inside channel ({channel_position:.1%} from bottom), waiting for breakout"
        
        return StrategyResult(
            signal=signal,
            confidence=confidence,
            reasoning=reasoning,
            metadata=metadata,
            timestamp=datetime.now()
        )
