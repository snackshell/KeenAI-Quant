"""
Reinforcement Learning for KeenAI-Quant
Q-Learning based approach for trading strategy optimization
"""

from typing import Dict, Optional, Tuple
import numpy as np
from collections import defaultdict


class QLearningAgent:
    """
    Q-Learning agent for trading decisions
    Learns optimal actions based on market states and rewards
    """
    
    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.1
    ):
        """
        Initialize Q-Learning agent
        
        Args:
            learning_rate: How quickly to update Q-values (alpha)
            discount_factor: Future reward discount (gamma)
            epsilon: Exploration rate for epsilon-greedy policy
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        # Q-table: state -> action -> value
        self.q_table: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
        # Action space
        self.actions = ['BUY', 'SELL', 'HOLD']
        
        # Statistics
        self.total_updates = 0
        self.episodes = 0
    
    def _state_to_key(self, state: Dict) -> str:
        """
        Convert state dictionary to hashable key
        
        Args:
            state: Market state dictionary
            
        Returns:
            String key for Q-table
        """
        # Discretize continuous values for Q-table
        rsi = int(state.get('rsi_14', 50) / 10) * 10
        macd_signal = 'pos' if state.get('macd', 0) > 0 else 'neg'
        trend = state.get('market_regime', 'neutral')
        
        return f"rsi_{rsi}_macd_{macd_signal}_trend_{trend}"
    
    def get_action(self, state: Dict, explore: bool = True) -> str:
        """
        Get action using epsilon-greedy policy
        
        Args:
            state: Current market state
            explore: Whether to explore (random action)
            
        Returns:
            Action to take (BUY/SELL/HOLD)
        """
        state_key = self._state_to_key(state)
        
        # Exploration: random action
        if explore and np.random.random() < self.epsilon:
            return np.random.choice(self.actions)
        
        # Exploitation: best known action
        q_values = self.q_table[state_key]
        
        if not q_values:
            return 'HOLD'  # Default action for unknown states
        
        return max(q_values.items(), key=lambda x: x[1])[0]
    
    def update(
        self,
        state: Dict,
        action: str,
        reward: float,
        next_state: Dict,
        done: bool
    ):
        """
        Update Q-values based on experience
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode ended
        """
        state_key = self._state_to_key(state)
        next_state_key = self._state_to_key(next_state)
        
        # Current Q-value
        current_q = self.q_table[state_key][action]
        
        # Maximum Q-value for next state
        if done:
            max_next_q = 0.0
        else:
            next_q_values = self.q_table[next_state_key]
            max_next_q = max(next_q_values.values()) if next_q_values else 0.0
        
        # Q-learning update rule
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state_key][action] = new_q
        self.total_updates += 1
        
        if done:
            self.episodes += 1
    
    def get_q_value(self, state: Dict, action: str) -> float:
        """
        Get Q-value for state-action pair
        
        Args:
            state: Market state
            action: Action
            
        Returns:
            Q-value
        """
        state_key = self._state_to_key(state)
        return self.q_table[state_key][action]
    
    def get_best_action(self, state: Dict) -> Tuple[str, float]:
        """
        Get best action and its Q-value
        
        Args:
            state: Market state
            
        Returns:
            Tuple of (action, q_value)
        """
        state_key = self._state_to_key(state)
        q_values = self.q_table[state_key]
        
        if not q_values:
            return ('HOLD', 0.0)
        
        best_action = max(q_values.items(), key=lambda x: x[1])
        return best_action
    
    def decay_epsilon(self, decay_rate: float = 0.995, min_epsilon: float = 0.01):
        """
        Decay exploration rate over time
        
        Args:
            decay_rate: Multiplicative decay factor
            min_epsilon: Minimum epsilon value
        """
        self.epsilon = max(min_epsilon, self.epsilon * decay_rate)
    
    def get_stats(self) -> Dict:
        """Get learning statistics"""
        return {
            'total_updates': self.total_updates,
            'episodes': self.episodes,
            'states_learned': len(self.q_table),
            'epsilon': self.epsilon,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor
        }
    
    def save_policy(self) -> Dict:
        """
        Save learned policy
        
        Returns:
            Dictionary representation of Q-table
        """
        return {
            'q_table': dict(self.q_table),
            'stats': self.get_stats()
        }
    
    def load_policy(self, policy: Dict):
        """
        Load learned policy
        
        Args:
            policy: Dictionary with Q-table and stats
        """
        if 'q_table' in policy:
            self.q_table = defaultdict(lambda: defaultdict(float), policy['q_table'])


# Global Q-learning agent instance
q_agent = QLearningAgent()
