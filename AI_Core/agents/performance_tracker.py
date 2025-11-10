"""
Agent Performance Tracker for KeenAI-Quant
Tracks AI agent performance and calculates metrics
"""

from typing import Dict, List
from datetime import datetime, timedelta
import numpy as np

from backend.database import db, AgentPerformanceDAL, AIDecisionDAL
from backend.models.trading_models import AgentPrediction


class AgentPerformanceTracker:
    """
    Track and analyze AI agent performance
    Calculates win rate, Sharpe ratio, and other metrics
    """
    
    def __init__(self):
        """Initialize performance tracker"""
        self.agent_trades = {}  # Track trades per agent
        self.agent_returns = {}  # Track returns per agent
    
    def record_prediction(
        self,
        agent_name: str,
        prediction: AgentPrediction,
        actual_outcome: str = None
    ):
        """
        Record an agent prediction
        
        Args:
            agent_name: Name of the agent
            prediction: AgentPrediction object
            actual_outcome: Actual market outcome ('correct', 'incorrect', or None if unknown)
        """
        if agent_name not in self.agent_trades:
            self.agent_trades[agent_name] = []
        
        self.agent_trades[agent_name].append({
            'prediction': prediction,
            'outcome': actual_outcome,
            'timestamp': prediction.timestamp
        })
    
    def record_trade_result(
        self,
        agent_name: str,
        pnl: float,
        trade_return: float
    ):
        """
        Record trade result for an agent
        
        Args:
            agent_name: Name of the agent
            pnl: Profit/loss in currency
            trade_return: Return as percentage
        """
        if agent_name not in self.agent_returns:
            self.agent_returns[agent_name] = []
        
        self.agent_returns[agent_name].append({
            'pnl': pnl,
            'return': trade_return,
            'timestamp': datetime.now()
        })
    
    def calculate_metrics(self, agent_name: str, days: int = 30) -> Dict:
        """
        Calculate performance metrics for an agent
        
        Args:
            agent_name: Name of the agent
            days: Number of days to look back
            
        Returns:
            Dictionary with performance metrics
        """
        # Get recent trades
        trades = self.agent_trades.get(agent_name, [])
        returns = self.agent_returns.get(agent_name, [])
        
        # Filter by date
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_trades = [t for t in trades if t['timestamp'] >= cutoff_date]
        recent_returns = [r for r in returns if r['timestamp'] >= cutoff_date]
        
        # Calculate win rate
        total_signals = len(recent_trades)
        correct_signals = len([t for t in recent_trades if t['outcome'] == 'correct'])
        win_rate = correct_signals / total_signals if total_signals > 0 else 0.0
        
        # Calculate average confidence
        avg_confidence = np.mean([t['prediction'].confidence for t in recent_trades]) if recent_trades else 0.0
        
        # Calculate Sharpe ratio
        if len(recent_returns) > 1:
            returns_array = np.array([r['return'] for r in recent_returns])
            mean_return = np.mean(returns_array)
            std_return = np.std(returns_array)
            sharpe_ratio = (mean_return / std_return) * np.sqrt(252) if std_return > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        return {
            'total_signals': total_signals,
            'correct_signals': correct_signals,
            'win_rate': win_rate,
            'avg_confidence': avg_confidence,
            'sharpe_ratio': sharpe_ratio
        }
    
    def update_database(self, agent_name: str):
        """
        Update agent performance in database
        
        Args:
            agent_name: Name of the agent
        """
        metrics = self.calculate_metrics(agent_name)
        
        session = db.get_session()
        try:
            AgentPerformanceDAL.update_performance(
                session=session,
                agent_name=agent_name,
                metrics=metrics
            )
        finally:
            session.close()
    
    def get_all_agent_metrics(self, days: int = 30) -> Dict[str, Dict]:
        """
        Get metrics for all agents
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary mapping agent name to metrics
        """
        all_metrics = {}
        
        for agent_name in self.agent_trades.keys():
            all_metrics[agent_name] = self.calculate_metrics(agent_name, days)
        
        return all_metrics
    
    def get_leaderboard(self, days: int = 30) -> List[Dict]:
        """
        Get agent leaderboard sorted by performance
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of agent metrics sorted by win rate
        """
        all_metrics = self.get_all_agent_metrics(days)
        
        leaderboard = []
        for agent_name, metrics in all_metrics.items():
            leaderboard.append({
                'agent_name': agent_name,
                **metrics
            })
        
        # Sort by win rate, then by Sharpe ratio
        leaderboard.sort(key=lambda x: (x['win_rate'], x['sharpe_ratio']), reverse=True)
        
        return leaderboard


# Global instance
performance_tracker = AgentPerformanceTracker()
