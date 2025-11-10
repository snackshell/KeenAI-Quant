"""
Monte Carlo Risk Analysis for KeenAI-Quant
Uses Monte Carlo simulation for risk assessment
"""

import numpy as np
from typing import List, Dict, Optional
from Backtesting.monte_carlo_simulator import MonteCarloSimulator, MonteCarloResult


class MonteCarloRiskAnalyzer:
    """
    Analyzes risk using Monte Carlo simulation
    Provides probabilistic risk metrics
    """
    
    def __init__(self, num_simulations: int = 1000):
        """
        Initialize Monte Carlo risk analyzer
        
        Args:
            num_simulations: Number of simulations to run
        """
        self.simulator = MonteCarloSimulator(num_simulations)
    
    def analyze_trade_risk(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        win_rate: float,
        position_size: float
    ) -> Dict[str, float]:
        """
        Analyze risk for a single trade
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            win_rate: Estimated win rate
            position_size: Position size
            
        Returns:
            Risk metrics dictionary
        """
        # Calculate potential outcomes
        max_loss = abs(entry_price - stop_loss) * position_size
        max_profit = abs(take_profit - entry_price) * position_size
        
        # Expected value
        expected_value = (win_rate * max_profit) - ((1 - win_rate) * max_loss)
        
        # Risk-reward ratio
        risk_reward = max_profit / max_loss if max_loss > 0 else 0
        
        return {
            'max_loss': max_loss,
            'max_profit': max_profit,
            'expected_value': expected_value,
            'risk_reward_ratio': risk_reward,
            'win_rate': win_rate,
            'breakeven_win_rate': 1 / (1 + risk_reward) if risk_reward > 0 else 0.5
        }
    
    def analyze_portfolio_risk(
        self,
        current_balance: float,
        trade_history: List[Dict],
        num_future_trades: int = 100
    ) -> MonteCarloResult:
        """
        Analyze portfolio risk using historical data
        
        Args:
            current_balance: Current account balance
            trade_history: Historical trades
            num_future_trades: Number of future trades to simulate
            
        Returns:
            MonteCarloResult with risk metrics
        """
        if not trade_history:
            return MonteCarloResult(0, 0, 0, 0, 0, 0, 0)
        
        return self.simulator.simulate_portfolio(current_balance, trade_history)
    
    def calculate_var(
        self,
        current_balance: float,
        trade_history: List[Dict],
        confidence_level: float = 0.95
    ) -> Dict[str, float]:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            current_balance: Current balance
            trade_history: Historical trades
            confidence_level: Confidence level (0.95 or 0.99)
            
        Returns:
            VaR metrics
        """
        result = self.analyze_portfolio_risk(current_balance, trade_history)
        
        var_value = result.var_95 if confidence_level == 0.95 else result.var_99
        var_dollars = abs(var_value * current_balance)
        
        return {
            'var_percentage': var_value * 100,
            'var_dollars': var_dollars,
            'confidence_level': confidence_level,
            'interpretation': f"With {confidence_level:.0%} confidence, maximum loss will not exceed ${var_dollars:.2f}"
        }
    
    def stress_test(
        self,
        current_balance: float,
        scenarios: List[Dict]
    ) -> Dict[str, any]:
        """
        Run stress tests on portfolio
        
        Args:
            current_balance: Current balance
            scenarios: List of stress scenarios
            
        Returns:
            Stress test results
        """
        results = {}
        
        for scenario in scenarios:
            name = scenario.get('name', 'Unknown')
            loss_percentage = scenario.get('loss_percentage', 0.10)
            
            potential_loss = current_balance * loss_percentage
            remaining_balance = current_balance - potential_loss
            
            results[name] = {
                'loss_percentage': loss_percentage * 100,
                'potential_loss': potential_loss,
                'remaining_balance': remaining_balance,
                'recovery_needed': (potential_loss / remaining_balance) * 100 if remaining_balance > 0 else float('inf')
            }
        
        return results
