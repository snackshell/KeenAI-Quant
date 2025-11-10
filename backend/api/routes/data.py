"""
Market Data API Routes
Get market data and indicators
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from Data_Engine.data_acquisition import DataAcquisition
from Data_Engine.context_builder import ContextBuilder

router = APIRouter()


# Response Models
class CandleResponse(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketContextResponse(BaseModel):
    pair: str
    current_price: float
    trend: str
    market_regime: str
    rsi_14: float
    macd_line: float
    adx_14: float
    atr_14: float
    bb_upper: float
    bb_middle: float
    bb_lower: float


@router.get("/candles/{pair}", response_model=List[CandleResponse])
async def get_candles(pair: str, timeframe: str = "5m", limit: int = 100):
    """Get recent candles for a pair"""
    try:
        # This would connect to Data Engine
        # For now, return placeholder
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context/{pair}", response_model=MarketContextResponse)
async def get_market_context(pair: str):
    """Get current market context for a pair"""
    try:
        # This would use Context Builder
        # For now, return placeholder
        raise HTTPException(status_code=501, detail="Not implemented yet")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pairs")
async def get_trading_pairs():
    """Get list of trading pairs"""
    return {
        "pairs": ["EUR/USD", "XAU/USD", "BTC/USD", "ETH/USD"]
    }
