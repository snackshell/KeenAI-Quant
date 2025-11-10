"""
Position Sizing for KeenAI-Quant
Calculates optimal position sizes based on risk parameters
"""

from typing import Dict, Optional
from backend.models.trading_models import Account


class PositionSizer:
    """
    Calculates position sizes based on risk management rules
    Implements Kelly Criterion and fixed fractional sizing
    """
    
    def __init__(
        self,
        risk_per_trade: float = 0.02,
        max_position_size: float = 0.25
    ):
        """
        Initialize position sizer
        
        Args:
            risk_per_trade: Risk percentage per trade (default 2%)
            max_position_size: Maximum position size as % of account
        """
        self.risk_per_trade = risk_per_trade
        self.max_position_size = max_position_size
    
    def calculate_position_size(
        self,
        account: Account,
        entry_price: float,
        stop_loss_price: float,
        confidence: float = 1.0
    ) -> float:
        """
        Calculate position size based on risk
        
        Args:
            account: Account information
            entry_price: Entry price
            stop_loss_price: Stop loss price
            confidence: AI confidence (0-1)
            
        Returns:
            Position size in units
        """
        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss_price)
        
        if risk_per_unit == 0:
            return 0.0
        
        # Calculate dollar risk
        dollar_risk = account.balance * self.risk_per_trade * confidence
        
        # Calculate position size
        position_size = dollar_risk / risk_per_unit
        
        # Apply maximum position size limit
        max_units = (account.balance * self.max_position_size) / entry_price
        position_size = min(position_size, max_units)
        
        return position_size
    
    def calculate_kelly_size(
        self,
        account: Account,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Calculate position size using Kelly Criterion
        
        Args:
            account: Account information
            win_rate: Historical win rate
            avg_win: Average winning trade
            avg_loss: Average losing trade
            
        Returns:
            Position size as % of account
        """
        if avg_loss == 0:
            return 0.0
        
        # Kelly formula: f = (p * b - q) / b
        # where p = win rate, q = loss rate, b = avg_win/avg_loss
        b = abs(avg_win / avg_loss)
        q = 1 - win_rate
        
        kelly_fraction = (win_rate * b - q) / b
        
        # Use half-Kelly for safety
        kelly_fraction = kelly_fraction * 0.5
        
        # Clamp to reasonable range
        kelly_fraction = max(0.0, min(kelly_fraction, self.max_position_size))
        
        return kelly_fraction
    
    def calculate_volatility_adjusted_size(
        self,
        account: Account,
        current_volatility: float,
        avg_volatility: float,
        base_size: float
    ) -> float:
        """
        Adjust position size based on volatility
        
        Args:
            account: Account information
            current_volatility: Current market volatility (ATR)
            avg_volatility: Average volatility
            base_size: Base position size
            
        Returns:
            Adjusted position size
        """
        if avg_volatility == 0:
            return base_size
        
        # Reduce size when volatility is high
        volatility_ratio = avg_volatility / current_volatility
        adjusted_size = base_size * volatility_ratio
        
        # Clamp to reasonable range
        max_size = account.balance * self.max_position_size
        return min(adjusted_size, max_size)
    
    def get_position_limits(self, account: Account) -> Dict[str, float]:
        """
        Get position size limits
        
        Args:
            account: Account information
            
        Returns:
            Dictionary with limits
        """
        return {
            'max_position_value': account.balance * self.max_position_size,
            'max_risk_per_trade': account.balance * self.risk_per_trade,
            'max_total_risk': account.balance * 0.10,  # 10% max total risk
            'min_position_value': account.balance * 0.01  # 1% minimum
        }
