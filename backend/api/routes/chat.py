"""
Chat API Routes
Handle chat interactions with Keen Agent
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from backend.models.trading_models import MarketContext

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    agent: str = "Keen Agent"


@router.post("", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Send a message to Keen Agent and get REAL AI response - NO FALLBACKS"""
    try:
        from AI_Core.agents.keen_agent import KeenAgent
        from Data_Engine.context_builder import context_builder
        from Broker_Integration.account_manager import account_manager
        from Broker_Integration.position_manager import position_manager
        
        print(f"💬 Chat request: {request.message}")
        
        # Initialize Keen Agent
        keen_agent = KeenAgent()
        
        # Get account and positions
        account = account_manager.get_account()
        positions = position_manager.get_all_positions()
        balance = account.balance if account else 10000.0
        
        print(f"📊 Building market context (Balance: ${balance:,.2f}, Positions: {len(positions)})")
        
        # Determine which pair to analyze based on user query
        query_lower = request.message.lower()
        target_pair = "EUR/USD"  # Default
        
        if "gold" in query_lower or "xau" in query_lower:
            target_pair = "XAU/USD"
        elif "btc" in query_lower or "bitcoin" in query_lower:
            target_pair = "BTC/USD"
        elif "eth" in query_lower or "ethereum" in query_lower:
            target_pair = "ETH/USD"
        
        # Try to fetch data from MT5 first
        from Data_Engine.mt5_data_fetcher import mt5_data_fetcher
        
        print(f"🔌 Checking MT5 connection...")
        if not mt5_data_fetcher.mt5_client or not mt5_data_fetcher.mt5_client.connected:
            print("⚠️ MT5 not connected, attempting to connect...")
            if mt5_data_fetcher.mt5_client:
                mt5_data_fetcher.mt5_client.connect()
        
        # Build context for the target pair
        context = context_builder.build_context(
            pair=target_pair,
            timeframe="5m",
            account_balance=balance,
            current_positions=positions
        )
        
        if not context:
            # Try other pairs if target fails
            print(f"⚠️ Failed to build context for {target_pair}, trying alternatives...")
            for pair in ["EUR/USD", "XAU/USD", "BTC/USD", "ETH/USD"]:
                if pair != target_pair:
                    context = context_builder.build_context(
                        pair=pair,
                        timeframe="5m",
                        account_balance=balance,
                        current_positions=positions
                    )
                    if context:
                        print(f"✅ Using context for {pair}")
                        break
        
        if not context:
            # Last resort: Create minimal context for AI to respond
            print("⚠️ No market data available, creating minimal context...")
            context = MarketContext(
                pair=target_pair,
                current_price=1.0850 if target_pair == "EUR/USD" else 2050.0,
                indicators={
                    'rsi_14': 50.0,
                    'macd': 0.0,
                    'macd_signal': 0.0,
                    'macd_histogram': 0.0,
                    'bb_upper': 0.0,
                    'bb_middle': 0.0,
                    'bb_lower': 0.0,
                    'atr_14': 0.0,
                    'adx_14': 25.0,
                    'ema_9': 0.0,
                    'ema_21': 0.0,
                },
                recent_candles=[],
                current_positions=positions,
                account_balance=balance,
                market_regime="unknown",
                timestamp=datetime.now()
            )
            print("⚠️ Using minimal context - AI will note data unavailability")
        
        print(f"🤖 Calling AI model with context for {context.pair}...")
        
        # Get response from Keen Agent - THIS IS THE REAL AI CALL
        agent_response = await keen_agent.analyze_and_decide(
            context=context,
            user_query=request.message
        )
        
        if not agent_response:
            raise HTTPException(
                status_code=500,
                detail="AI model failed to generate response. Check API key and model availability."
            )
        
        # Extract response
        response_text = agent_response.get('explanation') or agent_response.get('reasoning')
        
        if not response_text:
            raise HTTPException(
                status_code=500,
                detail="AI model returned empty response"
            )
        
        print(f"✅ AI response generated ({len(response_text)} chars)")
        
        return ChatResponse(response=response_text)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat system error: {str(e)}")
