"""
Event System for KeenAI-Quant Backend
Pub/Sub event handling for system-wide notifications
"""

from typing import Callable, Dict, List, Any
from datetime import datetime
from enum import Enum
import asyncio


class EventType(Enum):
    """System event types"""
    # Trading Events
    TRADE_OPENED = "trade_opened"
    TRADE_CLOSED = "trade_closed"
    TRADE_MODIFIED = "trade_modified"
    
    # Signal Events
    SIGNAL_GENERATED = "signal_generated"
    SIGNAL_EXECUTED = "signal_executed"
    
    # Risk Events
    RISK_LIMIT_REACHED = "risk_limit_reached"
    CIRCUIT_BREAKER_TRIGGERED = "circuit_breaker_triggered"
    
    # System Events
    SYSTEM_STARTED = "system_started"
    SYSTEM_STOPPED = "system_stopped"
    ERROR_OCCURRED = "error_occurred"
    
    # Market Events
    MARKET_DATA_UPDATED = "market_data_updated"
    PRICE_ALERT = "price_alert"


class Event:
    """Event object containing event data"""
    
    def __init__(self, event_type: EventType, data: Dict[str, Any]):
        self.type = event_type
        self.data = data
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'type': self.type.value,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }


class EventBus:
    """
    Event bus for pub/sub messaging
    Allows components to communicate without tight coupling
    """
    
    def __init__(self):
        """Initialize event bus"""
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """
        Subscribe to an event type
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """
        Unsubscribe from an event type
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
        """
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
    
    async def publish(self, event_type: EventType, data: Dict[str, Any]):
        """
        Publish an event
        
        Args:
            event_type: Type of event
            data: Event data
        """
        event = Event(event_type, data)
        
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Notify subscribers
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    print(f"Error in event callback: {e}")
    
    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """
        Get event history
        
        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        return events[-limit:]


# Global event bus instance
event_bus = EventBus()
