"""
Base Strategy Interface
Abstract base class for all trading strategies
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime, time
from enum import Enum

from backend.models.trading_models import MarketContext, TradingSignal, OrderDirection


class StrategyType(str, Enum):
    """Strategy type enumeration"""
    TREND_FOLLOWING = "TREND_FOLLOWING"
    MEAN_REVERSION = "MEAN_REVERSION"
    BREAKOUT = "BREAKOUT"
    ARBITRAGE = "ARBITRAGE"
    MOMENTUM = "MOMENTUM"


@dataclass
class StrategyResult:
    """Result from strategy analysis"""
    signal: Optional[TradingSignal]
    confidence: float  # 0.0 to 1.0
    reasoning: str
    metadata: Dict[str, Any]  # Additional strategy-specific data
    timestamp: datetime
    
    def __str__(self) -> str:
        if self.signal:
            return (
                f"StrategyResult(signal={self.signal.direction.value}, "
                f"confidence={self.confidence:.2%}, "
                f"reasoning='{self.reasoning[:50]}...')" 
            )
        return f"StrategyResult(signal=None, confidence={self.confidence:.2%})"


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies
    
    All strategies must implement the analyze() method and provide
    configuration for supported pairs, timeframes, and trading hours.
    """
    
    def __init__(self, name: str, strategy_type: StrategyType):
        """
        Initialize base strategy
        
        Args:
            name: Strategy name (e.g., "EMA_Crossover")
            strategy_type: Type of strategy
        """
        self.name = name
        self.strategy_type = strategy_type
        self.enabled = True
        self.last_analysis: Optional[datetime] = None
        
        # Performance tracking
        self.total_signals = 0
        self.successful_signals = 0
        self.total_pnl = 0.0
        
        # Configuration (to be set by subclasses)
        self.supported_pairs: List[str] = []
        self.required_timeframes: List[str] = ["1h", "4h", "1d"]
        self.min_confidence_threshold = 0.6
        
        # Trading hours (UTC)
        self.trading_start = time(0, 0)  # 00:00 UTC
        self.trading_end = time(23, 59)  # 23:59 UTC
        
        print(f"📈 {self.name} strategy initialized")
    
    @abstractmethod
    def analyze(self, context: MarketContext) -> StrategyResult:
        """
        Analyze market context and generate trading signal
        
        Args:
            context: MarketContext with all market data
            
        Returns:
            StrategyResult with signal and analysis details
        """
        pass
    
    def should_trade(self, pair: str, current_time: datetime) -> bool:
        """
        Check if strategy should trade for given pair and time
        
        Args:
            pair: Trading pair (e.g., "EUR/USD")
            current_time: Current datetime
            
        Returns:
            True if strategy should trade
        """
        if pair not in self.supported_pairs:
            return False
        
        if not self.enabled:
            return False
        
        current_time_utc = current_time.time()
        if not (self.trading_start <= current_time_utc <= self.trading_end):
            return False
        
        return True
    
    def validate_context(self, context: MarketContext) -> bool:
        """
        Validate that market context has required data
        
        Args:
            context: MarketContext to validate
            
        Returns:
            True if context is valid for this strategy
        """
        if not context or not context.pair:
            return False
        
        if context.pair not in self.supported_pairs:
            return False
        
        # Check required indicators
        required_indicators = ['rsi_14', 'macd_line', 'bb_upper', 'bb_lower', 'atr_14']
        for indicator in required_indicators:
            if not hasattr(context, indicator) or getattr(context, indicator) is None:
                return False
        
        return True
    
    def record_signal_result(self, success: bool, pnl: float = 0.0) -> None:
        """Record the result of a trading signal"""
        self.total_signals += 1
        if success:
            self.successful_signals += 1
        self.total_pnl += pnl
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get strategy performance metrics"""
        win_rate = (self.successful_signals / self.total_signals) if self.total_signals > 0 else 0.0
        avg_pnl = (self.total_pnl / self.total_signals) if self.total_signals > 0 else 0.0
        
        return {
            'name': self.name,
            'type': self.strategy_type.value,
            'enabled': self.enabled,
            'total_signals': self.total_signals,
            'successful_signals': self.successful_signals,
            'win_rate': win_rate,
            'total_pnl': self.total_pnl,
            'avg_pnl_per_signal': avg_pnl,
            'last_analysis': self.last_analysis.isoformat() if self.last_analysis else None
        }
    
    def enable(self) -> None:
        """Enable the strategy"""
        self.enabled = True
        print(f"✅ {self.name} strategy enabled")
    
    def disable(self) -> None:
        """Disable the strategy"""
        self.enabled = False
        print(f"⏸️ {self.name} strategy disabled")
    
    def __str__(self) -> str:
        return f"{self.name} ({self.strategy_type.value})"
