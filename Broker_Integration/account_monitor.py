"""
Account Monitor for KeenAI-Quant
Monitors account status and sends alerts
"""

from typing import Dict, List, Callable, Optional
from datetime import datetime
from backend.models.trading_models import Account
from backend.core.events import event_bus, EventType


class AccountMonitor:
    """
    Monitors account health and sends alerts
    Tracks balance, margin, and risk metrics
    """
    
    def __init__(
        self,
        low_balance_threshold: float = 1000.0,
        low_margin_threshold: float = 0.20
    ):
        """
        Initialize account monitor
        
        Args:
            low_balance_threshold: Alert when balance drops below this
            low_margin_threshold: Alert when margin level drops below this (20%)
        """
        self.low_balance_threshold = low_balance_threshold
        self.low_margin_threshold = low_margin_threshold
        
        self.alert_callbacks: List[Callable] = []
        self.last_account_state: Optional[Account] = None
        self.alerts_sent: Dict[str, datetime] = {}
    
    def register_alert_callback(self, callback: Callable):
        """
        Register callback for alerts
        
        Args:
            callback: Function to call when alert is triggered
        """
        self.alert_callbacks.append(callback)
    
    async def check_account(self, account: Account):
        """
        Check account status and send alerts if needed
        
        Args:
            account: Current account state
        """
        self.last_account_state = account
        
        # Check balance
        if account.balance < self.low_balance_threshold:
            await self._send_alert(
                'low_balance',
                f"⚠️ Low Balance Alert: ${account.balance:.2f}",
                {'balance': account.balance, 'threshold': self.low_balance_threshold}
            )
        
        # Check margin level
        margin_level = account.margin_level
        if margin_level < self.low_margin_threshold:
            await self._send_alert(
                'low_margin',
                f"⚠️ Low Margin Alert: {margin_level:.2%}",
                {'margin_level': margin_level, 'threshold': self.low_margin_threshold}
            )
        
        # Check for significant balance change
        if self.last_account_state:
            balance_change = account.balance - self.last_account_state.balance
            change_pct = abs(balance_change / self.last_account_state.balance) if self.last_account_state.balance > 0 else 0
            
            if change_pct > 0.10:  # 10% change
                await self._send_alert(
                    'significant_change',
                    f"📊 Significant Balance Change: {balance_change:+.2f} ({change_pct:.1%})",
                    {'balance_change': balance_change, 'change_pct': change_pct}
                )
    
    async def _send_alert(self, alert_type: str, message: str, data: Dict):
        """
        Send alert to all registered callbacks
        
        Args:
            alert_type: Type of alert
            message: Alert message
            data: Alert data
        """
        # Prevent duplicate alerts within 5 minutes
        now = datetime.now()
        if alert_type in self.alerts_sent:
            last_sent = self.alerts_sent[alert_type]
            if (now - last_sent).total_seconds() < 300:  # 5 minutes
                return
        
        self.alerts_sent[alert_type] = now
        
        # Send to callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, message, data)
            except Exception as e:
                print(f"Error in alert callback: {e}")
        
        # Publish event
        await event_bus.publish(EventType.ERROR_OCCURRED, {
            'alert_type': alert_type,
            'message': message,
            'data': data
        })
        
        print(message)
    
    def get_account_health(self, account: Account) -> Dict[str, any]:
        """
        Get account health metrics
        
        Args:
            account: Account to analyze
            
        Returns:
            Health metrics dictionary
        """
        health_score = 100.0
        issues = []
        
        # Check balance
        if account.balance < self.low_balance_threshold:
            health_score -= 30
            issues.append("Low balance")
        
        # Check margin
        if account.margin_level < self.low_margin_threshold:
            health_score -= 40
            issues.append("Low margin level")
        
        # Check equity
        if account.equity < account.balance * 0.90:
            health_score -= 20
            issues.append("Significant unrealized losses")
        
        # Determine status
        if health_score >= 80:
            status = "Healthy"
        elif health_score >= 60:
            status = "Warning"
        else:
            status = "Critical"
        
        return {
            'health_score': max(0, health_score),
            'status': status,
            'issues': issues,
            'balance': account.balance,
            'equity': account.equity,
            'margin_level': account.margin_level,
            'free_margin': account.free_margin
        }


# Global account monitor instance
account_monitor = AccountMonitor()
