"""
Database Access Layer (DAL) for KeenAI-Quant
Provides CRUD operations and common queries
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func

from .schema import (
    HistoricalCandle, Trade, AIDecision, AgentPerformance,
    SystemLog, StrategyPerformance, RiskEvent, BacktestResult
)
from backend.models.trading_models import Candle, AgentPrediction


class CandleDAL:
    """Data access for historical candles"""
    
    @staticmethod
    def insert_candle(session: Session, candle: Candle) -> HistoricalCandle:
        """Insert a single candle"""
        db_candle = HistoricalCandle(
            pair=candle.pair,
            timeframe=candle.timeframe,
            timestamp=candle.timestamp,
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            volume=candle.volume
        )
        session.add(db_candle)
        session.commit()
        return db_candle
    
    @staticmethod
    def get_recent_candles(
        session: Session,
        pair: str,
        timeframe: str,
        limit: int = 1000
    ) -> List[HistoricalCandle]:
        """Get most recent candles for a pair/timeframe"""
        return session.query(HistoricalCandle).filter(
            and_(
                HistoricalCandle.pair == pair,
                HistoricalCandle.timeframe == timeframe
            )
        ).order_by(desc(HistoricalCandle.timestamp)).limit(limit).all()
    
    @staticmethod
    def get_candles_range(
        session: Session,
        pair: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[HistoricalCandle]:
        """Get candles within a date range"""
        return session.query(HistoricalCandle).filter(
            and_(
                HistoricalCandle.pair == pair,
                HistoricalCandle.timeframe == timeframe,
                HistoricalCandle.timestamp >= start_date,
                HistoricalCandle.timestamp <= end_date
            )
        ).order_by(HistoricalCandle.timestamp).all()


class TradeDAL:
    """Data access for trades"""
    
    @staticmethod
    def insert_trade(session: Session, trade_data: Dict[str, Any]) -> Trade:
        """Insert a new trade"""
        trade = Trade(**trade_data)
        session.add(trade)
        session.commit()
        return trade
    
    @staticmethod
    def update_trade(session: Session, trade_id: str, updates: Dict[str, Any]) -> Optional[Trade]:
        """Update an existing trade"""
        trade = session.query(Trade).filter(Trade.trade_id == trade_id).first()
        if trade:
            for key, value in updates.items():
                setattr(trade, key, value)
            session.commit()
        return trade
    
    @staticmethod
    def get_open_trades(session: Session, pair: Optional[str] = None) -> List[Trade]:
        """Get all open trades, optionally filtered by pair"""
        query = session.query(Trade).filter(Trade.status == 'OPEN')
        if pair:
            query = query.filter(Trade.pair == pair)
        return query.all()
    
    @staticmethod
    def get_trades_today(session: Session) -> List[Trade]:
        """Get all trades from today"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return session.query(Trade).filter(
            Trade.opened_at >= today_start
        ).all()
    
    @staticmethod
    def get_trade_history(
        session: Session,
        pair: Optional[str] = None,
        days: int = 30
    ) -> List[Trade]:
        """Get trade history for specified days"""
        start_date = datetime.now() - timedelta(days=days)
        query = session.query(Trade).filter(Trade.opened_at >= start_date)
        if pair:
            query = query.filter(Trade.pair == pair)
        return query.order_by(desc(Trade.opened_at)).all()


class AIDecisionDAL:
    """Data access for AI decisions"""
    
    @staticmethod
    def log_decision(
        session: Session,
        pair: str,
        agent_name: str,
        prediction: AgentPrediction,
        ensemble_decision: Optional[str] = None,
        ensemble_confidence: Optional[float] = None
    ) -> AIDecision:
        """Log an AI agent decision"""
        decision = AIDecision(
            timestamp=prediction.timestamp,
            pair=pair,
            agent_name=agent_name,
            signal=prediction.signal.value,
            confidence=prediction.confidence,
            reasoning=prediction.reasoning,
            ensemble_decision=ensemble_decision,
            ensemble_confidence=ensemble_confidence
        )
        session.add(decision)
        session.commit()
        return decision
    
    @staticmethod
    def get_recent_decisions(
        session: Session,
        agent_name: Optional[str] = None,
        hours: int = 24
    ) -> List[AIDecision]:
        """Get recent AI decisions"""
        start_time = datetime.now() - timedelta(hours=hours)
        query = session.query(AIDecision).filter(AIDecision.timestamp >= start_time)
        if agent_name:
            query = query.filter(AIDecision.agent_name == agent_name)
        return query.order_by(desc(AIDecision.timestamp)).all()


