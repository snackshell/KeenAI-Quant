"""
Trading API Routes
Control trading system and get trading information
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from main_orchestrator import main_orchestrator
from Broker_Integration.account_manager import account_manager
from Broker_Integration.position_manager import position_manager
from Broker_Integration.order_manager import order_manager

router = APIRouter()


# Request/Response Models
class TradingControlResponse(BaseModel):
    success: bool
    message: str
    state: str


class AccountResponse(BaseModel):
    balance: float
    equity: float
    margin_used: float
    margin_available: float
    unrealized_pnl: float
    realized_pnl_today: float


class PositionResponse(BaseModel):
    position_id: str
    pair: str
    direction: str
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    stop_loss: float
    take_profit: float


class TradeResponse(BaseModel):
    trade_id: str
    pair: str
    direction: str
    size: float
    entry_price: float
    exit_price: Optional[float]
    pnl: Optional[float]
    opened_at: str
    closed_at: Optional[str]
    status: str


@router.post("/start", response_model=TradingControlResponse)
async def start_trading():
    """Start the trading system"""
    try:
        if main_orchestrator.state.value == "RUNNING":
            return TradingControlResponse(
                success=False,
                message="Trading system is already running",
                state=main_orchestrator.state.value
            )
        
        # Start trading in background
        import asyncio
        asyncio.create_task(main_orchestrator.start_trading())
        
        return TradingControlResponse(
            success=True,
            message="Trading system started successfully",
            state="STARTING"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", response_model=TradingControlResponse)
async def stop_trading():
    """Stop the trading system"""
    try:
        if main_orchestrator.state.value == "STOPPED":
            return TradingControlResponse(
                success=False,
                message="Trading system is already stopped",
                state=main_orchestrator.state.value
            )
        
        await main_orchestrator.stop_trading()
        
        return TradingControlResponse(
            success=True,
            message="Trading system stopped successfully",
            state=main_orchestrator.state.value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pause", response_model=TradingControlResponse)
async def pause_trading():
    """Pause the trading system"""
    try:
        await main_orchestrator.pause_trading()
        
        return TradingControlResponse(
            success=True,
            message="Trading system paused",
            state=main_orchestrator.state.value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume", response_model=TradingControlResponse)
async def resume_trading():
    """Resume the trading system"""
    try:
        await main_orchestrator.resume_trading()
        
        return TradingControlResponse(
            success=True,
            message="Trading system resumed",
            state=main_orchestrator.state.value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """Get trading system status"""
    try:
        return main_orchestrator.get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/account", response_model=AccountResponse)
async def get_account():
    """Get account information"""
    try:
        # Try to get account from account manager
        account = account_manager.get_account()
        
        if account:
            return AccountResponse(
                balance=account.balance,
                equity=account.equity,
                margin_used=account.margin_used,
                margin_available=account.margin_available,
                unrealized_pnl=account.unrealized_pnl,
                realized_pnl_today=account.realized_pnl_today
            )
        
        # Fallback: Use broker service for direct MT5 integration
        try:
            from Broker_Integration.broker_service import broker_service
            
            success, response_data, status_code = broker_service.get_account_info()
            
            if success and 'data' in response_data:
                account_data = response_data['data']
                print(f"✅ Got account from broker service - Balance: ${account_data['balance']}")
                return AccountResponse(
                    balance=account_data['balance'],
                    equity=account_data['equity'],
                    margin_used=account_data['margin'],
                    margin_available=account_data['margin_free'],
                    unrealized_pnl=account_data['profit'],
                    realized_pnl_today=0.0
                )
            
        except ImportError:
            print("❌ MetaTrader5 module not installed!")
            raise HTTPException(
                status_code=503,
                detail="MetaTrader5 package not installed. Install with: pip install MetaTrader5"
            )
        except Exception as e:
            print(f"❌ MT5 connection error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"MT5 connection failed: {str(e)}"
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions():
    """Get open positions"""
    try:
        positions = position_manager.get_all_positions()
        
        return [
            PositionResponse(
                position_id=pos.position_id,
                pair=pos.pair,
                direction=pos.direction.value,
                size=pos.size,
                entry_price=pos.entry_price,
                current_price=pos.current_price,
                unrealized_pnl=pos.unrealized_pnl,
                stop_loss=pos.stop_loss,
                take_profit=pos.take_profit
            )
            for pos in positions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(limit: int = 100):
    """Get trade history"""
    session = None
    try:
        from backend.database import db
        from backend.database.dal import TradeDAL
        
        session = db.get_session()
        trade_dal = TradeDAL(session)
        
        trades = trade_dal.get_trade_history(limit=limit)
        
        result = [
            TradeResponse(
                trade_id=trade.trade_id,
                pair=trade.pair,
                direction=trade.direction,
                size=trade.size,
                entry_price=trade.entry_price,
                exit_price=trade.exit_price,
                pnl=trade.pnl,
                opened_at=trade.opened_at.isoformat(),
                closed_at=trade.closed_at.isoformat() if trade.closed_at else None,
                status=trade.status
            )
            for trade in trades
        ]
        
        return result
        
    except ImportError as e:
        # Database not initialized, return empty list
        print(f"⚠️ Database not available: {e}")
        return []
    except Exception as e:
        print(f"❌ Error getting trades: {e}")
        import traceback
        traceback.print_exc()
        # Return empty list instead of error
        return []
    finally:
        if session:
            session.close()
