"""
Feature Engineering for KeenAI-Quant
Creates features from raw market data for AI/ML models
"""

import numpy as np
from typing import List, Dict
from backend.models.trading_models import Candle


class FeatureEngineer:
    """
    Engineers features from market data
    Creates technical and statistical features for ML models
    """
    
    def __init__(self):
        """Initialize feature engineer"""
        pass
    
    def create_features(self, candles: List[Candle], indicators: Dict) -> Dict[str, float]:
        """
        Create feature set from candles and indicators
        
        Args:
            candles: List of candles
            indicators: Technical indicators
            
        Returns:
            Dictionary of features
        """
        if len(candles) < 2:
            return {}
        
        features = {}
        
        # Price-based features
        features.update(self._price_features(candles))
        
        # Indicator features
        features.update(self._indicator_features(indicators))
        
        # Statistical features
        features.update(self._statistical_features(candles))
        
        # Time-based features
        features.update(self._time_features(candles[-1]))
        
        return features
    
    def _price_features(self, candles: List[Candle]) -> Dict[str, float]:
        """Extract price-based features"""
        latest = candles[-1]
        prev = candles[-2] if len(candles) > 1 else latest
        
        # Price changes
        price_change = (latest.close - prev.close) / prev.close if prev.close > 0 else 0
        
        # Price position in range
        price_range = latest.high - latest.low
        price_position = (latest.close - latest.low) / price_range if price_range > 0 else 0.5
        
        return {
            'price_change': price_change,
            'price_change_pct': price_change * 100,
            'price_position': price_position,
            'body_size': abs(latest.close - latest.open),
            'upper_wick': latest.high - max(latest.open, latest.close),
            'lower_wick': min(latest.open, latest.close) - latest.low,
            'is_bullish': 1.0 if latest.close > latest.open else 0.0
        }
    
    def _indicator_features(self, indicators: Dict) -> Dict[str, float]:
        """Extract indicator-based features"""
        features = {}
        
        # RSI features
        rsi = indicators.get('rsi_14', 50)
        features['rsi_normalized'] = rsi / 100.0
        features['rsi_oversold'] = 1.0 if rsi < 30 else 0.0
        features['rsi_overbought'] = 1.0 if rsi > 70 else 0.0
        
        # MACD features
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        features['macd_diff'] = macd - macd_signal
        features['macd_bullish'] = 1.0 if macd > macd_signal else 0.0
        
        # Moving average features
        ema_9 = indicators.get('ema_9', 0)
        ema_21 = indicators.get('ema_21', 0)
        if ema_21 > 0:
            features['ema_ratio'] = ema_9 / ema_21
        
        # Bollinger Bands
        bb_upper = indicators.get('bb_upper', 0)
        bb_lower = indicators.get('bb_lower', 0)
        bb_middle = indicators.get('bb_middle', 0)
        if bb_upper > bb_lower:
            features['bb_width'] = (bb_upper - bb_lower) / bb_middle if bb_middle > 0 else 0
        
        # ADX
        features['adx'] = indicators.get('adx_14', 0) / 100.0
        
        return features
    
    def _statistical_features(self, candles: List[Candle]) -> Dict[str, float]:
        """Extract statistical features"""
        if len(candles) < 20:
            return {}
        
        closes = [c.close for c in candles[-20:]]
        volumes = [c.volume for c in candles[-20:]]
        
        return {
            'price_std': np.std(closes),
            'price_mean': np.mean(closes),
            'volume_std': np.std(volumes),
            'volume_mean': np.mean(volumes),
            'price_skew': self._calculate_skew(closes),
            'volume_ratio': volumes[-1] / np.mean(volumes) if np.mean(volumes) > 0 else 1.0
        }
    
    def _time_features(self, candle: Candle) -> Dict[str, float]:
        """Extract time-based features"""
        hour = candle.timestamp.hour
        day_of_week = candle.timestamp.weekday()
        
        return {
            'hour': hour / 24.0,
            'day_of_week': day_of_week / 7.0,
            'is_market_open': 1.0 if 9 <= hour <= 16 else 0.0,
            'is_weekend': 1.0 if day_of_week >= 5 else 0.0
        }
    
    def _calculate_skew(self, values: List[float]) -> float:
        """Calculate skewness of values"""
        if len(values) < 3:
            return 0.0
        
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return 0.0
        
        n = len(values)
        skew = (n / ((n - 1) * (n - 2))) * sum(((x - mean) / std) ** 3 for x in values)
        
        return skew
    
    def normalize_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize features to 0-1 range
        
        Args:
            features: Raw features
            
        Returns:
            Normalized features
        """
        normalized = {}
        
        for key, value in features.items():
            # Clip extreme values
            if abs(value) > 1000:
                value = np.sign(value) * 1000
            
            # Normalize to 0-1 range (simple min-max)
            normalized[key] = (value + 1000) / 2000
        
        return normalized
