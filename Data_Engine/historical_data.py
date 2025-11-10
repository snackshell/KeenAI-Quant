"""
Historical Data Manager for KeenAI-Quant
Manages historical market data storage and retrieval
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from backend.models.trading_models import Candle
import json
import os


class HistoricalDataManager:
    """
    Manages historical market data
    Stores and retrieves candle data for backtesting
    """
    
    def __init__(self, data_dir: str = "./data/historical"):
        """
        Initialize historical data manager
        
        Args:
            data_dir: Directory to store historical data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_candles(self, pair: str, timeframe: str, candles: List[Candle]):
        """
        Save candles to disk
        
        Args:
            pair: Trading pair
            timeframe: Timeframe (1m, 5m, 1h, etc.)
            candles: List of candles
        """
        filename = self._get_filename(pair, timeframe)
        filepath = os.path.join(self.data_dir, filename)
        
        # Convert candles to dict
        data = {
            'pair': pair,
            'timeframe': timeframe,
            'candles': [self._candle_to_dict(c) for c in candles],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_candles(
        self,
        pair: str,
        timeframe: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Candle]:
        """
        Load candles from disk
        
        Args:
            pair: Trading pair
            timeframe: Timeframe
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of candles
        """
        filename = self._get_filename(pair, timeframe)
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        candles = [self._dict_to_candle(c) for c in data['candles']]
        
        # Apply date filters
        if start_date:
            candles = [c for c in candles if c.timestamp >= start_date]
        if end_date:
            candles = [c for c in candles if c.timestamp <= end_date]
        
        return candles
    
    def get_latest_candles(
        self,
        pair: str,
        timeframe: str,
        count: int = 100
    ) -> List[Candle]:
        """
        Get latest N candles
        
        Args:
            pair: Trading pair
            timeframe: Timeframe
            count: Number of candles
            
        Returns:
            List of latest candles
        """
        candles = self.load_candles(pair, timeframe)
        return candles[-count:] if candles else []
    
    def append_candle(self, pair: str, timeframe: str, candle: Candle):
        """
        Append a new candle to existing data
        
        Args:
            pair: Trading pair
            timeframe: Timeframe
            candle: New candle
        """
        candles = self.load_candles(pair, timeframe)
        candles.append(candle)
        self.save_candles(pair, timeframe, candles)
    
    def get_data_info(self, pair: str, timeframe: str) -> Optional[Dict]:
        """
        Get information about stored data
        
        Args:
            pair: Trading pair
            timeframe: Timeframe
            
        Returns:
            Data info dictionary
        """
        candles = self.load_candles(pair, timeframe)
        
        if not candles:
            return None
        
        return {
            'pair': pair,
            'timeframe': timeframe,
            'candle_count': len(candles),
            'start_date': candles[0].timestamp.isoformat(),
            'end_date': candles[-1].timestamp.isoformat(),
            'data_quality': self._assess_data_quality(candles)
        }
    
    def _assess_data_quality(self, candles: List[Candle]) -> str:
        """Assess data quality"""
        if len(candles) < 100:
            return "Insufficient"
        elif len(candles) < 1000:
            return "Limited"
        else:
            return "Good"
    
    def _get_filename(self, pair: str, timeframe: str) -> str:
        """Generate filename for pair/timeframe"""
        pair_clean = pair.replace('/', '_')
        return f"{pair_clean}_{timeframe}.json"
    
    def _candle_to_dict(self, candle: Candle) -> Dict:
        """Convert candle to dictionary"""
        return {
            'timestamp': candle.timestamp.isoformat(),
            'open': candle.open,
            'high': candle.high,
            'low': candle.low,
            'close': candle.close,
            'volume': candle.volume
        }
    
    def _dict_to_candle(self, data: Dict) -> Candle:
        """Convert dictionary to candle"""
        return Candle(
            timestamp=datetime.fromisoformat(data['timestamp']),
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            volume=data['volume']
        )
