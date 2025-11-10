"""
Market Regime Detection for KeenAI-Quant
Identifies market conditions: trending, ranging, volatile
"""

import numpy as np
from typing import List, Tuple
from backend.models.trading_models import Candle
from .indicators import TechnicalIndicators


class MarketRegimeDetector:
    """
    Detect market regime to adapt trading strategies
    """
    
    @staticmethod
    def detect_regime(candles: List[Candle]) -> str:
        """
        Detect current market regime
        Returns: 'trending', 'ranging', or 'volatile'
        """
        if len(candles) < 50:
            return 'unknown'
        
        # Calculate indicators for regime detection
        adx = TechnicalIndicators.adx(candles, 14)
        atr = TechnicalIndicators.atr(candles, 14)
        bb = TechnicalIndicators.bollinger_bands(candles, 20, 2.0)
        
        if not adx or not atr or not bb:
            return 'unknown'
        
        current_price = candles[-1].close
        bb_upper, bb_middle, bb_lower = bb
        
        # Calculate volatility
        closes = np.array([c.close for c in candles[-20:]])
        volatility = np.std(closes) / np.mean(closes) * 100
        
        # Regime detection logic
        if adx > 25:
            # Strong trend
            return 'trending'
        elif volatility > 2.0:
            # High volatility
            return 'volatile'
        else:
            # Range-bound
            return 'ranging'
    
    @staticmethod
    def get_trend_direction(candles: List[Candle]) -> str:
        """
        Get trend direction
        Returns: 'up', 'down', or 'sideways'
        """
        if len(candles) < 50:
            return 'sideways'
        
        # Use multiple EMAs for trend confirmation
        ema_9 = TechnicalIndicators.ema(candles, 9)
        ema_21 = TechnicalIndicators.ema(candles, 21)
        ema_55 = TechnicalIndicators.ema(candles, 55)
        
        if not ema_9 or not ema_21 or not ema_55:
            return 'sideways'
        
        # Trend is up if EMAs are aligned upward
        if ema_9 > ema_21 > ema_55:
            return 'up'
        elif ema_9 < ema_21 < ema_55:
            return 'down'
        else:
            return 'sideways'
    
    @staticmethod
    def get_volatility_level(candles: List[Candle]) -> str:
        """
        Get volatility level
        Returns: 'low', 'normal', or 'high'
        """
        if len(candles) < 20:
            return 'normal'
        
        atr = TechnicalIndicators.atr(candles, 14)
        if not atr:
            return 'normal'
        
        current_price = candles[-1].close
        atr_percentage = (atr / current_price) * 100
        
        if atr_percentage < 0.5:
            return 'low'
        elif atr_percentage > 2.0:
            return 'high'
        else:
            return 'normal'
    
    @staticmethod
    def get_market_context(candles: List[Candle]) -> dict:
        """
        Get complete market context
        Returns dictionary with regime, trend, volatility
        """
        return {
            'regime': MarketRegimeDetector.detect_regime(candles),
            'trend': MarketRegimeDetector.get_trend_direction(candles),
            'volatility': MarketRegimeDetector.get_volatility_level(candles)
        }