class AgentPerformanceDAL:
    """Data access for agent performance metrics"""
    
    @staticmethod
    def update_performance(
        session: Session,
        agent_name: str,
        metrics: Dict[str, Any]
    ) -> AgentPerformance:
        """Update or create agent performance record"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        perf = session.query(AgentPerformance).filter(
            and_(
                AgentPerformance.agent_name == agent_name,
                AgentPerformance.date == today
            )
        ).first()
        
        if perf:
            for key, value in metrics.items():
                setattr(perf, key, value)
        else:
            perf = AgentPerformance(
                agent_name=agent_name,
                date=today,
                **metrics
            )
            session.add(perf)
        
        session.commit()
        return perf
    
    @staticmethod
    def get_agent_performance(
        session: Session,
        agent_name: str,
        days: int = 30
    ) -> List[AgentPerformance]:
        """Get agent performance history"""
        start_date = datetime.now() - timedelta(days=days)
        return session.query(AgentPerformance).filter(
            and_(
                AgentPerformance.agent_name == agent_name,
                AgentPerformance.date >= start_date
            )
        ).order_by(AgentPerformance.date).all()


class SystemLogDAL:
    """Data access for system logs"""
    
    @staticmethod
    def log(
        session: Session,
        level: str,
        category: str,
        message: str,
        details: Optional[Dict] = None
    ) -> SystemLog:
        """Create a system log entry"""
        log = SystemLog(
            timestamp=datetime.now(),
            level=level,
            category=category,
            message=message,
            details=details
        )
        session.add(log)
        session.commit()
        return log
    
    @staticmethod
    def get_logs(
        session: Session,
        level: Optional[str] = None,
        category: Optional[str] = None,
        hours: int = 24,
        limit: int = 1000
    ) -> List[SystemLog]:
        """Get system logs with filters"""
        start_time = datetime.now() - timedelta(hours=hours)
        query = session.query(SystemLog).filter(SystemLog.timestamp >= start_time)
        
        if level:
            query = query.filter(SystemLog.level == level)
        if category:
            query = query.filter(SystemLog.category == category)
        
        return query.order_by(desc(SystemLog.timestamp)).limit(limit).all()


class StrategyPerformanceDAL:
    """Data access for strategy performance"""
    
    @staticmethod
    def update_performance(
        session: Session,
        strategy_name: str,
        pair: str,
        metrics: Dict[str, Any]
    ) -> StrategyPerformance:
        """Update or create strategy performance record"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        perf = session.query(StrategyPerformance).filter(
            and_(
                StrategyPerformance.strategy_name == strategy_name,
                StrategyPerformance.pair == pair,
                StrategyPerformance.date == today
            )
        ).first()
        
        if perf:
            for key, value in metrics.items():
                setattr(perf, key, value)
        else:
            perf = StrategyPerformance(
                strategy_name=strategy_name,
                pair=pair,
                date=today,
                **metrics
            )
            session.add(perf)
        
        session.commit()
        return perf
    
    @staticmethod
    def get_strategy_performance(
        session: Session,
        strategy_name: str,
        pair: Optional[str] = None,
        days: int = 30
    ) -> List[StrategyPerformance]:
        """Get strategy performance history"""
        start_date = datetime.now() - timedelta(days=days)
        query = session.query(StrategyPerformance).filter(
            and_(
                StrategyPerformance.strategy_name == strategy_name,
                StrategyPerformance.date >= start_date
            )
        )
        if pair:
            query = query.filter(StrategyPerformance.pair == pair)
        
        return query.order_by(StrategyPerformance.date).all()


class RiskEventDAL:
    """Data access for risk events"""
    
    @staticmethod
    def log_event(
        session: Session,
        event_type: str,
        description: str,
        pair: Optional[str] = None,
        details: Optional[Dict] = None
    ) -> RiskEvent:
        """Log a risk management event"""
        event = RiskEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            pair=pair,
            description=description,
            details=details
        )
        session.add(event)
        session.commit()
        return event
    
    @staticmethod
    def get_unresolved_events(session: Session) -> List[RiskEvent]:
        """Get all unresolved risk events"""
        return session.query(RiskEvent).filter(
            RiskEvent.resolved == False
        ).order_by(desc(RiskEvent.timestamp)).all()
    
    @staticmethod
    def resolve_event(session: Session, event_id: int) -> Optional[RiskEvent]:
        """Mark a risk event as resolved"""
        event = session.query(RiskEvent).filter(RiskEvent.id == event_id).first()
        if event:
            event.resolved = True
            event.resolved_at = datetime.now()
            session.commit()
        return event


class BacktestDAL:
    """Data access for backtest results"""
    
    @staticmethod
    def save_result(session: Session, result_data: Dict[str, Any]) -> BacktestResult:
        """Save backtest result"""
        result = BacktestResult(**result_data)
        session.add(result)
        session.commit()
        return result
    
    @staticmethod
    def get_results(
        session: Session,
        strategy_name: Optional[str] = None,
        limit: int = 50
    ) -> List[BacktestResult]:
        """Get backtest results"""
        query = session.query(BacktestResult)
        if strategy_name:
            query = query.filter(BacktestResult.strategy_name == strategy_name)
        
        return query.order_by(desc(BacktestResult.created_at)).limit(limit).all()
