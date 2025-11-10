"""
Core trading data models for KeenAI-Quant
All models use dataclasses for simplicity and performance
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class OrderDirection(str, Enum):
    """Order direction"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class OrderType(str, Enum):
    """Order type"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(str, Enum):
    """Order status"""
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class Tick:
    """Real-time tick data"""
    pair: str
    timestamp: datetime
    bid: float
    ask: float
    volume: float = 0.0
    
    @property
    def mid_price(self) -> float:
        """Calculate mid price"""
        return (self.bid + self.ask) / 2
    
    @property
    def spread(self) -> float:
        """Calculate spread"""
        return self.ask - self.bid


@dataclass
class Candle:
    """OHLCV candle data"""
    pair: str
    timestamp: datetime
    timeframe: str  # '1m', '5m', '15m', '1h', '4h', '1d'
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def __post_init__(self):
        """Validate candle data"""
        if self.high < max(self.open, self.close):
            raise ValueError(f"High {self.high} must be >= max(open, close)")
        if self.low > min(self.open, self.close):
            raise ValueError(f"Low {self.low} must be <= min(open, close)")
    
    @property
    def is_bullish(self) -> bool:
        """Check if candle is bullish"""
        return self.close > self.open
    
    @property
    def body_size(self) -> float:
        """Calculate candle body size"""
        return abs(self.close - self.open)
    
    @property
    def range_size(self) -> float:
        """Calculate candle range"""
        return self.high - self.low


@dataclass
class TradingSignal:
    """Trading signal from AI or strategy"""
    pair: str
    direction: OrderDirection
    confidence: float  # 0.0 to 1.0
    entry_price: float
    stop_loss: float
    take_profit: float
    size: float
    reasoning: str
    source: str  # 'AI_ENSEMBLE', 'STRATEGY_TREND', etc.
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate signal"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        if self.size <= 0:
            raise ValueError(f"Size must be positive, got {self.size}")
    
    @property
    def risk_reward_ratio(self) -> float:
        """Calculate risk-reward ratio"""
        if self.direction == OrderDirection.BUY:
            risk = self.entry_price - self.stop_loss
            reward = self.take_profit - self.entry_price
        else:  # SELL
            risk = self.stop_loss - self.entry_price
            reward = self.entry_price - self.take_profit
        
        return reward / risk if risk > 0 else 0.0


@dataclass
class Order:
    """Order representation"""
    order_id: str
    pair: str
    direction: OrderDirection
    order_type: OrderType
    size: float
    price: Optional[float] = None  # None for market orders
    stop_loss: float = 0.0
    take_profit: float = 0.0
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    filled_at: Optional[datetime] = None
    filled_price: Optional[float] = None
    filled_size: float = 0.0
    
    @property
    def is_filled(self) -> bool:
        """Check if order is fully filled"""
        return self.status == OrderStatus.FILLED
    
    @property
    def is_active(self) -> bool:
        """Check if order is active"""
        return self.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]


@dataclass
class Position:
    """Open position"""
    position_id: str
    pair: str
    direction: OrderDirection
    size: float
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    unrealized_pnl: float
    opened_at: datetime
    
    @property
    def pnl_percentage(self) -> float:
        """Calculate P&L as percentage"""
        if self.direction == OrderDirection.BUY:
            return ((self.current_price - self.entry_price) / self.entry_price) * 100
        else:  # SELL
            return ((self.entry_price - self.current_price) / self.entry_price) * 100
    
    @property
    def is_profitable(self) -> bool:
        """Check if position is profitable"""
        return self.unrealized_pnl > 0
    
    def update_price(self, new_price: float):
        """Update current price and recalculate P&L"""
        self.current_price = new_price
        if self.direction == OrderDirection.BUY:
            self.unrealized_pnl = (new_price - self.entry_price) * self.size
        else:  # SELL
            self.unrealized_pnl = (self.entry_price - new_price) * self.size


@dataclass
class Account:
    """Account information"""
    balance: float
    equity: float
    margin_used: float
    margin_available: float
    unrealized_pnl: float
    realized_pnl_today: float
    positions: List[Position] = field(default_factory=list)
    
    @property
    def margin_level(self) -> float:
        """Calculate margin level percentage"""
        if self.margin_used > 0:
            return (self.equity / self.margin_used) * 100
        return float('inf')
    
    @property
    def free_margin(self) -> float:
        """Calculate free margin"""
        return self.equity - self.margin_used
    
    @property
    def total_pnl(self) -> float:
        """Calculate total P&L (realized + unrealized)"""
        return self.realized_pnl_today + self.unrealized_pnl


@dataclass
class AgentPrediction:
    """Prediction from a single AI agent"""
    agent_name: str
    signal: OrderDirection
    confidence: float  # 0.0 to 1.0
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate prediction"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")


@dataclass
class EnsembleDecision:
    """Combined decision from multiple AI agents"""
    signal: OrderDirection
    confidence: float  # Weighted average confidence
    agent_votes: Dict[str, AgentPrediction]
    weights_used: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def agreement_score(self) -> float:
        """Calculate how much agents agree (0-1)"""
        if not self.agent_votes:
            return 0.0
        
        # Count votes for the winning signal
        winning_votes = sum(
            1 for pred in self.agent_votes.values()
            if pred.signal == self.signal
        )
        return winning_votes / len(self.agent_votes)
    
    @property
    def participating_agents(self) -> List[str]:
        """Get list of agents that participated"""
        return list(self.agent_votes.keys())


@dataclass
class MarketContext:
    """Market context for AI analysis"""
    pair: str
    current_price: float
    indicators: Dict[str, float]  # RSI, MACD, etc.
    recent_candles: List[Candle]
    current_positions: List[Position]
    account_balance: float
    market_regime: str  # 'trending', 'ranging', 'volatile'
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for AI API calls"""
        return {
            'pair': self.pair,
            'current_price': self.current_price,
            'indicators': self.indicators,
            'candle_count': len(self.recent_candles),
            'latest_candle': {
                'open': self.recent_candles[-1].open if self.recent_candles else None,
                'high': self.recent_candles[-1].high if self.recent_candles else None,
                'low': self.recent_candles[-1].low if self.recent_candles else None,
                'close': self.recent_candles[-1].close if self.recent_candles else None,
            } if self.recent_candles else None,
            'position_count': len(self.current_positions),
            'account_balance': self.account_balance,
            'market_regime': self.market_regime,
            'timestamp': self.timestamp.isoformat()
        }


# Validation helper functions
def validate_price(price: float, name: str = "price") -> None:
    """Validate price is positive"""
    if price <= 0:
        raise ValueError(f"{name} must be positive, got {price}")


def validate_size(size: float) -> None:
    """Validate position size is positive"""
    if size <= 0:
        raise ValueError(f"Size must be positive, got {size}")


def validate_pair(pair: str, valid_pairs: List[str]) -> None:
    """Validate trading pair"""
    if pair not in valid_pairs:
        raise ValueError(f"Invalid pair {pair}. Must be one of {valid_pairs}")
