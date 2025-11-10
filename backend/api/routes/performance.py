"""
Performance API Routes
Get system and strategy performance metrics
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
from pydantic import BaseModel

from Strategy_Framework.strategy_orchestrator import strategy_orchestrator

router = APIRouter()


# Response Models
class StrategyPerformanceResponse(BaseModel):
    name: str
    type: str
    enabled: bool
    total_signals: int
    successful_signals: int
    win_rate: float
    total_pnl: float
    avg_pnl_per_signal: float


@router.get("/strategies", response_model=List[StrategyPerformanceResponse])
async def get_strategy_performance():
    """Get performance metrics for all strategies"""
    try:
        metrics = strategy_orchestrator.get_all_performance_metrics()
        
        return [
            StrategyPerformanceResponse(
                name=data['name'],
                type=data['type'],
                enabled=data['enabled'],
                total_signals=data['total_signals'],
                successful_signals=data['successful_signals'],
                win_rate=data['win_rate'],
                total_pnl=data['total_pnl'],
                avg_pnl_per_signal=data['avg_pnl_per_signal']
            )
            for strategy_name, data in metrics.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system")
async def get_system_performance():
    """Get overall system performance"""
    try:
        from main_orchestrator import main_orchestrator
        
        status = main_orchestrator.get_system_status()
        
        return {
            "total_updates": status.get('total_updates', 0),
            "total_signals": status.get('total_signals', 0),
            "total_trades": status.get('total_trades', 0),
            "errors_count": status.get('errors_count', 0),
            "uptime": status.get('start_time', 'N/A')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/equity-curve")
async def get_equity_curve():
    """Get equity curve data for performance chart"""
    try:
        from Broker_Integration.account_manager import account_manager
        from datetime import datetime, timedelta
        
        # Get account info
        account = account_manager.get_account()
        
        if not account:
            # Return sample data if no account
            return {
                "timestamps": [],
                "equity": [],
                "balance": []
            }
        
        # Try to get from database
        try:
            from backend.database import db
            from backend.database.dal import PerformanceDAL
            
            session = db.get_session()
            perf_dal = PerformanceDAL(session)
            
            # Get last 30 days of equity data
            start_date = datetime.now() - timedelta(days=30)
            equity_data = perf_dal.get_equity_curve(start_date)
            
            session.close()
            
            if equity_data:
                return {
                    "timestamps": [point['timestamp'].isoformat() for point in equity_data],
                    "equity": [point['equity'] for point in equity_data],
                    "balance": [point['balance'] for point in equity_data]
                }
        except Exception as db_error:
            print(f"⚠️ Database not available for equity curve: {db_error}")
        
        # Fallback: Return current snapshot
        return {
            "timestamps": [datetime.now().isoformat()],
            "equity": [account.equity],
            "balance": [account.balance]
        }
        
    except Exception as e:
        print(f"❌ Error getting equity curve: {e}")
        raise HTTPException(status_code=500, detail=str(e))
