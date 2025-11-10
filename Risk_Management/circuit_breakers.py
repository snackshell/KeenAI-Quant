"""
Circuit Breaker System
Monitors trading performance and halts trading when risk limits are breached
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional
from enum import Enum

from backend.models.trading_models import Account
from backend.config import config


class CircuitBreakerStatus(str, Enum):
    """Circuit breaker status"""
    ACTIVE = "ACTIVE"  # Trading allowed
    TRIPPED = "TRIPPED"  # Trading halted
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"  # Manually disabled


@dataclass
class CircuitBreakerEvent:
    """Record of circuit breaker trigger"""
    timestamp: datetime
    reason: str
    trigger_value: float
    threshold_value: float
    
    def __str__(self) -> str:
        return (
            f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{self.reason} (Value: {self.trigger_value:.2f}, Threshold: {self.threshold_value:.2f})"
        )


class CircuitBreaker:
    """
    Circuit breaker system that monitors trading performance
    and halts trading when risk limits are breached
    """
    
    def __init__(self):
        """Initialize circuit breaker with configuration"""
        self.risk_config = config.risk
        
        # Risk thresholds
        self.max_daily_loss = self.risk_config.max_daily_loss  # 5%
        self.max_drawdown = self.risk_config.max_drawdown  # 15%
        self.max_consecutive_losses = 5
        
        # State tracking
        self.status = CircuitBreakerStatus.ACTIVE
        self.starting_balance_today: Optional[float] = None
        self.peak_equity: Optional[float] = None
        self.consecutive_losses = 0
        self.last_reset_date: Optional[date] = None
        self.trip_history: List[CircuitBreakerEvent] = []
        
        print(f"🔒 CircuitBreaker initialized:")
        print(f"   Max daily loss: {self.max_daily_loss*100}%")
        print(f"   Max drawdown: {self.max_drawdown*100}%")
        print(f"   Max consecutive losses: {self.max_consecutive_losses}")
    
    def check_all_conditions(self, account: Account) -> bool:
        """
        Check all circuit breaker conditions
        
        Args:
            account: Current account state
            
        Returns:
            True if all checks pass (trading allowed), False if breaker tripped
        """
        # If already tripped, stay tripped
        if self.status == CircuitBreakerStatus.TRIPPED:
            return False
        
        # If manual override, allow trading
        if self.status == CircuitBreakerStatus.MANUAL_OVERRIDE:
            return True
        
        # Reset daily tracking if new day
        self._check_daily_reset()
        
        # Initialize tracking values
        if self.starting_balance_today is None:
            self.starting_balance_today = account.balance
        
        if self.peak_equity is None or account.equity > self.peak_equity:
            self.peak_equity = account.equity
        
        # Check 1: Daily loss limit
        if not self.check_daily_loss(account.realized_pnl_today, self.starting_balance_today):
            return False
        
        # Check 2: Drawdown limit
        if not self.check_drawdown(account.equity, self.peak_equity):
            return False
        
        # Check 3: Consecutive losses (checked separately when trade closes)
        if not self.check_consecutive_losses():
            return False
        
        return True
    
    def check_daily_loss(self, current_pnl: float, starting_balance: float) -> bool:
        """
        Check if daily loss exceeds limit
        
        Args:
            current_pnl: Current realized P&L for the day
            starting_balance: Starting balance at beginning of day
            
        Returns:
            True if within limits, False if limit breached
        """
        if starting_balance <= 0:
            return True
        
        loss_percentage = abs(current_pnl / starting_balance)
        
        if current_pnl < 0 and loss_percentage > self.max_daily_loss:
            self._trigger_breaker(
                reason="Daily loss limit exceeded",
                trigger_value=loss_percentage * 100,
                threshold_value=self.max_daily_loss * 100
            )
            return False
        
        return True
    
    def check_drawdown(self, current_equity: float, peak_equity: float) -> bool:
        """
        Check if drawdown from peak exceeds limit
        
        Args:
            current_equity: Current account equity
            peak_equity: Peak equity reached
            
        Returns:
            True if within limits, False if limit breached
        """
        if peak_equity <= 0:
            return True
        
        drawdown = (peak_equity - current_equity) / peak_equity
        
        if drawdown > self.max_drawdown:
            self._trigger_breaker(
                reason="Maximum drawdown exceeded",
                trigger_value=drawdown * 100,
                threshold_value=self.max_drawdown * 100
            )
            return False
        
        return True
    
    def check_consecutive_losses(self) -> bool:
        """
        Check if consecutive losses exceed limit
        
        Returns:
            True if within limits, False if limit breached
        """
        if self.consecutive_losses >= self.max_consecutive_losses:
            self._trigger_breaker(
                reason="Maximum consecutive losses reached",
                trigger_value=self.consecutive_losses,
                threshold_value=self.max_consecutive_losses
            )
            return False
        
        return True
    
    def record_trade_result(self, pnl: float) -> None:
        """
        Record the result of a closed trade
        Updates consecutive loss counter
        
        Args:
            pnl: Profit/loss of the closed trade
        """
        if pnl < 0:
            self.consecutive_losses += 1
            print(f"📉 Loss recorded. Consecutive losses: {self.consecutive_losses}/{self.max_consecutive_losses}")
        else:
            if self.consecutive_losses > 0:
                print(f"📈 Win! Resetting consecutive loss counter from {self.consecutive_losses}")
            self.consecutive_losses = 0
        
        # Check if consecutive losses triggered breaker
        self.check_consecutive_losses()
    
    def _trigger_breaker(self, reason: str, trigger_value: float, threshold_value: float) -> None:
        """
        Trigger the circuit breaker
        
        Args:
            reason: Reason for triggering
            trigger_value: Value that triggered the breaker
            threshold_value: Threshold that was exceeded
        """
        self.status = CircuitBreakerStatus.TRIPPED
        
        event = CircuitBreakerEvent(
            timestamp=datetime.now(),
            reason=reason,
            trigger_value=trigger_value,
            threshold_value=threshold_value
        )
        
        self.trip_history.append(event)
        
        print(f"\n🚨 CIRCUIT BREAKER TRIPPED! 🚨")
        print(f"   Reason: {reason}")
        print(f"   Value: {trigger_value:.2f}")
        print(f"   Threshold: {threshold_value:.2f}")
        print(f"   Trading HALTED")
        print(f"   Manual reset required\n")
    
    def reset_breaker(self, manual: bool = True) -> bool:
        """
        Reset the circuit breaker
        
        Args:
            manual: Whether this is a manual reset
            
        Returns:
            True if reset successful
        """
        if self.status == CircuitBreakerStatus.TRIPPED:
            if manual:
                self.status = CircuitBreakerStatus.ACTIVE
                self.consecutive_losses = 0
                print(f"✅ Circuit breaker manually reset")
                print(f"   Status: {self.status}")
                print(f"   Trading resumed")
                return True
            else:
                print(f"⚠️ Automatic reset not allowed when tripped")
                print(f"   Manual reset required")
                return False
        else:
            print(f"ℹ️ Circuit breaker already active")
            return True
    
    def _check_daily_reset(self) -> None:
        """Check if we need to reset daily tracking (new trading day)"""
        today = date.today()
        
        if self.last_reset_date != today:
            print(f"📅 New trading day: {today}")
            print(f"   Resetting daily tracking")
            self.starting_balance_today = None
            self.last_reset_date = today
            
            # Reset consecutive losses at start of new day
            if self.consecutive_losses > 0:
                print(f"   Resetting consecutive losses from {self.consecutive_losses}")
                self.consecutive_losses = 0
    
    def get_status(self) -> dict:
        """
        Get current circuit breaker status
        
        Returns:
            Dictionary with status information
        """
        return {
            'status': self.status.value,
            'is_active': self.status == CircuitBreakerStatus.ACTIVE,
            'consecutive_losses': self.consecutive_losses,
            'max_consecutive_losses': self.max_consecutive_losses,
            'starting_balance_today': self.starting_balance_today,
            'peak_equity': self.peak_equity,
            'trip_count': len(self.trip_history),
            'last_trip': str(self.trip_history[-1]) if self.trip_history else None,
            'last_reset_date': self.last_reset_date.isoformat() if self.last_reset_date else None
        }
    
    def get_trip_history(self, limit: int = 10) -> List[str]:
        """
        Get recent circuit breaker trip history
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of trip event strings
        """
        return [str(event) for event in self.trip_history[-limit:]]
    
    def is_halted(self) -> bool:
        """
        Check if circuit breaker is currently halted (tripped)
        
        Returns:
            True if trading is halted, False if trading is allowed
        """
        return self.status == CircuitBreakerStatus.TRIPPED
    
    def enable_manual_override(self) -> None:
        """Enable manual override (bypass circuit breaker)"""
        self.status = CircuitBreakerStatus.MANUAL_OVERRIDE
        print(f"⚠️ Manual override enabled - circuit breaker bypassed")
    
    def disable_manual_override(self) -> None:
        """Disable manual override (re-enable circuit breaker)"""
        if self.status == CircuitBreakerStatus.MANUAL_OVERRIDE:
            self.status = CircuitBreakerStatus.ACTIVE
            print(f"✅ Manual override disabled - circuit breaker active")


# Global instance
circuit_breaker = CircuitBreaker()
