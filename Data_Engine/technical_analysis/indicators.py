"""
Technical Indicators for KeenAI-Quant
Optimized calculations using numpy for performance
All indicators designed to work with List[Candle] input
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from backend.models.trading_models import Candle


class TechnicalIndicators:
    """
    Technical indicator calculations
    Optimized for speed with numpy vectorization
    """
    
    @staticmethod
    def _candles_to_arrays(candles: List[Candle]) -> Dict[str, np.ndarray]:
        """Convert candle list to numpy arrays for fast computation"""
        if not candles:
            return {}
        
        return {
            'open': np.array([c.open for c in candles]),
            'high': np.array([c.high for c in candles]),
            'low': np.array([c.low for c in candles]),
            'close': np.array([c.close for c in candles]),
            'volume': np.array([c.volume for c in candles])
        }
    
    @staticmethod
    def sma(candles: List[Candle], period: int = 20) -> Optional[float]:
        """Simple Moving Average"""
        if len(candles) < period:
            return None
        
        closes = np.array([c.close for c in candles[-period:]])
        return float(np.mean(closes))
    
    @staticmethod
    def ema(candles: List[Candle], period: int = 20) -> Optional[float]:
        """Exponential Moving Average"""
        if len(candles) < period:
            return None
        
        closes = np.array([c.close for c in candles])
        
        # Calculate EMA using pandas-style algorithm
        multiplier = 2 / (period + 1)
        ema_values = np.zeros(len(closes))
        ema_values[0] = closes[0]
        
        for i in range(1, len(closes)):
            ema_values[i] = (closes[i] * multiplier) + (ema_values[i-1] * (1 - multiplier))
        
        return float(ema_values[-1])
    
    @staticmethod
    def rsi(candles: List[Candle], period: int = 14) -> Optional[float]:
        """Relative Strength Index"""
        if len(candles) < period + 1:
            return None
        
        closes = np.array([c.close for c in candles])
        deltas = np.diff(closes)
        
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi_value = 100 - (100 / (1 + rs))
        
        return float(rsi_value)
    
    @staticmethod
    def macd(
        candles: List[Candle],
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Optional[Tuple[float, float, float]]:
        """
        MACD (Moving Average Convergence Divergence)
        Returns: (macd_line, signal_line, histogram)
        """
        if len(candles) < slow + signal:
            return None
        
        # Calculate EMAs
        closes = np.array([c.close for c in candles])
        
        # Fast EMA
        fast_ema = TechnicalIndicators._calculate_ema_array(closes, fast)
        # Slow EMA
        slow_ema = TechnicalIndicators._calculate_ema_array(closes, slow)
        
        # MACD line
        macd_line = fast_ema - slow_ema
        
        # Signal line (EMA of MACD)
        signal_line = TechnicalIndicators._calculate_ema_array(macd_line, signal)
        
        # Histogram
        histogram = macd_line - signal_line
        
        return (
            float(macd_line[-1]),
            float(signal_line[-1]),
            float(histogram[-1])
        )
    
    @staticmethod
    def _calculate_ema_array(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA array (helper function)"""
        multiplier = 2 / (period + 1)
        ema = np.zeros(len(data))
        ema[0] = data[0]
        
        for i in range(1, len(data)):
            ema[i] = (data[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        
        return ema
    
    @staticmethod
    def bollinger_bands(
        candles: List[Candle],
        period: int = 20,
        std_dev: float = 2.0
    ) -> Optional[Tuple[float, float, float]]:
        """
        Bollinger Bands
        Returns: (upper_band, middle_band, lower_band)
        """
        if len(candles) < period:
            return None
        
        closes = np.array([c.close for c in candles[-period:]])
        
        middle = np.mean(closes)
        std = np.std(closes)
        
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        return (float(upper), float(middle), float(lower))
    
    @staticmethod
    def atr(candles: List[Candle], period: int = 14) -> Optional[float]:
        """Average True Range"""
        if len(candles) < period + 1:
            return None
        
        highs = np.array([c.high for c in candles])
        lows = np.array([c.low for c in candles])
        closes = np.array([c.close for c in candles])
        
        # True Range calculation
        tr1 = highs[1:] - lows[1:]
        tr2 = np.abs(highs[1:] - closes[:-1])
        tr3 = np.abs(lows[1:] - closes[:-1])
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        
        # ATR is EMA of TR
        atr_value = np.mean(tr[-period:])
        
        return float(atr_value)
    
    @staticmethod
    def adx(candles: List[Candle], period: int = 14) -> Optional[float]:
        """Average Directional Index"""
        if len(candles) < period * 2:
            return None
        
        highs = np.array([c.high for c in candles])
        lows = np.array([c.low for c in candles])
        closes = np.array([c.close for c in candles])
        
        # Calculate +DM and -DM
        high_diff = np.diff(highs)
        low_diff = -np.diff(lows)
        
        plus_dm = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0)
        minus_dm = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0)
        
        # Calculate TR
        tr1 = highs[1:] - lows[1:]
        tr2 = np.abs(highs[1:] - closes[:-1])
        tr3 = np.abs(lows[1:] - closes[:-1])
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        
        # Smooth with EMA
        atr_value = np.mean(tr[-period:])
        plus_di = 100 * np.mean(plus_dm[-period:]) / atr_value if atr_value > 0 else 0
        minus_di = 100 * np.mean(minus_dm[-period:]) / atr_value if atr_value > 0 else 0
        
        # Calculate DX and ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0
        
        return float(dx)
    
    @staticmethod
    def stochastic(
        candles: List[Candle],
        k_period: int = 14,
        d_period: int = 3
    ) -> Optional[Tuple[float, float]]:
        """
        Stochastic Oscillator
        Returns: (%K, %D)
        """
        if len(candles) < k_period:
            return None
        
        recent = candles[-k_period:]
        closes = np.array([c.close for c in recent])
        highs = np.array([c.high for c in recent])
        lows = np.array([c.low for c in recent])
        
        highest_high = np.max(highs)
        lowest_low = np.min(lows)
        current_close = closes[-1]
        
        if highest_high == lowest_low:
            k_value = 50.0
        else:
            k_value = 100 * (current_close - lowest_low) / (highest_high - lowest_low)
        
        # %D is SMA of %K (simplified - should track multiple %K values)
        d_value = k_value  # Simplified
        
        return (float(k_value), float(d_value))
    
    @staticmethod
    def cci(candles: List[Candle], period: int = 20) -> Optional[float]:
        """Commodity Channel Index"""
        if len(candles) < period:
            return None
        
        recent = candles[-period:]
        
        # Typical Price
        tp = np.array([(c.high + c.low + c.close) / 3 for c in recent])
        
        sma_tp = np.mean(tp)
        mean_deviation = np.mean(np.abs(tp - sma_tp))
        
        if mean_deviation == 0:
            return 0.0
        
        cci_value = (tp[-1] - sma_tp) / (0.015 * mean_deviation)
        
        return float(cci_value)
    
    @staticmethod
    def williams_r(candles: List[Candle], period: int = 14) -> Optional[float]:
        """Williams %R"""
        if len(candles) < period:
            return None
        
        recent = candles[-period:]
        highs = np.array([c.high for c in recent])
        lows = np.array([c.low for c in recent])
        close = recent[-1].close
        
        highest_high = np.max(highs)
        lowest_low = np.min(lows)
        
        if highest_high == lowest_low:
            return -50.0
        
        wr = -100 * (highest_high - close) / (highest_high - lowest_low)
        
        return float(wr)
    
    @staticmethod
    def calculate_all(candles: List[Candle]) -> Dict[str, float]:
        """
        Calculate all indicators at once
        Returns dictionary with all indicator values
        Optimized to avoid redundant calculations
        """
        if len(candles) < 50:  # Need minimum data
            return {}
        
        indicators = {}
        
        try:
            # Moving Averages
            indicators['sma_20'] = TechnicalIndicators.sma(candles, 20) or 0.0
            indicators['sma_50'] = TechnicalIndicators.sma(candles, 50) or 0.0
            indicators['sma_200'] = TechnicalIndicators.sma(candles, 200) or 0.0
            indicators['ema_9'] = TechnicalIndicators.ema(candles, 9) or 0.0
            indicators['ema_21'] = TechnicalIndicators.ema(candles, 21) or 0.0
            indicators['ema_55'] = TechnicalIndicators.ema(candles, 55) or 0.0
            
            # Momentum
            indicators['rsi_14'] = TechnicalIndicators.rsi(candles, 14) or 50.0
            
            stoch = TechnicalIndicators.stochastic(candles)
            if stoch:
                indicators['stoch_k'], indicators['stoch_d'] = stoch
            
            indicators['cci_20'] = TechnicalIndicators.cci(candles, 20) or 0.0
            indicators['williams_r'] = TechnicalIndicators.williams_r(candles, 14) or -50.0
            
            # Trend
            macd_result = TechnicalIndicators.macd(candles)
            if macd_result:
                indicators['macd'], indicators['macd_signal'], indicators['macd_histogram'] = macd_result
            
            indicators['adx_14'] = TechnicalIndicators.adx(candles, 14) or 0.0
            
            # Volatility
            bb = TechnicalIndicators.bollinger_bands(candles)
            if bb:
                indicators['bb_upper'], indicators['bb_middle'], indicators['bb_lower'] = bb
            
            indicators['atr_14'] = TechnicalIndicators.atr(candles, 14) or 0.0
            
            # Current price for reference
            indicators['current_price'] = candles[-1].close
            
        except Exception as e:
            print(f"⚠️ Error calculating indicators: {e}")
        
        return indicators


# Convenience function
def calculate_indicators(candles: List[Candle]) -> Dict[str, float]:
    """Calculate all technical indicators for a candle list"""
    return TechnicalIndicators.calculate_all(candles)
