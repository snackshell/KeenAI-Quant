"""
Monte Carlo Simulator for KeenAI-Quant
Simulates multiple trading scenarios for risk assessment
"""

import numpy as np
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class MonteCarloResult:
    """Results from Monte Carlo simulation"""
    mean_return: float
    std_return: float
    var_95: float  # Value at Risk at 95%
    var_99: float  # Value at Risk at 99%
    max_drawdown: float
    win_rate: float
    simulations: int


class MonteCarloSimulator:
    """
    Monte Carlo simulator for trading strategy analysis
    Runs multiple simulations to assess risk and potential outcomes
    """
    
    def __init__(self, num_simulations: int = 1000):
        """
        Initialize Monte Carlo simulator
        
        Args:
            num_simulations: Number of simulations to run
        """
        self.num_simulations = num_simulations
    
    def simulate_strategy(
        self,
        initial_balance: float,
        avg_return: float,
        std_return: float,
        num_trades: int,
        win_rate: float
    ) -> MonteCarloResult:
        """
        Simulate trading strategy outcomes
        
        Args:
            initial_balance: Starting capital
            avg_return: Average return per trade
            std_return: Standard deviation of returns
            num_trades: Number of trades to simulate
            win_rate: Historical win rate
            
        Returns:
            MonteCarloResult with simulation statistics
        """
        final_balances = []
        max_drawdowns = []
        
        for _ in range(self.num_simulations):
            balance = initial_balance
            peak = initial_balance
            max_dd = 0.0
            
            for _ in range(num_trades):
                # Generate random return based on win rate
                if np.random.random() < win_rate:
                    # Winning trade
                    trade_return = abs(np.random.normal(avg_return, std_return))
                else:
                    # Losing trade
                    trade_return = -abs(np.random.normal(avg_return, std_return))
                
                balance *= (1 + trade_return)
                
                # Track drawdown
                if balance > peak:
                    peak = balance
                drawdown = (peak - balance) / peak
                max_dd = max(max_dd, drawdown)
            
            final_balances.append(balance)
            max_drawdowns.append(max_dd)
        
        # Calculate statistics
        returns = [(b - initial_balance) / initial_balance for b in final_balances]
        returns_sorted = sorted(returns)
        
        return MonteCarloResult(
            mean_return=np.mean(returns),
            std_return=np.std(returns),
            var_95=returns_sorted[int(0.05 * len(returns))],
            var_99=returns_sorted[int(0.01 * len(returns))],
            max_drawdown=np.mean(max_drawdowns),
            win_rate=win_rate,
            simulations=self.num_simulations
        )
    
    def simulate_portfolio(
        self,
        initial_balance: float,
        trade_history: List[Dict]
    ) -> MonteCarloResult:
        """
        Simulate portfolio based on historical trades
        
        Args:
            initial_balance: Starting capital
            trade_history: List of historical trades with 'pnl' field
            
        Returns:
            MonteCarloResult
        """
        if not trade_history:
            return MonteCarloResult(0, 0, 0, 0, 0, 0, 0)
        
        # Extract statistics from history
        returns = [t.get('pnl', 0) for t in trade_history]
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        win_rate = sum(1 for r in returns if r > 0) / len(returns)
        
        return self.simulate_strategy(
            initial_balance,
            avg_return,
            std_return,
            len(trade_history),
            win_rate
        )
