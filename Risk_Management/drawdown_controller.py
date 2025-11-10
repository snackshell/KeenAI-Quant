"""
Drawdown Controller for KeenAI-Quant
Monitors and controls drawdown to protect capital
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import deque


class DrawdownController:
    """
    Controls drawdown and implements protective measures
    Pauses trading when drawdown limits are reached
    """
    
    def __init__(
        self,
        max_drawdown: float = 0.15,
        daily_loss_limit: float = 0.05,
        recovery_threshold: float = 0.10
    ):
        """
        Initialize drawdown controller
        
        Args:
            max_drawdown: Maximum allowed drawdown (15%)
            daily_loss_limit: Maximum daily loss (5%)
            recovery_threshold: Drawdown level to resume trading (10%)
        """
        self.max_drawdown = max_drawdown
        self.daily_loss_limit = daily_loss_limit
        self.recovery_threshold = recovery_threshold
        
        self.peak_balance = 0.0
        self.current_drawdown = 0.0
        self.daily_pnl = 0.0
        self.trading_paused = False
        self.pause_reason = None
        
        # Track daily performance
        self.daily_start_balance = 0.0
        self.last_reset_date = datetime.now().date()
    
    def update(self, current_balance: float) -> Dict[str, any]:
        """
        Update drawdown calculations
        
        Args:
            current_balance: Current account balance
            
        Returns:
            Status dictionary
        """
        # Reset daily tracking if new day
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.daily_start_balance = current_balance
            self.daily_pnl = 0.0
            self.last_reset_date = current_date
        
        # Update peak
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
        
        # Calculate current drawdown
        if self.peak_balance > 0:
            self.current_drawdown = (self.peak_balance - current_balance) / self.peak_balance
        
        # Calculate daily P&L
        if self.daily_start_balance > 0:
            self.daily_pnl = (current_balance - self.daily_start_balance) / self.daily_start_balance
        
        # Check if we should pause trading
        self._check_limits()
        
        return self.get_status()
    
    def _check_limits(self):
        """Check if any limits are breached"""
        # Check max drawdown
        if self.current_drawdown >= self.max_drawdown:
            self.trading_paused = True
            self.pause_reason = f"Max drawdown reached: {self.current_drawdown:.2%}"
            return
        
        # Check daily loss limit
        if self.daily_pnl <= -self.daily_loss_limit:
            self.trading_paused = True
            self.pause_reason = f"Daily loss limit reached: {self.daily_pnl:.2%}"
            return
        
        # Check if we can resume trading
        if self.trading_paused and self.current_drawdown < self.recovery_threshold:
            self.trading_paused = False
            self.pause_reason = None
    
    def can_trade(self) -> bool:
        """
        Check if trading is allowed
        
        Returns:
            True if trading is allowed
        """
        return not self.trading_paused
    
    def get_status(self) -> Dict[str, any]:
        """
        Get current drawdown status
        
        Returns:
            Status dictionary
        """
        return {
            'current_drawdown': self.current_drawdown,
            'max_drawdown': self.max_drawdown,
            'daily_pnl': self.daily_pnl,
            'daily_loss_limit': self.daily_loss_limit,
            'trading_paused': self.trading_paused,
            'pause_reason': self.pause_reason,
            'peak_balance': self.peak_balance,
            'drawdown_percentage': self.current_drawdown * 100
        }
    
    def reset(self, new_peak: Optional[float] = None):
        """
        Reset drawdown tracking
        
        Args:
            new_peak: Optional new peak balance
        """
        if new_peak:
            self.peak_balance = new_peak
        self.current_drawdown = 0.0
        self.trading_paused = False
        self.pause_reason = None
    
    def force_pause(self, reason: str):
        """
        Manually pause trading
        
        Args:
            reason: Reason for pause
        """
        self.trading_paused = True
        self.pause_reason = reason
    
    def force_resume(self):
        """Manually resume trading"""
        self.trading_paused = False
        self.pause_reason = None
