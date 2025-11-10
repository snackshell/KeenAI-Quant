"""
MT5 Data Fetcher
Fetches real historical and live data from MetaTrader 5
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from backend.models.trading_models import Candle

logger = logging.getLogger(__name__)


class MT5DataFetcher:
    """Fetch market data from MT5"""
    
    def __init__(self):
        self.mt5_client = None
        self._initialize_mt5()
    
    def _initialize_mt5(self):
        """Initialize MT5 client"""
        try:
            from Broker_Integration.mt5_client import mt5_client
            self.mt5_client = mt5_client
            logger.info("MT5 data fetcher initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MT5 client: {e}")
    
    def _map_symbol(self, pair: str) -> str:
        """Map trading pair to MT5 symbol"""
        # Map common pairs to MT5 symbols
        symbol_map = {
            'EUR/USD': 'EURUSD',
            'XAU/USD': 'XAUUSD',
            'BTC/USD': 'BTCUSD',
            'ETH/USD': 'ETHUSD',
        }
        return symbol_map.get(pair, pair.replace('/', ''))
    
    def _map_timeframe(self, timeframe: str):
        """Map timeframe string to MT5 timeframe constant"""
        if not self.mt5_client or not self.mt5_client.mt5:
            return None
        
        mt5 = self.mt5_client.mt5
        timeframe_map = {
            '1m': mt5.TIMEFRAME_M1,
            '5m': mt5.TIMEFRAME_M5,
            '15m': mt5.TIMEFRAME_M15,
            '30m': mt5.TIMEFRAME_M30,
            '1h': mt5.TIMEFRAME_H1,
            '4h': mt5.TIMEFRAME_H4,
            '1d': mt5.TIMEFRAME_D1,
        }
        return timeframe_map.get(timeframe)
    
    def fetch_historical_data(
        self,
        pair: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Candle]:
        """
        Fetch historical candle data from MT5
        
        Args:
            pair: Trading pair (e.g., 'EUR/USD')
            timeframe: Timeframe (e.g., '1h', '5m')
            start_date: Start date
            end_date: End date
            
        Returns:
            List of Candle objects
        """
        if not self.mt5_client:
            logger.error("MT5 client not initialized")
            return []
        
        if not self.mt5_client.connected:
            if not self.mt5_client.connect():
                logger.error("Failed to connect to MT5")
                return []
        
        try:
            symbol = self._map_symbol(pair)
            mt5_timeframe = self._map_timeframe(timeframe)
            
            if not mt5_timeframe:
                logger.error(f"Invalid timeframe: {timeframe}")
                return []
            
            # Fetch rates from MT5
            rates = self.mt5_client.mt5.copy_rates_range(
                symbol,
                mt5_timeframe,
                start_date,
                end_date
            )
            
            if rates is None or len(rates) == 0:
                logger.warning(f"No data returned for {pair} {timeframe}")
                return []
            
            # Convert to Candle objects
            candles = []
            for rate in rates:
                candle = Candle(
                    pair=pair,
                    timestamp=datetime.fromtimestamp(rate['time']),
                    timeframe=timeframe,
                    open=float(rate['open']),
                    high=float(rate['high']),
                    low=float(rate['low']),
                    close=float(rate['close']),
                    volume=float(rate['tick_volume'])
                )
                candles.append(candle)
            
            logger.info(f"Fetched {len(candles)} candles for {pair} {timeframe}")
            return candles
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return []
    
    def fetch_recent_candles(
        self,
        pair: str,
        timeframe: str,
        count: int = 100
    ) -> List[Candle]:
        """
        Fetch recent candles from MT5
        
        Args:
            pair: Trading pair
            timeframe: Timeframe
            count: Number of candles to fetch
            
        Returns:
            List of recent Candle objects
        """
        if not self.mt5_client:
            logger.error("MT5 client not initialized")
            return []
        
        if not self.mt5_client.connected:
            if not self.mt5_client.connect():
                logger.error("Failed to connect to MT5")
                return []
        
        try:
            symbol = self._map_symbol(pair)
            mt5_timeframe = self._map_timeframe(timeframe)
            
            if not mt5_timeframe:
                logger.error(f"Invalid timeframe: {timeframe}")
                return []
            
            # Fetch recent rates
            rates = self.mt5_client.mt5.copy_rates_from_pos(
                symbol,
                mt5_timeframe,
                0,  # Start from current
                count
            )
            
            if rates is None or len(rates) == 0:
                logger.warning(f"No data returned for {pair} {timeframe}")
                return []
            
            # Convert to Candle objects
            candles = []
            for rate in rates:
                candle = Candle(
                    pair=pair,
                    timestamp=datetime.fromtimestamp(rate['time']),
                    timeframe=timeframe,
                    open=float(rate['open']),
                    high=float(rate['high']),
                    low=float(rate['low']),
                    close=float(rate['close']),
                    volume=float(rate['tick_volume'])
                )
                candles.append(candle)
            
            return candles
            
        except Exception as e:
            logger.error(f"Error fetching recent candles: {e}")
            return []
    
    def get_current_price(self, pair: str) -> Optional[float]:
        """Get current price for a pair"""
        if not self.mt5_client:
            return None
        
        if not self.mt5_client.connected:
            if not self.mt5_client.connect():
                return None
        
        try:
            symbol = self._map_symbol(pair)
            tick = self.mt5_client.mt5.symbol_info_tick(symbol)
            
            if tick:
                return float(tick.bid)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            return None


# Global instance
mt5_data_fetcher = MT5DataFetcher()
