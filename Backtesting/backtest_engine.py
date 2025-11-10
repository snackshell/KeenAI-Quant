"""
Backtest Execution Engine
Simulates strategy execution on historical data
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Optional
import numpy as np

from backend.models.trading_models import Candle, TradingSignal, Position, OrderDirection
from Strategy_Framework.base_strategy import BaseStrategy
from Backtesting.performance_analyzer import PerformanceAnalyzer, PerformanceMetrics


@dataclass
class BacktestConfig:
    """Backtest configuration"""
    strategy: BaseStrategy
    pair: str
    start_date: date
    end_date: date
    initial_balance: float = 10000.0
    slippage: float = 0.0001  # 1 pip or 0.01%
    commission: float = 0.0002  # 2 pips or 0.02%
    latency_ms: int = 100  # Execution delay


@dataclass
class Trade:
    """Simulated trade"""
    entry_time: datetime
    exit_time: Optional[datetime]
    pair: str
    direction: OrderDirection
    entry_price: float
    exit_price: Optional[float]
    size: float
    pnl: Optional[float]
    commission: float
    slippage: float


@dataclass
class BacktestResult:
    """Backtest results"""
    config: BacktestConfig
    trades: List[Trade]
    equity_curve: List[float]
    timestamps: List[datetime]
    performance: PerformanceMetrics
    final_balance: float
    total_return: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'pair': self.config.pair,
            'start_date': self.config.start_date.isoformat(),
            'end_date': self.config.end_date.isoformat(),
            'initial_balance': self.config.initial_balance,
            'final_balance': self.final_balance,
            'total_return': self.total_return,
            'total_trades': len(self.trades),
            'performance': {
                'sharpe_ratio': self.performance.sharpe_ratio,
                'max_drawdown': self.performance.max_drawdown,
                'win_rate': self.performance.win_rate,
                'profit_factor': self.performance.profit_factor,
                'avg_win': self.performance.avg_win,
                'avg_loss': self.performance.avg_loss
            }
        }


class BacktestEngine:
    """
    Backtest Execution Engine
    
    Simulates strategy execution on historical data with:
    - Realistic order execution (slippage, commission, latency)
    - Position tracking and P&L calculation
    - Performance metrics generation
    """
    
    def __init__(self):
        """Initialize backtest engine"""
        self.analyzer = PerformanceAnalyzer()
        print("📊 Backtest Engine initialized")
    
    def run(self, config: BacktestConfig, historical_data: List[Candle]) -> BacktestResult:
        """
        Run backtest on historical data
        
        Args:
            config: Backtest configuration
            historical_data: List of historical candles
            
        Returns:
            BacktestResult with trades and performance metrics
        """
        print(f"\n🔄 Running backtest for {config.pair}")
        print(f"   Period: {config.start_date} to {config.end_date}")
        print(f"   Strategy: {config.strategy.name}")
        print(f"   Initial Balance: ${config.initial_balance:,.2f}")
        
        # Initialize tracking
        balance = config.initial_balance
        equity_curve = [balance]
        timestamps = [historical_data[0].timestamp]
        trades: List[Trade] = []
        current_position: Optional[Position] = None
        
        # Simulate trading
        for i, candle in enumerate(historical_data):
            # Build simple context (in real backtest, use full context builder)
            from backend.models.trading_models import MarketContext
            
            # Skip if not enough data for indicators
            if i < 50:
                continue
            
            # Simple context (would use full context builder in production)
            context = MarketContext(
                pair=config.pair,
                current_price=candle.close,
                indicators={
                    'rsi_14': 50.0,
                    'macd': 0.0,
                    'macd_signal': 0.0,
                    'macd_histogram': 0.0,
                    'bb_upper': candle.close * 1.02,
                    'bb_middle': candle.close,
                    'bb_lower': candle.close * 0.98,
                    'atr_14': candle.close * 0.01,
                    'adx_14': 25.0,
                    'ema_9': candle.close,
                    'ema_21': candle.close,
                    'ema_55': candle.close,
                },
                recent_candles=historical_data[max(0, i-50):i+1],
                current_positions=[],
                account_balance=balance,
                market_regime="ranging",
                timestamp=candle.timestamp
            )
            
            # Get strategy signal
            if config.strategy.should_trade(config.pair, candle.timestamp):
                result = config.strategy.analyze(context)
                
                if result.signal and result.confidence >= config.strategy.min_confidence_threshold:
                    signal = result.signal
                    
                    # Close existing position if opposite direction
                    if current_position and current_position.direction != signal.direction:
                        trade = self._close_position(
                            current_position,
                            candle.close,
                            candle.timestamp,
                            config
                        )
                        trades.append(trade)
                        balance += trade.pnl
                        current_position = None
                    
                    # Open new position if no position
                    if not current_position:
                        current_position = self._open_position(
                            signal,
                            candle.close,
                            candle.timestamp,
                            balance,
                            config
                        )
            
            # Check stop-loss and take-profit
            if current_position:
                if current_position.direction == OrderDirection.BUY:
                    if candle.low <= current_position.stop_loss:
                        # Stop-loss hit
                        trade = self._close_position(
                            current_position,
                            current_position.stop_loss,
                            candle.timestamp,
                            config
                        )
                        trades.append(trade)
                        balance += trade.pnl
                        current_position = None
                    elif candle.high >= current_position.take_profit:
                        # Take-profit hit
                        trade = self._close_position(
                            current_position,
                            current_position.take_profit,
                            candle.timestamp,
                            config
                        )
                        trades.append(trade)
                        balance += trade.pnl
                        current_position = None
                else:  # SELL
                    if candle.high >= current_position.stop_loss:
                        trade = self._close_position(
                            current_position,
                            current_position.stop_loss,
                            candle.timestamp,
                            config
                        )
                        trades.append(trade)
                        balance += trade.pnl
                        current_position = None
                    elif candle.low <= current_position.take_profit:
                        trade = self._close_position(
                            current_position,
                            current_position.take_profit,
                            candle.timestamp,
                            config
                        )
                        trades.append(trade)
                        balance += trade.pnl
                        current_position = None
            
            # Update equity curve
            current_equity = balance
            if current_position:
                # Add unrealized P&L
                if current_position.direction == OrderDirection.BUY:
                    unrealized = (candle.close - current_position.entry_price) * current_position.size
                else:
                    unrealized = (current_position.entry_price - candle.close) * current_position.size
                current_equity += unrealized
            
            equity_curve.append(current_equity)
            timestamps.append(candle.timestamp)
        
        # Close any remaining position
        if current_position:
            trade = self._close_position(
                current_position,
                historical_data[-1].close,
                historical_data[-1].timestamp,
                config
            )
            trades.append(trade)
            balance += trade.pnl
        
        # Calculate performance metrics
        performance = self.analyzer.calculate_metrics(trades, equity_curve, config.initial_balance)
        
        # Create result
        result = BacktestResult(
            config=config,
            trades=trades,
            equity_curve=equity_curve,
            timestamps=timestamps,
            performance=performance,
            final_balance=balance,
            total_return=((balance - config.initial_balance) / config.initial_balance) * 100
        )
        
        print(f"\n✅ Backtest Complete")
        print(f"   Final Balance: ${result.final_balance:,.2f}")
        print(f"   Total Return: {result.total_return:.2f}%")
        print(f"   Total Trades: {len(trades)}")
        print(f"   Win Rate: {performance.win_rate:.2%}")
        print(f"   Sharpe Ratio: {performance.sharpe_ratio:.2f}")
        print(f"   Max Drawdown: {performance.max_drawdown:.2%}")
        
        return result
    
    def _open_position(
        self,
        signal: TradingSignal,
        current_price: float,
        timestamp: datetime,
        balance: float,
        config: BacktestConfig
    ) -> Position:
        """Open a new position"""
        # Apply slippage
        if signal.direction == OrderDirection.BUY:
            entry_price = current_price * (1 + config.slippage)
        else:
            entry_price = current_price * (1 - config.slippage)
        
        # Calculate position size (2% risk per trade)
        risk_amount = balance * 0.02
        stop_distance = abs(entry_price - signal.stop_loss)
        size = risk_amount / stop_distance if stop_distance > 0 else 0.01
        
        # Create position
        position = Position(
            position_id=f"backtest_{timestamp.timestamp()}",
            pair=signal.pair,
            direction=signal.direction,
            size=size,
            entry_price=entry_price,
            current_price=entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            unrealized_pnl=0.0,
            opened_at=timestamp
        )
        
        return position
    
    def _close_position(
        self,
        position: Position,
        exit_price: float,
        timestamp: datetime,
        config: BacktestConfig
    ) -> Trade:
        """Close a position and create trade record"""
        # Apply slippage
        if position.direction == OrderDirection.BUY:
            actual_exit = exit_price * (1 - config.slippage)
        else:
            actual_exit = exit_price * (1 + config.slippage)
        
        # Calculate P&L
        if position.direction == OrderDirection.BUY:
            pnl = (actual_exit - position.entry_price) * position.size
        else:
            pnl = (position.entry_price - actual_exit) * position.size
        
        # Apply commission
        commission = (position.entry_price + actual_exit) * position.size * config.commission
        pnl -= commission
        
        # Create trade record
        trade = Trade(
            entry_time=position.opened_at,
            exit_time=timestamp,
            pair=position.pair,
            direction=position.direction,
            entry_price=position.entry_price,
            exit_price=actual_exit,
            size=position.size,
            pnl=pnl,
            commission=commission,
            slippage=config.slippage
        )
        
        return trade
