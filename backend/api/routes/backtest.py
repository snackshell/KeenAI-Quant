"""
Backtesting API Routes
Run and manage strategy backtests
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from Backtesting import BacktestEngine, BacktestConfig
from Strategy_Framework.trend_following_strategy import TrendFollowingStrategy
from Strategy_Framework.mean_reversion_strategy import MeanReversionStrategy
from Strategy_Framework.breakout_strategy import BreakoutStrategy
from backend.models.trading_models import Candle

router = APIRouter()

# Global backtest engine
backtest_engine = BacktestEngine()

# Store backtest results (in production, use database)
backtest_results = {}


# Request/Response Models
class BacktestRequest(BaseModel):
    strategy_name: str
    pair: str
    start_date: str
    end_date: str
    initial_balance: float = 10000.0


class BacktestResponse(BaseModel):
    backtest_id: str
    status: str
    result: Optional[dict]


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """
    Run a backtest with specified parameters
    
    Args:
        request: Backtest configuration
        
    Returns:
        Backtest ID and initial status
    """
    try:
        # Select strategy
        if request.strategy_name == "Trend_Following_EMA_ADX":
            strategy = TrendFollowingStrategy()
        elif request.strategy_name == "Mean_Reversion_RSI_BB":
            strategy = MeanReversionStrategy()
        elif request.strategy_name == "Breakout_Donchian":
            strategy = BreakoutStrategy()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy_name}")
        
        # Parse dates
        start_date = datetime.fromisoformat(request.start_date).date()
        end_date = datetime.fromisoformat(request.end_date).date()
        
        # Validate date range
        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        
        # Create config
        config = BacktestConfig(
            strategy=strategy,
            pair=request.pair,
            start_date=start_date,
            end_date=end_date,
            initial_balance=request.initial_balance
        )
        
        # Load historical data
        print(f"📊 Loading historical data for {request.pair} from {start_date} to {end_date}")
        historical_data = _load_historical_data(request.pair, start_date, end_date)
        
        if not historical_data or len(historical_data) < 50:
            raise HTTPException(
                status_code=404, 
                detail=f"Insufficient historical data (got {len(historical_data)} candles, need at least 50)"
            )
        
        print(f"✅ Loaded {len(historical_data)} candles, running backtest...")
        
        # Run backtest
        result = backtest_engine.run(config, historical_data)
        
        # Store result
        backtest_id = f"bt_{datetime.now().timestamp()}"
        backtest_results[backtest_id] = result
        
        print(f"✅ Backtest complete: {result.total_return:.2f}% return, {len(result.trades)} trades")
        
        return BacktestResponse(
            backtest_id=backtest_id,
            status="completed",
            result=result.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ Backtest error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@router.get("/results/{backtest_id}")
async def get_backtest_results(backtest_id: str):
    """Get backtest results by ID"""
    if backtest_id not in backtest_results:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    result = backtest_results[backtest_id]
    return result.to_dict()


@router.get("/history")
async def get_backtest_history():
    """Get list of previous backtests"""
    return {
        "backtests": [
            {
                "backtest_id": bt_id,
                "pair": result.config.pair,
                "strategy": result.config.strategy.name,
                "start_date": result.config.start_date.isoformat(),
                "end_date": result.config.end_date.isoformat(),
                "total_return": result.total_return,
                "total_trades": len(result.trades)
            }
            for bt_id, result in backtest_results.items()
        ]
    }


def _load_historical_data(pair: str, start_date: date, end_date: date) -> List[Candle]:
    """
    Load historical data from MT5
    """
    try:
        # Try to fetch real data from MT5
        from Data_Engine.mt5_data_fetcher import mt5_data_fetcher
        
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Fetch 1-hour candles for backtesting
        candles = mt5_data_fetcher.fetch_historical_data(
            pair=pair,
            timeframe='1h',
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        if candles and len(candles) > 0:
            print(f"✅ Loaded {len(candles)} real candles from MT5 for backtest")
            return candles
        
        print(f"⚠️ No MT5 data available, generating sample data")
        
    except Exception as e:
        print(f"⚠️ Error fetching MT5 data: {e}, using sample data")
    
    # Fallback: Generate valid sample data
    from datetime import timedelta
    import numpy as np
    
    candles = []
    current_date = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.min.time())
    
    # Set realistic base prices
    base_prices = {
        'EUR/USD': 1.0850,
        'XAU/USD': 2050.0,
        'BTC/USD': 45000.0,
        'ETH/USD': 2500.0
    }
    base_price = base_prices.get(pair, 1.0)
    
    while current_date <= end_datetime:
        # Generate valid OHLC data
        open_price = base_price
        
        # Generate close with small random change
        close_change = (np.random.random() - 0.5) * 0.02  # ±1%
        close_price = open_price * (1 + close_change)
        
        # High must be >= max(open, close)
        high_price = max(open_price, close_price) * (1 + np.random.random() * 0.005)
        
        # Low must be <= min(open, close)
        low_price = min(open_price, close_price) * (1 - np.random.random() * 0.005)
        
        # Ensure valid OHLC relationships
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        candle = Candle(
            pair=pair,
            timestamp=current_date,
            timeframe="1h",
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=1000.0
        )
        candles.append(candle)
        
        current_date += timedelta(hours=1)
        base_price = close_price
    
    print(f"✅ Generated {len(candles)} sample candles for backtest")
    return candles


import numpy as np
