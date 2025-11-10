"""
Real-time Data Feeds for KeenAI-Quant
Manages real-time market data streaming
"""

from typing import Dict, Callable, Optional, List
from datetime import datetime
import asyncio
from backend.models.trading_models import Tick, Candle


class RealtimeDataFeed:
    """
    Manages real-time market data feeds
    Provides tick and candle data streaming
    """
    
    def __init__(self):
        """Initialize realtime data feed"""
        self.subscribers: Dict[str, List[Callable]] = {}
        self.active_pairs: List[str] = []
        self.is_running = False
        self.last_ticks: Dict[str, Tick] = {}
    
    def subscribe(self, pair: str, callback: Callable):
        """
        Subscribe to real-time data for a pair
        
        Args:
            pair: Trading pair
            callback: Callback function to receive updates
        """
        if pair not in self.subscribers:
            self.subscribers[pair] = []
        
        self.subscribers[pair].append(callback)
        
        if pair not in self.active_pairs:
            self.active_pairs.append(pair)
        
        print(f"📡 Subscribed to {pair} real-time data")
    
    def unsubscribe(self, pair: str, callback: Callable):
        """
        Unsubscribe from real-time data
        
        Args:
            pair: Trading pair
            callback: Callback to remove
        """
        if pair in self.subscribers:
            self.subscribers[pair].remove(callback)
            
            if not self.subscribers[pair]:
                del self.subscribers[pair]
                self.active_pairs.remove(pair)
    
    async def start(self):
        """Start real-time data feed"""
        self.is_running = True
        print("📡 Real-time data feed started")
        
        # In production, this would connect to actual data source
        # For now, it's a placeholder
        while self.is_running:
            await asyncio.sleep(1)
    
    def stop(self):
        """Stop real-time data feed"""
        self.is_running = False
        print("📡 Real-time data feed stopped")
    
    async def process_tick(self, tick: Tick):
        """
        Process incoming tick data
        
        Args:
            tick: Tick data
        """
        self.last_ticks[tick.pair] = tick
        
        # Notify subscribers
        if tick.pair in self.subscribers:
            for callback in self.subscribers[tick.pair]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(tick)
                    else:
                        callback(tick)
                except Exception as e:
                    print(f"Error in tick callback: {e}")
    
    async def process_candle(self, candle: Candle, pair: str):
        """
        Process incoming candle data
        
        Args:
            candle: Candle data
            pair: Trading pair
        """
        # Notify subscribers
        if pair in self.subscribers:
            for callback in self.subscribers[pair]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(candle)
                    else:
                        callback(candle)
                except Exception as e:
                    print(f"Error in candle callback: {e}")
    
    def get_last_tick(self, pair: str) -> Optional[Tick]:
        """
        Get last tick for a pair
        
        Args:
            pair: Trading pair
            
        Returns:
            Last tick or None
        """
        return self.last_ticks.get(pair)
    
    def get_active_pairs(self) -> List[str]:
        """Get list of active pairs"""
        return self.active_pairs.copy()
    
    def get_subscriber_count(self, pair: str) -> int:
        """Get number of subscribers for a pair"""
        return len(self.subscribers.get(pair, []))


# Global realtime feed instance
realtime_feed = RealtimeDataFeed()
