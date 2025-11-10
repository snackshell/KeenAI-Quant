"""
Experience Replay Buffer for KeenAI-Quant
Stores and samples past trading experiences for learning
"""

from typing import List, Dict, Optional, Tuple
from collections import deque
import random
from datetime import datetime


class Experience:
    """Single trading experience"""
    
    def __init__(
        self,
        state: Dict,
        action: str,
        reward: float,
        next_state: Dict,
        done: bool
    ):
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state
        self.done = done
        self.timestamp = datetime.now()


class ExperienceReplayBuffer:
    """
    Replay buffer for storing and sampling trading experiences
    Used for reinforcement learning and pattern recognition
    """
    
    def __init__(self, capacity: int = 10000):
        """
        Initialize replay buffer
        
        Args:
            capacity: Maximum number of experiences to store
        """
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity
    
    def add(
        self,
        state: Dict,
        action: str,
        reward: float,
        next_state: Dict,
        done: bool
    ):
        """
        Add an experience to the buffer
        
        Args:
            state: Market state before action
            action: Action taken (BUY/SELL/HOLD)
            reward: Reward received (PnL)
            next_state: Market state after action
            done: Whether episode ended
        """
        experience = Experience(state, action, reward, next_state, done)
        self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """
        Sample random batch of experiences
        
        Args:
            batch_size: Number of experiences to sample
            
        Returns:
            List of Experience objects
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)
        
        return random.sample(list(self.buffer), batch_size)
    
    def sample_recent(self, n: int) -> List[Experience]:
        """
        Sample most recent experiences
        
        Args:
            n: Number of recent experiences
            
        Returns:
            List of recent Experience objects
        """
        return list(self.buffer)[-n:]
    
    def sample_by_reward(self, n: int, positive_only: bool = False) -> List[Experience]:
        """
        Sample experiences by reward
        
        Args:
            n: Number of experiences to sample
            positive_only: Only sample positive rewards
            
        Returns:
            List of Experience objects
        """
        experiences = list(self.buffer)
        
        if positive_only:
            experiences = [e for e in experiences if e.reward > 0]
        
        # Sort by reward and take top n
        experiences.sort(key=lambda e: e.reward, reverse=True)
        return experiences[:n]
    
    def get_statistics(self) -> Dict:
        """Get buffer statistics"""
        if not self.buffer:
            return {
                'size': 0,
                'avg_reward': 0.0,
                'positive_experiences': 0,
                'negative_experiences': 0
            }
        
        rewards = [e.reward for e in self.buffer]
        positive = sum(1 for r in rewards if r > 0)
        negative = sum(1 for r in rewards if r < 0)
        
        return {
            'size': len(self.buffer),
            'capacity': self.capacity,
            'avg_reward': sum(rewards) / len(rewards),
            'max_reward': max(rewards),
            'min_reward': min(rewards),
            'positive_experiences': positive,
            'negative_experiences': negative,
            'win_rate': positive / len(rewards) if rewards else 0.0
        }
    
    def clear(self):
        """Clear all experiences"""
        self.buffer.clear()
    
    def __len__(self) -> int:
        """Get buffer size"""
        return len(self.buffer)


# Global replay buffer instance
replay_buffer = ExperienceReplayBuffer()
