"""
Risk Validation Pipeline
Orchestrates risk checks before trade execution
"""

from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass

from backend.models.trading_models import TradingSignal, Account, OrderDirection
from .risk_assessor import RiskAssessor, ValidationResult
from .circuit_breakers import CircuitBreaker, CircuitBreakerStatus


@dataclass
class RiskValidationReport:
    """Complete risk validation report"""
    is_approved: bool
    signal: TradingSignal
    original_signal: TradingSignal
    validation_result: ValidationResult
    circuit_breaker_status: CircuitBreakerStatus
    risk_metrics: dict
    rejection_reasons: List[str]
    timestamp: datetime
    
    def __str__(self) -> str:
        status = "✅ APPROVED" if self.is_approved else "❌ REJECTED"
        reasons = "\n   ".join(self.rejection_reasons) if self.rejection_reasons else "None"
        return (
            f"\n{'='*60}\n"
            f"Risk Validation Report - {status}\n"
            f"{'='*60}\n"
            f"Pair: {self.signal.pair}\n"
            f"Direction: {self.signal.direction.value}\n"
            f"Entry: ${self.signal.entry_price:.5f}\n"
            f"Size: {self.signal.size:.4f} (Original: {self.original_signal.size:.4f})\n"
            f"Stop Loss: ${self.signal.stop_loss:.5f}\n"
            f"Take Profit: ${self.signal.take_profit:.5f}\n"
            f"R:R Ratio: {self.signal.risk_reward_ratio:.2f}:1\n"
            f"Confidence: {self.signal.confidence:.1%}\n"
            f"Circuit Breaker: {self.circuit_breaker_status.value}\n"
            f"Rejection Reasons: {reasons}\n"
            f"{'='*60}\n"
        )


class RiskValidator:
    """
    Risk validation pipeline that orchestrates all risk checks
    Combines risk assessor and circuit breaker checks
    """
    
    def __init__(self):
        """Initialize risk validator with components"""
        self.risk_assessor = RiskAssessor()
        self.circuit_breaker = CircuitBreaker()
        self.validation_history: List[RiskValidationReport] = []
        
        print(f"🛡️ RiskValidator initialized")
        print(f"   Components: RiskAssessor + CircuitBreaker")
    
    def validate_signal(
        self, 
        signal: TradingSignal, 
        account: Account,
        adjust_size: bool = True
    ) -> RiskValidationReport:
        """
        Validate a trading signal through complete risk pipeline
        
        Args:
            signal: Trading signal to validate
            account: Current account state
            adjust_size: Whether to adjust position size for risk
            
        Returns:
            RiskValidationReport with validation results
        """
        rejection_reasons = []
        original_signal = signal
        
        # Step 1: Check circuit breaker
        if not self.circuit_breaker.check_all_conditions(account):
            rejection_reasons.append(
                f"Circuit breaker tripped: {self.circuit_breaker.status.value}"
            )
        
        # Step 2: Adjust signal for risk if requested
        if adjust_size:
            signal = self.risk_assessor.adjust_signal_for_risk(signal, account)
        
        # Step 3: Validate adjusted signal
        validation_result = self.risk_assessor.validate_trade(signal, account)
        
        if not validation_result.is_valid:
            rejection_reasons.append(validation_result.reason)
        
        # Step 4: Get risk metrics
        risk_metrics = self.risk_assessor.get_risk_metrics(account)
        
        # Step 5: Additional checks
        
        # Check if HOLD signal
        if signal.direction == OrderDirection.HOLD:
            rejection_reasons.append("Signal direction is HOLD")
        
        # Check confidence threshold (minimum 60%)
        if signal.confidence < 0.6:
            rejection_reasons.append(
                f"Confidence {signal.confidence:.1%} below minimum 60%"
            )
        
        # Determine approval
        is_approved = len(rejection_reasons) == 0
        
        # Create report
        report = RiskValidationReport(
            is_approved=is_approved,
            signal=signal,
            original_signal=original_signal,
            validation_result=validation_result,
            circuit_breaker_status=self.circuit_breaker.status,
            risk_metrics=risk_metrics,
            rejection_reasons=rejection_reasons,
            timestamp=datetime.now()
        )
        
        # Store in history
        self.validation_history.append(report)
        
        # Log result
        self._log_validation(report)
        
        return report
    
    def _log_validation(self, report: RiskValidationReport) -> None:
        """Log validation result"""
        if report.is_approved:
            print(f"\n✅ Trade APPROVED: {report.signal.pair} {report.signal.direction.value}")
            print(f"   Size: {report.signal.size:.4f}")
            print(f"   Entry: ${report.signal.entry_price:.5f}")
            print(f"   R:R: {report.signal.risk_reward_ratio:.2f}:1")
        else:
            print(f"\n❌ Trade REJECTED: {report.signal.pair} {report.signal.direction.value}")
            for reason in report.rejection_reasons:
                print(f"   - {reason}")
    
    def record_trade_close(self, pnl: float) -> None:
        """
        Record a closed trade result
        Updates circuit breaker consecutive loss counter
        
        Args:
            pnl: Profit/loss of closed trade
        """
        self.circuit_breaker.record_trade_result(pnl)
    
    def reset_circuit_breaker(self, manual: bool = True) -> bool:
        """
        Reset circuit breaker
        
        Args:
            manual: Whether this is a manual reset
            
        Returns:
            True if reset successful
        """
        return self.circuit_breaker.reset_breaker(manual)
    
    def get_validation_stats(self) -> dict:
        """
        Get validation statistics
        
        Returns:
            Dictionary with validation stats
        """
        if not self.validation_history:
            return {
                'total_validations': 0,
                'approved': 0,
                'rejected': 0,
                'approval_rate': 0.0
            }
        
        total = len(self.validation_history)
        approved = sum(1 for r in self.validation_history if r.is_approved)
        rejected = total - approved
        
        # Count rejection reasons
        rejection_counts = {}
        for report in self.validation_history:
            if not report.is_approved:
                for reason in report.rejection_reasons:
                    rejection_counts[reason] = rejection_counts.get(reason, 0) + 1
        
        return {
            'total_validations': total,
            'approved': approved,
            'rejected': rejected,
            'approval_rate': approved / total if total > 0 else 0.0,
            'rejection_reasons': rejection_counts,
            'circuit_breaker_status': self.circuit_breaker.get_status()
        }
    
    def get_recent_validations(self, limit: int = 10) -> List[RiskValidationReport]:
        """
        Get recent validation reports
        
        Args:
            limit: Maximum number of reports to return
            
        Returns:
            List of recent validation reports
        """
        return self.validation_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear validation history"""
        self.validation_history.clear()
        print(f"🗑️ Validation history cleared")


# Global instance
risk_validator = RiskValidator()
