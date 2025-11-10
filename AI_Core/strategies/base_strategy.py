"""
Base Strategy Interface for KeenAI-Quant
All trading strategies inherit from this base class
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime

from backend.models.trading_models import MarketContext, TradingSignal


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies
    Defines the interface that all strategies must implement
    """
    
    def __init__(self, name: str, enabled: bool = True):
        """
        Initialize base strategy
        
        Args:
            name: Strategy name
            enabled: Whether strategy is active
        """
        self.name = name
        self.enabled = enabled
        self.signals_generated = 0
        self.last_signal_time: Optional[datetime] = None
    
    @abstractmethod
    async def analyze(self, context: MarketContext) -> Optional[TradingSignal]:
        """
        Analyze market and generate trading signal
        
        Args:
            context: Market context with all data
            
        Returns:
            TradingSignal or None
        """
        pass
    
    @abstractmethod
    def get_required_indicators(self) -> list[str]:
        """
        Get list of required technical indicators
        
        Returns:
            List of indicator names
        """
        pass
    
    def validate_context(self, context: MarketContext) -> bool:
        """
        Validate that context has required indicators
        
        Args:
            context: Market context
            
        Returns:
            True if valid
        """
        required = self.get_required_indicators()
        return all(ind in context.indicators for ind in required)
    
    def record_signal(self, signal: Optional[TradingSignal]):
        """
        Record signal generation
        
        Args:
            signal: Generated signal
        """
        if signal:
            self.signals_generated += 1
            self.last_signal_time = datetime.now()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get strategy statistics"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'signals_generated': self.signals_generated,
            'last_signal': self.last_signal_time.isoformat() if self.last_signal_time else None
        }
    
    def enable(self):
        """Enable strategy"""
        self.enabled = True
    
    def disable(self):
        """Disable strategy"""
        self.enabled = False
