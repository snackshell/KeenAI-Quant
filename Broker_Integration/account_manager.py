"""
Account Manager
Manages account information and updates
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from backend.models.trading_models import Account, Position

# Optional OpenAlgo wrapper for fallback
try:
    from .openalgo_wrapper import OpenAlgoWrapper
    OPENALGO_AVAILABLE = True
except ImportError:
    OPENALGO_AVAILABLE = False
    OpenAlgoWrapper = None


class AccountManager:
    """
    Manages account information retrieval and updates
    """
    
    def __init__(
        self,
        wrapper: Optional[Any] = None,
        position_manager: Optional[Any] = None
    ):
        """
        Initialize account manager
        
        Args:
            wrapper: OpenAlgo wrapper instance (optional, for fallback)
            position_manager: Position manager instance
        """
        # OpenAlgo wrapper is optional now
        if OPENALGO_AVAILABLE and wrapper is None:
            try:
                self.wrapper = OpenAlgoWrapper()
            except:
                self.wrapper = None
        else:
            self.wrapper = wrapper
        
        # Import position manager here to avoid circular import
        if position_manager is None:
            from .position_manager import PositionManager
            self.position_manager = PositionManager()
        else:
            self.position_manager = position_manager
        
        self.account: Optional[Account] = None
        self.last_update: Optional[datetime] = None
        self.update_interval = 5  # seconds
        self.is_updating = False
        
        print(f"💰 AccountManager initialized")
        print(f"   Update interval: {self.update_interval}s")
    
    def update_account(self) -> bool:
        """
        Update account information from broker
        
        Returns:
            True if successful
        """
        try:
            # Use broker service for direct MT5 integration
            from .broker_service import broker_service
            
            success, response_data, status_code = broker_service.get_account_info()
            
            if not success or 'data' not in response_data:
                print(f"⚠️ Failed to get account data from broker service")
                return False
            
            account_data = response_data['data']
            
            # Update positions
            self.position_manager.update_positions()
            
            # Create account object directly from broker data
            self.account = Account(
                balance=account_data['balance'],
                equity=account_data['equity'],
                margin_used=account_data['margin'],
                margin_available=account_data['margin_free'],
                unrealized_pnl=account_data['profit'],
                realized_pnl_today=0.0,
                positions=self.position_manager.get_all_positions()
            )
            
            self.last_update = datetime.now()
            
            print(f"💰 Account updated:")
            print(f"   Balance: ${self.account.balance:.2f}")
            print(f"   Equity: ${self.account.equity:.2f}")
            print(f"   Unrealized P&L: ${self.account.unrealized_pnl:.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating account: {e}")
            return False
    
    def _parse_account_data(
        self,
        funds_data: Dict[str, Any],
        positions: list[Position]
    ) -> Account:
        """
        Parse account data from broker format
        
        Args:
            funds_data: Funds data from broker
            positions: List of open positions
            
        Returns:
            Account object
        """
        # Extract account values
        # Note: Field names may vary by broker
        balance = float(funds_data.get('availablecash', 0))
        equity = float(funds_data.get('net', balance))
        margin_used = float(funds_data.get('utiliseddebits', 0))
        margin_available = float(funds_data.get('availablemargin', balance))
        
        # Calculate unrealized P&L from positions
        unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
        
        # Realized P&L today (would need to track from trades)
        realized_pnl_today = 0.0
        
        # Create account object
        account = Account(
            balance=balance,
            equity=equity,
            margin_used=margin_used,
            margin_available=margin_available,
            unrealized_pnl=unrealized_pnl,
            realized_pnl_today=realized_pnl_today,
            positions=positions
        )
        
        return account
    
    def get_account(self) -> Optional[Account]:
        """
        Get current account state
        
        Returns:
            Account object or None
        """
        return self.account
    
    async def start_auto_update(self) -> None:
        """
        Start automatic account updates
        Updates account every N seconds
        """
        if self.is_updating:
            print(f"⚠️ Auto-update already running")
            return
        
        self.is_updating = True
        print(f"🔄 Starting auto-update (every {self.update_interval}s)")
        
        while self.is_updating:
            try:
                self.update_account()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ Error in auto-update: {e}")
                await asyncio.sleep(self.update_interval)
    
    def stop_auto_update(self) -> None:
        """Stop automatic account updates"""
        self.is_updating = False
        print(f"⏹️ Auto-update stopped")
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get account summary
        
        Returns:
            Dictionary with account summary
        """
        if not self.account:
            return {
                'status': 'not_initialized',
                'message': 'Account not yet updated'
            }
        
        return {
            'status': 'active',
            'balance': self.account.balance,
            'equity': self.account.equity,
            'margin_used': self.account.margin_used,
            'margin_available': self.account.margin_available,
            'margin_level': self.account.margin_level,
            'unrealized_pnl': self.account.unrealized_pnl,
            'realized_pnl_today': self.account.realized_pnl_today,
            'total_pnl': self.account.total_pnl,
            'open_positions': len(self.account.positions),
            'last_update': self.last_update.isoformat() if self.last_update else None
        }
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """
        Get risk-related metrics
        
        Returns:
            Dictionary with risk metrics
        """
        if not self.account:
            return {}
        
        # Calculate exposure
        total_exposure = sum(
            pos.size * pos.current_price
            for pos in self.account.positions
        )
        
        exposure_percentage = (total_exposure / self.account.balance * 100) if self.account.balance > 0 else 0
        
        return {
            'account_balance': self.account.balance,
            'account_equity': self.account.equity,
            'total_exposure': total_exposure,
            'exposure_percentage': exposure_percentage,
            'margin_used': self.account.margin_used,
            'margin_available': self.account.margin_available,
            'margin_level': self.account.margin_level,
            'free_margin': self.account.free_margin,
            'unrealized_pnl': self.account.unrealized_pnl,
            'realized_pnl_today': self.account.realized_pnl_today
        }
    
    def is_account_healthy(self) -> bool:
        """
        Check if account is in healthy state
        
        Returns:
            True if account is healthy
        """
        if not self.account:
            return False
        
        # Check margin level (should be > 100%)
        if self.account.margin_level < 100:
            print(f"⚠️ Low margin level: {self.account.margin_level:.1f}%")
            return False
        
        # Check if equity is positive
        if self.account.equity <= 0:
            print(f"⚠️ Negative equity: ${self.account.equity:.2f}")
            return False
        
        return True
    
    def get_update_status(self) -> Dict[str, Any]:
        """
        Get update status information
        
        Returns:
            Dictionary with update status
        """
        return {
            'is_updating': self.is_updating,
            'update_interval': self.update_interval,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'account_initialized': self.account is not None
        }


# Global instance
account_manager = AccountManager()
