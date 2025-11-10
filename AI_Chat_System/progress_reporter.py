"""
Progress Reporter for KeenAI-Quant
Reports trading progress and performance in natural language
"""

from typing import Dict, List
from datetime import datetime, timedelta


class ProgressReporter:
    """
    Generates natural language progress reports
    Summarizes trading performance and system status
    """
    
    def __init__(self):
        """Initialize progress reporter"""
        pass
    
    def generate_daily_summary(self, stats: Dict) -> str:
        """
        Generate daily performance summary
        
        Args:
            stats: Daily statistics
            
        Returns:
            Natural language summary
        """
        trades = stats.get('trades_today', 0)
        pnl = stats.get('pnl_today', 0.0)
        win_rate = stats.get('win_rate', 0.0)
        
        summary = f"📊 Daily Summary ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        
        if trades == 0:
            summary += "No trades executed today.\n"
        else:
            summary += f"Trades: {trades}\n"
            summary += f"P&L: {pnl:+.2f}%\n"
            summary += f"Win Rate: {win_rate:.1f}%\n"
            
            if pnl > 0:
                summary += "\n✅ Profitable day!"
            elif pnl < 0:
                summary += "\n⚠️ Loss day - review risk management"
            else:
                summary += "\n➖ Break-even day"
        
        return summary
    
    def generate_trade_report(self, trade: Dict) -> str:
        """
        Generate report for a single trade
        
        Args:
            trade: Trade information
            
        Returns:
            Trade report
        """
        pair = trade.get('pair', 'Unknown')
        direction = trade.get('direction', 'Unknown')
        pnl = trade.get('pnl', 0.0)
        duration = trade.get('duration_hours', 0)
        
        report = f"📈 Trade Report: {pair}\n\n"
        report += f"Direction: {direction}\n"
        report += f"Result: {pnl:+.2f}%\n"
        report += f"Duration: {duration:.1f} hours\n"
        
        if pnl > 0:
            report += "\n✅ Winning trade"
        else:
            report += "\n❌ Losing trade"
        
        return report
    
    def generate_weekly_summary(self, stats: Dict) -> str:
        """
        Generate weekly performance summary
        
        Args:
            stats: Weekly statistics
            
        Returns:
            Weekly summary
        """
        trades = stats.get('trades_week', 0)
        pnl = stats.get('pnl_week', 0.0)
        win_rate = stats.get('win_rate', 0.0)
        best_pair = stats.get('best_pair', 'N/A')
        
        summary = f"📊 Weekly Summary\n\n"
        summary += f"Total Trades: {trades}\n"
        summary += f"Net P&L: {pnl:+.2f}%\n"
        summary += f"Win Rate: {win_rate:.1f}%\n"
        summary += f"Best Pair: {best_pair}\n"
        
        return summary
    
    def generate_system_status(self, status: Dict) -> str:
        """
        Generate system status report
        
        Args:
            status: System status information
            
        Returns:
            Status report
        """
        report = "🤖 System Status\n\n"
        
        ai_status = status.get('ai_enabled', False)
        trading_status = status.get('trading_enabled', False)
        open_positions = status.get('open_positions', 0)
        
        report += f"AI Agent: {'✅ Active' if ai_status else '❌ Inactive'}\n"
        report += f"Trading: {'✅ Enabled' if trading_status else '⏸️ Paused'}\n"
        report += f"Open Positions: {open_positions}\n"
        
        if 'last_signal' in status:
            report += f"Last Signal: {status['last_signal']}\n"
        
        return report
    
    def generate_alert(self, alert_type: str, data: Dict) -> str:
        """
        Generate alert message
        
        Args:
            alert_type: Type of alert
            data: Alert data
            
        Returns:
            Alert message
        """
        if alert_type == 'risk_limit':
            return f"⚠️ RISK ALERT: {data.get('message', 'Risk limit reached')}"
        elif alert_type == 'new_signal':
            return f"🔔 NEW SIGNAL: {data.get('pair')} - {data.get('direction')}"
        elif alert_type == 'trade_closed':
            pnl = data.get('pnl', 0.0)
            emoji = '✅' if pnl > 0 else '❌'
            return f"{emoji} Trade Closed: {data.get('pair')} - {pnl:+.2f}%"
        else:
            return f"ℹ️ {data.get('message', 'System notification')}"
