"""
Data Acquisition Component for KeenAI-Quant
Connects to MT5 via OpenAlgo and manages real-time data feeds for 4 pairs
Optimized for low memory usage with circular buffers
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from collections import deque
import pandas as pd

# Add openalgo to path
sys.path.append(str(Path(__file__).parent.parent / 'openalgo'))

from backend.models.trading_models import Tick, Candle
from backend.config import config
from backend.database import db, CandleDAL


class CircularBuffer:
    """Memory-efficient circular buffer for candle storage"""
    
    def __init__(self, maxlen: int = 1000):
        self.buffer = deque(maxlen=maxlen)
        self.maxlen = maxlen
    
    def append(self, item: Candle):
        """Add candle to buffer"""
        self.buffer.append(item)
    
    def get_recent(self, n: int = 100) -> List[Candle]:
        """Get n most recent candles"""
        return list(self.buffer)[-n:] if n < len(self.buffer) else list(self.buffer)
    
    def get_all(self) -> List[Candle]:
        """Get all candles in buffer"""
        return list(self.buffer)
    
    def clear(self):
        """Clear buffer"""
        self.buffer.clear()
    
    @property
    def size(self) -> int:
        """Current buffer size"""
        return len(self.buffer)


class DataAcquisition:
    """
    Data acquisition manager for real-time market data
    Uses OpenAlgo for MT5 connectivity
    """
    
    def __init__(self):
        self.pairs = config.trading.pairs
        self.timeframes = config.get('data.timeframes', ['1m', '5m', '15m', '1h', '4h', '1d'])
        self.buffer_size = config.get('performance.max_memory_gb', 4) * 250  # ~250 candles per GB
        
        # Circular buffers for each pair/timeframe combination
        self.buffers: Dict[str, Dict[str, CircularBuffer]] = {}
        for pair in self.pairs:
            self.buffers[pair] = {}
            for tf in self.timeframes:
                self.buffers[pair][tf] = CircularBuffer(maxlen=self.buffer_size)
        
        # Tick aggregation for candle building
        self.tick_buffers: Dict[str, List[Tick]] = {pair: [] for pair in self.pairs}
        
        # Callbacks for new candle events
        self.candle_callbacks: List[Callable] = []
        
        # OpenAlgo client (will be initialized when needed)
        self.openalgo_client = None
        
        # Running state
        self.is_running = False
        
        print(f"✅ DataAcquisition initialized for {len(self.pairs)} pairs, {len(self.timeframes)} timeframes")
        print(f"📊 Buffer size: {self.buffer_size} candles per timeframe")
    
    def initialize_openalgo(self):
        """Initialize OpenAlgo client"""
        try:
            # Import OpenAlgo API
            from openalgo import api as openalgo_api
            
            api_key = config.broker.get('openalgo_api_key')
            host = config.broker.get('openalgo_host', 'http://127.0.0.1:5000')
            
            if not api_key:
                raise ValueError("OpenAlgo API key not configured in .env")
            
            self.openalgo_client = openalgo_api(api_key=api_key, host=host)
            print(f"✅ OpenAlgo client initialized: {host}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize OpenAlgo: {e}")
            return False
    
    def subscribe_pair(self, pair: str) -> bool:
        """
        Subscribe to real-time data for a pair
        Note: OpenAlgo doesn't have direct WebSocket subscription,
        so we'll poll for data at configured intervals
        """
        if pair not in self.pairs:
            print(f"⚠️ Pair {pair} not in configured pairs")
            return False
        
        print(f"📡 Subscribed to {pair}")
        return True
    
    async def fetch_latest_quote(self, pair: str) -> Optional[Tick]:
        """Fetch latest quote from MT5"""
        try:
            from Data_Engine.mt5_data_fetcher import mt5_data_fetcher
            
            # Get current price from MT5
            loop = asyncio.get_event_loop()
            price = await loop.run_in_executor(
                None,
                mt5_data_fetcher.get_current_price,
                pair
            )
            
            if price:
                tick = Tick(
                    pair=pair,
                    timestamp=datetime.now(),
                    bid=price,
                    ask=price * 1.0001,  # Approximate spread
                    volume=0.0
                )
                return tick
            
            return None
            
        except Exception as e:
            print(f"❌ Error fetching quote for {pair}: {e}")
            return None
    
    async def fetch_historical_data(
        self,
        pair: str,
        timeframe: str,
        days: int = 30
    ) -> List[Candle]:
        """
        Fetch historical data from MT5
        Used for initial buffer population and backtesting
        """
        try:
            from Data_Engine.mt5_data_fetcher import mt5_data_fetcher
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch data using MT5
            loop = asyncio.get_event_loop()
            candles = await loop.run_in_executor(
                None,
                mt5_data_fetcher.fetch_historical_data,
                pair,
                timeframe,
                start_date,
                end_date
            )
            
            if candles:
                print(f"📥 Fetched {len(candles)} candles for {pair} {timeframe}")
                return candles
            
            return []
            
        except Exception as e:
            print(f"❌ Error fetching historical data for {pair}: {e}")
            return []
    
    async def populate_buffers(self):
        """Populate buffers with historical data"""
        print("📊 Populating buffers with historical data...")
        
        for pair in self.pairs:
            for timeframe in self.timeframes:
                # Fetch appropriate amount of history based on timeframe
                days_map = {
                    '1m': 5,
                    '5m': 10,
                    '15m': 20,
                    '1h': 30,
                    '4h': 60,
                    '1d': 365
                }
                days = days_map.get(timeframe, 30)
                
                candles = await self.fetch_historical_data(pair, timeframe, days)
                
                # Add to buffer
                for candle in candles:
                    self.buffers[pair][timeframe].append(candle)
                
                # Also save to database for persistence
                session = db.get_session()
                try:
                    for candle in candles[-100:]:  # Save last 100 to DB
                        CandleDAL.insert_candle(session, candle)
                except Exception as e:
                    print(f"⚠️ Error saving candles to DB: {e}")
                finally:
                    session.close()
        
        print("✅ Buffers populated")
    
    def on_tick(self, tick: Tick):
        """
        Process incoming tick data
        Aggregate ticks into candles for different timeframes
        """
        pair = tick.pair
        self.tick_buffers[pair].append(tick)
        
        # Check if we need to close any candles
        # This is a simplified version - in production, use proper time-based aggregation
        current_minute = tick.timestamp.replace(second=0, microsecond=0)
        
        # For now, we'll rely on fetching complete candles from OpenAlgo
        # rather than building from ticks (more reliable)
    
    def get_latest_candle(self, pair: str, timeframe: str) -> Optional[Candle]:
        """Get the most recent candle for a pair/timeframe"""
        buffer = self.buffers.get(pair, {}).get(timeframe)
        if buffer and buffer.size > 0:
            return buffer.get_recent(1)[0]
        return None
    
    def get_recent_candles(self, pair: str, timeframe: str, n: int = 100) -> List[Candle]:
        """Get n most recent candles"""
        buffer = self.buffers.get(pair, {}).get(timeframe)
        if buffer and buffer.size > 0:
            return buffer.get_recent(n)
        
        # If buffer is empty, fetch from MT5
        try:
            from Data_Engine.mt5_data_fetcher import mt5_data_fetcher
            candles = mt5_data_fetcher.fetch_recent_candles(pair, timeframe, n)
            
            # Populate buffer with fetched data
            if candles and buffer:
                for candle in candles:
                    buffer.append(candle)
            
            return candles
        except Exception as e:
            print(f"❌ Error fetching candles: {e}")
            return []
    
    def register_candle_callback(self, callback: Callable):
        """Register callback for new candle events"""
        self.candle_callbacks.append(callback)
    
    async def update_loop(self):
        """Main update loop - fetches latest data at configured intervals"""
        update_frequency = config.trading.update_frequency
        
        while self.is_running:
            try:
                # Fetch latest quotes for all pairs
                for pair in self.pairs:
                    tick = await self.fetch_latest_quote(pair)
                    if tick:
                        self.on_tick(tick)
                
                # Fetch latest candles (more reliable than building from ticks)
                for pair in self.pairs:
                    for timeframe in ['1m', '5m']:  # Only update short timeframes frequently
                        candles = await self.fetch_historical_data(pair, timeframe, days=1)
                        if candles:
                            # Add new candles to buffer
                            latest_in_buffer = self.get_latest_candle(pair, timeframe)
                            for candle in candles:
                                if not latest_in_buffer or candle.timestamp > latest_in_buffer.timestamp:
                                    self.buffers[pair][timeframe].append(candle)
                                    
                                    # Trigger callbacks
                                    for callback in self.candle_callbacks:
                                        try:
                                            await callback(candle)
                                        except Exception as e:
                                            print(f"⚠️ Callback error: {e}")
                
                # Wait for next update
                await asyncio.sleep(update_frequency)
                
            except Exception as e:
                print(f"❌ Error in update loop: {e}")
                await asyncio.sleep(update_frequency)
    
    async def start(self):
        """Start data acquisition"""
        if self.is_running:
            print("⚠️ Data acquisition already running")
            return
        
        print("🚀 Starting data acquisition...")
        
        # Initialize OpenAlgo
        if not self.initialize_openalgo():
            print("❌ Failed to start: OpenAlgo initialization failed")
            return
        
        # Subscribe to all pairs
        for pair in self.pairs:
            self.subscribe_pair(pair)
        
        # Populate buffers with historical data
        await self.populate_buffers()
        
        # Start update loop
        self.is_running = True
        asyncio.create_task(self.update_loop())
        
        print("✅ Data acquisition started")
    
    async def stop(self):
        """Stop data acquisition"""
        print("🛑 Stopping data acquisition...")
        self.is_running = False
        print("✅ Data acquisition stopped")
    
    def get_buffer_stats(self) -> Dict:
        """Get statistics about buffer usage"""
        stats = {}
        total_candles = 0
        
        for pair in self.pairs:
            stats[pair] = {}
            for timeframe in self.timeframes:
                size = self.buffers[pair][timeframe].size
                stats[pair][timeframe] = size
                total_candles += size
        
        # Estimate memory usage (rough estimate: 100 bytes per candle)
        memory_mb = (total_candles * 100) / (1024 * 1024)
        
        stats['total_candles'] = total_candles
        stats['estimated_memory_mb'] = round(memory_mb, 2)
        
        return stats


# Global instance
data_acquisition = DataAcquisition()
