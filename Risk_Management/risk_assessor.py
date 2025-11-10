"""
Risk Assessor Component
Calculates position sizes, stop-loss, take-profit levels
Validates trades against risk parameters
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from backend.models.trading_models import (
    TradingSignal, Account, OrderDirection, validate_price, validate_size
)
from backend.config import config


@dataclass
class ValidationResult:
    """Result of trade validation"""
    is_valid: bool
    reason: str = ""
    adjusted_size: Optional[float] = None
    
    def __str__(self) -> str:
        if self.is_valid:
            return f"✅ Valid{f' (adjusted size: {self.adjusted_size})' if self.adjusted_size else ''}"
        return f"❌ Invalid: {self.reason}"


class RiskAssessor:
    """
    Assesses and validates trading risks
    Calculates position sizes based on account risk parameters
    """
    
    def __init__(self):
        """Initialize risk assessor with configuration"""
        self.risk_config = config.risk
        
        # Risk parameters from config
        self.max_position_size = self.risk_config.max_position_size  # 25% of account
        self.max_daily_loss = self.risk_config.max_daily_loss  # 5% daily loss limit
        self.max_drawdown = self.risk_config.max_drawdown  # 15% max drawdown
        self.min_risk_reward = self.risk_config.min_risk_reward  # 1.5:1 minimum
        self.risk_per_trade = self.risk_config.risk_per_trade  # 2% risk per trade
        
        print(f"📊 RiskAssessor initialized:")
        print(f"   Max position size: {self.max_position_size*100}%")
        print(f"   Risk per trade: {self.risk_per_trade*100}%")
        print(f"   Min R:R ratio: {self.min_risk_reward}:1")
    
    def validate_trade(self, signal: TradingSignal, account: Account) -> ValidationResult:
        """
        Validate a trading signal against all risk parameters
        
        Args:
            signal: Trading signal to validate
            account: Current account state
            
        Returns:
            ValidationResult with validation status and reason
        """
        # Check 1: Risk-reward ratio
        rr_ratio = signal.risk_reward_ratio
        if rr_ratio < self.min_risk_reward:
            return ValidationResult(
                is_valid=False,
                reason=f"Risk-reward ratio {rr_ratio:.2f} below minimum {self.min_risk_reward}"
            )
        
        # Check 2: Position size
        max_size_by_account = account.balance * self.max_position_size / signal.entry_price
        if signal.size > max_size_by_account:
            return ValidationResult(
                is_valid=False,
                reason=f"Position size {signal.size:.4f} exceeds max {max_size_by_account:.4f}"
            )
        
        # Check 3: Account exposure (total position value)
        current_exposure = sum(
            pos.size * pos.current_price 
            for pos in account.positions
        )
        signal_exposure = signal.size * signal.entry_price
        total_exposure = current_exposure + signal_exposure
        max_exposure = account.balance * 0.75  # Max 75% total exposure
        
        if total_exposure > max_exposure:
            return ValidationResult(
                is_valid=False,
                reason=f"Total exposure ${total_exposure:.2f} exceeds max ${max_exposure:.2f}"
            )
        
        # Check 4: Stop-loss validation
        if signal.direction == OrderDirection.BUY:
            if signal.stop_loss >= signal.entry_price:
                return ValidationResult(
                    is_valid=False,
                    reason="Stop-loss must be below entry for BUY orders"
                )
        elif signal.direction == OrderDirection.SELL:
            if signal.stop_loss <= signal.entry_price:
                return ValidationResult(
                    is_valid=False,
                    reason="Stop-loss must be above entry for SELL orders"
                )
        
        # Check 5: Take-profit validation
        if signal.direction == OrderDirection.BUY:
            if signal.take_profit <= signal.entry_price:
                return ValidationResult(
                    is_valid=False,
                    reason="Take-profit must be above entry for BUY orders"
                )
        elif signal.direction == OrderDirection.SELL:
            if signal.take_profit >= signal.entry_price:
                return ValidationResult(
                    is_valid=False,
                    reason="Take-profit must be below entry for SELL orders"
                )
        
        # Check 6: Margin availability
        required_margin = signal_exposure * 0.01  # Assume 1:100 leverage
        if required_margin > account.margin_available:
            return ValidationResult(
                is_valid=False,
                reason=f"Insufficient margin: need ${required_margin:.2f}, have ${account.margin_available:.2f}"
            )
        
        # All checks passed
        return ValidationResult(is_valid=True, reason="All risk checks passed")
    
    def calculate_position_size(
        self, 
        signal: TradingSignal, 
        account: Account
    ) -> float:
        """
        Calculate optimal position size based on risk parameters
        
        Formula:
        risk_amount = account_balance * risk_per_trade
        stop_distance = abs(entry_price - stop_loss)
        position_size = risk_amount / stop_distance
        position_size = min(position_size, max_position_size_limit)
        
        Args:
            signal: Trading signal with entry and stop-loss
            account: Current account state
            
        Returns:
            Calculated position size
        """
        # Calculate risk amount (2% of account)
        risk_amount = account.balance * self.risk_per_trade
        
        # Calculate stop distance
        stop_distance = abs(signal.entry_price - signal.stop_loss)
        
        if stop_distance == 0:
            print("⚠️ Warning: Stop distance is zero, using minimum size")
            return 0.01
        
        # Calculate position size based on risk
        position_size = risk_amount / stop_distance
        
        # Apply maximum position size limit (25% of account)
        max_size_by_account = (account.balance * self.max_position_size) / signal.entry_price
        position_size = min(position_size, max_size_by_account)
        
        # Round to reasonable precision
        position_size = round(position_size, 4)
        
        return position_size
    
    def calculate_stop_loss(
        self, 
        entry_price: float, 
        atr: float, 
        direction: OrderDirection,
        atr_multiplier: float = 2.0
    ) -> float:
        """
        Calculate stop-loss level using ATR
        
        Args:
            entry_price: Entry price
            atr: Average True Range value
            direction: Order direction (BUY/SELL)
            atr_multiplier: ATR multiplier (default 2.0)
            
        Returns:
            Stop-loss price level
        """
        validate_price(entry_price, "entry_price")
        validate_price(atr, "atr")
        
        stop_distance = atr * atr_multiplier
        
        if direction == OrderDirection.BUY:
            stop_loss = entry_price - stop_distance
        elif direction == OrderDirection.SELL:
            stop_loss = entry_price + stop_distance
        else:
            raise ValueError(f"Invalid direction for stop-loss calculation: {direction}")
        
        # Ensure stop-loss is positive
        stop_loss = max(stop_loss, 0.0001)
        
        return round(stop_loss, 5)
    
    def calculate_take_profit(
        self, 
        entry_price: float, 
        stop_loss: float, 
        direction: OrderDirection,
        rr_ratio: Optional[float] = None
    ) -> float:
        """
        Calculate take-profit level based on risk-reward ratio
        
        Args:
            entry_price: Entry price
            stop_loss: Stop-loss price
            direction: Order direction (BUY/SELL)
            rr_ratio: Risk-reward ratio (default from config)
            
        Returns:
            Take-profit price level
        """
        validate_price(entry_price, "entry_price")
        validate_price(stop_loss, "stop_loss")
        
        if rr_ratio is None:
            rr_ratio = self.min_risk_reward
        
        # Calculate risk distance
        risk_distance = abs(entry_price - stop_loss)
        
        # Calculate reward distance
        reward_distance = risk_distance * rr_ratio
        
        if direction == OrderDirection.BUY:
            take_profit = entry_price + reward_distance
        elif direction == OrderDirection.SELL:
            take_profit = entry_price - reward_distance
        else:
            raise ValueError(f"Invalid direction for take-profit calculation: {direction}")
        
        # Ensure take-profit is positive
        take_profit = max(take_profit, 0.0001)
        
        return round(take_profit, 5)
    
    def adjust_signal_for_risk(
        self, 
        signal: TradingSignal, 
        account: Account
    ) -> TradingSignal:
        """
        Adjust trading signal to comply with risk parameters
        Recalculates position size and validates levels
        
        Args:
            signal: Original trading signal
            account: Current account state
            
        Returns:
            Adjusted trading signal
        """
        # Calculate optimal position size
        optimal_size = self.calculate_position_size(signal, account)
        
        # Create adjusted signal
        adjusted_signal = TradingSignal(
            pair=signal.pair,
            direction=signal.direction,
            confidence=signal.confidence,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            size=optimal_size,
            reasoning=f"{signal.reasoning} [Risk-adjusted size: {optimal_size}]",
            source=signal.source,
            timestamp=datetime.now()
        )
        
        return adjusted_signal
    
    def get_risk_metrics(self, account: Account) -> dict:
        """
        Calculate current risk metrics for the account
        
        Args:
            account: Current account state
            
        Returns:
            Dictionary of risk metrics
        """
        total_exposure = sum(
            pos.size * pos.current_price 
            for pos in account.positions
        )
        
        exposure_percentage = (total_exposure / account.balance * 100) if account.balance > 0 else 0
        
        return {
            'account_balance': account.balance,
            'account_equity': account.equity,
            'total_exposure': total_exposure,
            'exposure_percentage': exposure_percentage,
            'margin_used': account.margin_used,
            'margin_available': account.margin_available,
            'margin_level': account.margin_level,
            'unrealized_pnl': account.unrealized_pnl,
            'realized_pnl_today': account.realized_pnl_today,
            'open_positions': len(account.positions),
            'max_position_size_usd': account.balance * self.max_position_size,
            'risk_per_trade_usd': account.balance * self.risk_per_trade
        }
