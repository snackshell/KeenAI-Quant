"""
SQLAlchemy database schema for KeenAI-Quant
Following OpenAlgo's database patterns
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text, JSON,
    ForeignKey, Index, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()


class HistoricalCandle(Base):
    """Historical OHLCV candle data"""
    __tablename__ = 'historical_candles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pair = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(5), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    __table_args__ = (
        Index('idx_pair_timeframe_timestamp', 'pair', 'timeframe', 'timestamp', unique=True),
    )
    
    def __repr__(self):
        return f"<Candle {self.pair} {self.timeframe} {self.timestamp}>"


class Trade(Base):
    """Trade execution records"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(String(50), unique=True, nullable=False, index=True)
    pair = Column(String(20), nullable=False, index=True)
    direction = Column(String(4), nullable=False)  # BUY/SELL
    size = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    pnl = Column(Float)
    opened_at = Column(DateTime, nullable=False, index=True)
    closed_at = Column(DateTime)
    reason = Column(Text)  # Why the trade was taken
    status = Column(String(20), nullable=False)  # OPEN, CLOSED, CANCELLED
    
    __table_args__ = (
        Index('idx_pair_opened', 'pair', 'opened_at'),
    )
    
    def __repr__(self):
        return f"<Trade {self.trade_id} {self.pair} {self.direction}>"


class AIDecision(Base):
    """AI agent decision logs"""
    __tablename__ = 'ai_decisions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    pair = Column(String(20), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False, index=True)
    signal = Column(String(10), nullable=False)  # BUY/SELL/HOLD
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text)
    ensemble_decision = Column(String(10))  # Final ensemble decision
    ensemble_confidence = Column(Float)
    
    __table_args__ = (
        Index('idx_timestamp_pair', 'timestamp', 'pair'),
        Index('idx_agent_timestamp', 'agent_name', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AIDecision {self.agent_name} {self.pair} {self.signal}>"


class AgentPerformance(Base):
    """AI agent performance metrics"""
    __tablename__ = 'agent_performance'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(50), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    total_signals = Column(Integer, default=0)
    correct_signals = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    avg_confidence = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    current_weight = Column(Float, default=1.0)
    
    __table_args__ = (
        Index('idx_agent_date', 'agent_name', 'date', unique=True),
    )
    
    def __repr__(self):
        return f"<AgentPerformance {self.agent_name} {self.date}>"


class SystemLog(Base):
    """System event logs"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    level = Column(String(10), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR
    category = Column(String(50), nullable=False, index=True)  # TRADE, AI, RISK, SYSTEM
    message = Column(Text, nullable=False)
    details = Column(JSON)  # Additional structured data
    
    __table_args__ = (
        Index('idx_timestamp_level', 'timestamp', 'level'),
        Index('idx_category_timestamp', 'category', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SystemLog {self.level} {self.category} {self.timestamp}>"


class StrategyPerformance(Base):
    """Strategy performance tracking"""
    __tablename__ = 'strategy_performance'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_name = Column(String(50), nullable=False, index=True)
    pair = Column(String(20), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    avg_win = Column(Float, default=0.0)
    avg_loss = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    
    __table_args__ = (
        Index('idx_strategy_pair_date', 'strategy_name', 'pair', 'date', unique=True),
    )
    
    def __repr__(self):
        return f"<StrategyPerformance {self.strategy_name} {self.pair}>"


class RiskEvent(Base):
    """Risk management events"""
    __tablename__ = 'risk_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # CIRCUIT_BREAKER, POSITION_REJECTED, etc.
    pair = Column(String(20))
    description = Column(Text, nullable=False)
    details = Column(JSON)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_timestamp_type', 'timestamp', 'event_type'),
    )
    
    def __repr__(self):
        return f"<RiskEvent {self.event_type} {self.timestamp}>"


class BacktestResult(Base):
    """Backtest execution results"""
    __tablename__ = 'backtest_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    backtest_id = Column(String(50), unique=True, nullable=False, index=True)
    strategy_name = Column(String(50), nullable=False, index=True)
    pair = Column(String(20), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_balance = Column(Float, nullable=False)
    final_balance = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    total_trades = Column(Integer, nullable=False)
    winning_trades = Column(Integer, nullable=False)
    losing_trades = Column(Integer, nullable=False)
    win_rate = Column(Float, nullable=False)
    profit_factor = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    avg_trade_duration = Column(Float)  # in hours
    created_at = Column(DateTime, default=datetime.now)
    config = Column(JSON)  # Backtest configuration
    
    __table_args__ = (
        Index('idx_strategy_created', 'strategy_name', 'created_at'),
    )
    
    def __repr__(self):
        return f"<BacktestResult {self.backtest_id} {self.strategy_name}>"


# Database connection and session management
class Database:
    """Database manager"""
    
    def __init__(self, db_url: str = "sqlite:///./data/keenai.db"):
        self.engine = create_engine(
            db_url,
            echo=False,  # Set to True for SQL debugging
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True  # Verify connections before using
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def init_db(self):
        """Initialize database with tables and indexes"""
        self.create_tables()
        print("✅ Database tables created successfully")
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        print(f"📊 Created {len(tables)} tables: {', '.join(tables)}")


# Global database instance
db = Database()
