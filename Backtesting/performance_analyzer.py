"""
Performance Metrics Calculator
Calculates comprehensive trading performance metrics
"""

from dataclasses import dataclass
from typing import List
import numpy as np


@dataclass
class PerformanceMetrics:
    """Trading performance metrics"""
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    largest_win: float
    largest_loss: float
    avg_trade_duration: float  # in hours
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'total_return': self.total_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'largest_win': self.largest_win,
            'largest_loss': self.largest_loss,
            'avg_trade_duration': self.avg_trade_duration
        }


class PerformanceAnalyzer:
    """
    Performance Metrics Calculator
    
    Calculates comprehensive trading performance metrics including:
    - Total return and Sharpe ratio
    - Maximum drawdown
    - Win rate and profit factor
    - Average win/loss and trade statistics
    """
    
    def calculate_metrics(
        self,
        trades: List,
        equity_curve: List[float],
        initial_balance: float
    ) -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics
        
        Args:
            trades: List of Trade objects
            equity_curve: List of equity values over time
            initial_balance: Starting balance
            
        Returns:
            PerformanceMetrics object
        """
        if not trades:
            return PerformanceMetrics(
                total_return=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                win_rate=0.0,
                profit_factor=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                largest_win=0.0,
                largest_loss=0.0,
                avg_trade_duration=0.0
            )
        
        # Calculate returns
        returns = np.diff(equity_curve) / equity_curve[:-1]
        total_return = ((equity_curve[-1] - initial_balance) / initial_balance) * 100
        
        # Calculate Sharpe Ratio (annualized, assuming daily data)
        if len(returns) > 1 and np.std(returns) > 0:
            sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252)
        else:
            sharpe_ratio = 0.0
        
        # Calculate Maximum Drawdown
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        
        # Analyze trades
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        win_rate = len(winning_trades) / len(trades) if trades else 0.0
        
        # Calculate profit factor
        total_wins = sum(t.pnl for t in winning_trades)
        total_losses = abs(sum(t.pnl for t in losing_trades))
        profit_factor = total_wins / total_losses if total_losses > 0 else 0.0
        
        # Average win/loss
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0.0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0.0
        
        # Largest win/loss
        largest_win = max([t.pnl for t in winning_trades]) if winning_trades else 0.0
        largest_loss = min([t.pnl for t in losing_trades]) if losing_trades else 0.0
        
        # Average trade duration
        durations = [(t.exit_time - t.entry_time).total_seconds() / 3600 for t in trades if t.exit_time]
        avg_trade_duration = np.mean(durations) if durations else 0.0
        
        return PerformanceMetrics(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            total_trades=len(trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            largest_win=largest_win,
            largest_loss=largest_loss,
            avg_trade_duration=avg_trade_duration
        )
    
    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """
        Calculate maximum drawdown from equity curve
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            Maximum drawdown as percentage
        """
        if len(equity_curve) < 2:
            return 0.0
        
        equity_array = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max
        max_drawdown = abs(np.min(drawdown)) * 100
        
        return max_drawdown
    
    def generate_trade_report(self, trades: List) -> str:
        """
        Generate detailed trade-by-trade report
        
        Args:
            trades: List of Trade objects
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("="*80)
        report.append("TRADE-BY-TRADE REPORT")
        report.append("="*80)
        report.append("")
        
        for i, trade in enumerate(trades, 1):
            report.append(f"Trade #{i}")
            report.append(f"  Pair: {trade.pair}")
            report.append(f"  Direction: {trade.direction.value}")
            report.append(f"  Entry: {trade.entry_time} @ ${trade.entry_price:.5f}")
            report.append(f"  Exit: {trade.exit_time} @ ${trade.exit_price:.5f}")
            report.append(f"  Size: {trade.size:.4f}")
            report.append(f"  P&L: ${trade.pnl:.2f}")
            report.append(f"  Commission: ${trade.commission:.2f}")
            report.append("")
        
        report.append("="*80)
        
        return "\n".join(report)
