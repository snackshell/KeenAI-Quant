"""
Base AI Agent Interface for KeenAI-Quant
Single unified agent using OpenRouter for model flexibility
"""

from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import time

from backend.models.trading_models import MarketContext, AgentPrediction, OrderDirection


class BaseAgent:
    """
    Base agent class for AI-powered trading analysis
    Uses OpenRouter for flexible model selection
    """
    
    def __init__(self, name: str, api_key: str, model: str = "deepseek/deepseek-v3.2-exp", timeout: int = 5):
        """
        Initialize agent
        
        Args:
            name: Agent name (e.g., 'KeenAgent')
            api_key: OpenRouter API key
            model: Model ID (default: deepseek/deepseek-v3.2-exp)
            timeout: Timeout in seconds for API calls
        """
        self.name = name
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.enabled = True
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.total_latency = 0.0
        self.base_url = "https://openrouter.ai/api/v1"
    
    @abstractmethod
    async def analyze(self, context: MarketContext) -> Optional[AgentPrediction]:
        """
        Analyze market context and return prediction
        
        Args:
            context: MarketContext with all market data
            
        Returns:
            AgentPrediction or None if analysis fails
        """
        pass
    
    def _build_prompt(self, context: MarketContext) -> str:
        """
        Build analysis prompt from market context
        This is a template that can be overridden by specific agents
        """
        indicators = context.indicators
        
        prompt = f"""You are an expert trading analyst. Analyze the following market data for {context.pair} and provide a trading recommendation.

Current Market Data:
- Price: ${context.current_price:.4f}
- Market Regime: {context.market_regime}

Technical Indicators:
- RSI(14): {indicators.get('rsi_14', 0):.2f}
- MACD: {indicators.get('macd', 0):.4f}
- MACD Signal: {indicators.get('macd_signal', 0):.4f}
- MACD Histogram: {indicators.get('macd_histogram', 0):.4f}
- ADX(14): {indicators.get('adx_14', 0):.2f}
- ATR(14): {indicators.get('atr_14', 0):.4f}
- Bollinger Bands: Upper={indicators.get('bb_upper', 0):.4f}, Middle={indicators.get('bb_middle', 0):.4f}, Lower={indicators.get('bb_lower', 0):.4f}
- EMA(9): {indicators.get('ema_9', 0):.4f}
- EMA(21): {indicators.get('ema_21', 0):.4f}
- EMA(55): {indicators.get('ema_55', 0):.4f}
- Stochastic K: {indicators.get('stoch_k', 0):.2f}
- Williams %R: {indicators.get('williams_r', 0):.2f}

Current Positions: {len(context.current_positions)} open position(s)
Account Balance: ${context.account_balance:.2f}

Based on this analysis, should we BUY, SELL, or HOLD?

Respond in this exact format:
SIGNAL: [BUY/SELL/HOLD]
CONFIDENCE: [0-100]
REASONING: [Your detailed analysis in 2-3 sentences]

Be decisive and provide clear reasoning based on the technical indicators."""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Optional[tuple]:
        """
        Parse AI response into signal, confidence, and reasoning
        
        Returns:
            Tuple of (signal, confidence, reasoning) or None if parsing fails
        """
        try:
            lines = response_text.strip().split('\n')
            signal = None
            confidence = None
            reasoning = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('SIGNAL:'):
                    signal_text = line.split(':', 1)[1].strip().upper()
                    if 'BUY' in signal_text:
                        signal = OrderDirection.BUY
                    elif 'SELL' in signal_text:
                        signal = OrderDirection.SELL
                    else:
                        signal = OrderDirection.HOLD
                        
                elif line.startswith('CONFIDENCE:'):
                    conf_text = line.split(':', 1)[1].strip()
                    # Extract number from text
                    import re
                    numbers = re.findall(r'\d+', conf_text)
                    if numbers:
                        confidence = float(numbers[0]) / 100.0  # Convert to 0-1 range
                        
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()
            
            # If reasoning spans multiple lines, capture it
            if reasoning and len(lines) > 3:
                reasoning_lines = []
                capture = False
                for line in lines:
                    if 'REASONING:' in line:
                        capture = True
                        reasoning_lines.append(line.split(':', 1)[1].strip())
                    elif capture and line.strip():
                        reasoning_lines.append(line.strip())
                reasoning = ' '.join(reasoning_lines)
            
            if signal and confidence is not None and reasoning:
                return (signal, confidence, reasoning)
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error parsing response from {self.name}: {e}")
            return None
    
    async def _call_with_timeout(self, coro):
        """Execute coroutine with timeout"""
        try:
            return await asyncio.wait_for(coro, timeout=self.timeout)
        except asyncio.TimeoutError:
            print(f"⏱️ {self.name} timed out after {self.timeout}s")
            self.failed_calls += 1
            return None
        except Exception as e:
            print(f"❌ {self.name} error: {e}")
            self.failed_calls += 1
            return None
    
    def get_stats(self) -> dict:
        """Get agent statistics"""
        success_rate = (self.successful_calls / self.total_calls * 100) if self.total_calls > 0 else 0
        avg_latency = (self.total_latency / self.successful_calls) if self.successful_calls > 0 else 0
        
        return {
            'name': self.name,
            'enabled': self.enabled,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': round(success_rate, 2),
            'avg_latency_ms': round(avg_latency * 1000, 2)
        }
    
    def enable(self):
        """Enable this agent"""
        self.enabled = True
        print(f"✅ {self.name} enabled")
    
    def disable(self):
        """Disable this agent"""
        self.enabled = False
        print(f"⏸️ {self.name} disabled")
