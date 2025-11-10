"""
KeenAgent - Unified AI Agent for KeenAI-Quant
Uses OpenRouter with DeepSeek V3.2 (or any other model)
Supports easy model switching and tool calling
"""

from openai import OpenAI
from typing import Optional, Dict, Any
from datetime import datetime
import time
import json
import asyncio
import os

from backend.models.trading_models import MarketContext, AgentPrediction, OrderDirection
from .base_agent import BaseAgent


class KeenAgent(BaseAgent):
    """
    Unified AI agent using OpenRouter
    Default model: DeepSeek V3.2 Exp (ultra-cheap and powerful)
    Can switch to any OpenRouter model by changing model ID
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "deepseek/deepseek-r1:free",
        timeout: int = 5,
        site_url: str = "https://keenai-quant.local",
        site_name: str = "KeenAI-Quant"
    ):
        # Get API key from parameter or environment or hardcoded
        if not api_key:
            api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            # Hardcoded API key as fallback
            api_key = "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"
        
        super().__init__(name='KeenAgent', api_key=api_key, model=model, timeout=timeout)
        
        # Initialize OpenAI client with OpenRouter base URL
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=api_key
        )
        
        # Optional headers for OpenRouter rankings
        self.extra_headers = {
            "HTTP-Referer": site_url,
            "X-Title": site_name
        }
        
        print(f"✅ KeenAgent initialized with model: {model}")
        print(f"🔑 API Key: {api_key[:20]}...")
    
    def _build_trading_prompt(self, context: MarketContext) -> str:
        """
        Build comprehensive trading analysis prompt
        Optimized for DeepSeek V3.2's capabilities
        """
        indicators = context.indicators
        
        prompt = f"""Analyze this trading opportunity for {context.pair} and provide a clear trading decision.

MARKET DATA:
- Current Price: ${context.current_price:.4f}
- Market Regime: {context.market_regime}
- Open Positions: {len(context.current_positions)}

TECHNICAL INDICATORS:
Momentum:
- RSI(14): {indicators.get('rsi_14', 0):.2f} (Oversold<30, Overbought>70)
- Stochastic K: {indicators.get('stoch_k', 0):.2f}
- Williams %R: {indicators.get('williams_r', 0):.2f}

Trend:
- MACD: {indicators.get('macd', 0):.4f}
- MACD Signal: {indicators.get('macd_signal', 0):.4f}
- MACD Histogram: {indicators.get('macd_histogram', 0):.4f}
- ADX(14): {indicators.get('adx_14', 0):.2f} (Strong trend>25)
- EMA(9): {indicators.get('ema_9', 0):.4f}
- EMA(21): {indicators.get('ema_21', 0):.4f}
- EMA(55): {indicators.get('ema_55', 0):.4f}

Volatility:
- ATR(14): {indicators.get('atr_14', 0):.4f}
- Bollinger Upper: {indicators.get('bb_upper', 0):.4f}
- Bollinger Middle: {indicators.get('bb_middle', 0):.4f}
- Bollinger Lower: {indicators.get('bb_lower', 0):.4f}

TRADING DECISION REQUIRED:
Based on technical analysis, should we BUY, SELL, or HOLD?

Respond in this EXACT format:
SIGNAL: [BUY/SELL/HOLD]
CONFIDENCE: [0-100]
REASONING: [Your 2-3 sentence analysis focusing on key indicators]

Be decisive and data-driven."""
        
        return prompt
    
    async def analyze(self, context: MarketContext) -> Optional[AgentPrediction]:
        """
        Analyze market using OpenRouter + DeepSeek V3.2
        
        Args:
            context: MarketContext with all market data
            
        Returns:
            AgentPrediction or None if analysis fails
        """
        if not self.enabled:
            return None
        
        start_time = time.time()
        self.total_calls += 1
        
        try:
            # Build prompt
            prompt = self._build_trading_prompt(context)
            
            # Make API call using OpenAI SDK with OpenRouter
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert trading analyst. Provide clear, decisive trading signals based on technical analysis. Always respond in the exact format requested."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=300,
                    extra_headers=self.extra_headers
                )
            )
            
            # Extract response
            response_text = response.choices[0].message.content
            
            # Parse response
            parsed = self._parse_response(response_text)
            if not parsed:
                print(f"⚠️ Failed to parse {self.name} response")
                self.failed_calls += 1
                return None
            
            signal, confidence, reasoning = parsed
            
            # Record success
            self.successful_calls += 1
            latency = time.time() - start_time
            self.total_latency += latency
            
            # Create prediction
            prediction = AgentPrediction(
                agent_name=self.name,
                signal=signal,
                confidence=confidence,
                reasoning=reasoning,
                timestamp=datetime.now()
            )
            
            print(f"✅ {self.name} ({self.model}): {signal.value} ({confidence:.0%} confidence) - {latency:.2f}s")
            
            return prediction
            
        except Exception as e:
            print(f"❌ {self.name} error: {e}")
            self.failed_calls += 1
            return None
    
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
    
    def switch_model(self, new_model: str):
        """
        Switch to a different model
        
        Args:
            new_model: New model ID (e.g., 'anthropic/claude-3.5-sonnet', 'google/gemini-2.0-flash-001')
        """
        old_model = self.model
        self.model = new_model
        print(f"🔄 {self.name} switched from {old_model} to {new_model}")
    
    async def analyze_and_decide(
        self, 
        context: MarketContext, 
        user_query: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze market and respond to user query using AI
        
        Args:
            context: Market context with indicators and data
            user_query: Optional user question
            
        Returns:
            Dict with 'explanation' or 'reasoning' key containing AI response
        """
        if not self.enabled:
            return None
        
        start_time = time.time()
        self.total_calls += 1
        
        try:
            # Build comprehensive prompt with market data
            indicators = context.indicators
            
            system_prompt = """You are KeenAI, an expert trading analyst and market advisor. 
You analyze real-time market data using technical indicators and provide clear, actionable insights.
Always base your analysis on the provided market data and indicators.
Be specific, data-driven, and helpful."""
            
            market_data = f"""
CURRENT MARKET DATA FOR {context.pair}:
- Current Price: ${context.current_price:.4f}
- Market Regime: {context.market_regime}
- Account Balance: ${context.account_balance:,.2f}
- Open Positions: {len(context.current_positions)}

TECHNICAL INDICATORS:
Momentum:
- RSI(14): {indicators.get('rsi_14', 0):.2f} (Oversold<30, Neutral:30-70, Overbought>70)
- Stochastic K: {indicators.get('stoch_k', 0):.2f}

Trend:
- MACD: {indicators.get('macd', 0):.4f}
- MACD Signal: {indicators.get('macd_signal', 0):.4f}
- MACD Histogram: {indicators.get('macd_histogram', 0):.4f}
- ADX(14): {indicators.get('adx_14', 0):.2f} (Weak<20, Moderate:20-25, Strong>25)
- EMA(9): {indicators.get('ema_9', 0):.4f}
- EMA(21): {indicators.get('ema_21', 0):.4f}

Volatility & Support/Resistance:
- ATR(14): {indicators.get('atr_14', 0):.4f}
- Bollinger Upper: {indicators.get('bb_upper', 0):.4f}
- Bollinger Middle: {indicators.get('bb_middle', 0):.4f}
- Bollinger Lower: {indicators.get('bb_lower', 0):.4f}
"""
            
            user_message = f"{market_data}\n\nUser Question: {user_query if user_query else 'Analyze current market conditions'}"
            
            # Make API call
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=500,
                    extra_headers=self.extra_headers
                )
            )
            
            # Extract response
            response_text = response.choices[0].message.content.strip()
            
            # Record success
            self.successful_calls += 1
            latency = time.time() - start_time
            self.total_latency += latency
            
            print(f"✅ {self.name} chat response generated in {latency:.2f}s")
            
            return {
                'explanation': response_text,
                'reasoning': response_text,
                'model': self.model,
                'latency': latency
            }
            
        except Exception as e:
            print(f"❌ {self.name} chat error: {e}")
            import traceback
            traceback.print_exc()
            self.failed_calls += 1
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        success_rate = (self.successful_calls / self.total_calls * 100) if self.total_calls > 0 else 0
        avg_latency = (self.total_latency / self.successful_calls) if self.successful_calls > 0 else 0
        
        return {
            'name': self.name,
            'model': self.model,
            'enabled': self.enabled,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': round(success_rate, 2),
            'avg_latency_ms': round(avg_latency * 1000, 2)
        }


# Convenience function to create agent
def create_keen_agent(
    api_key: str,
    model: str = "deepseek/deepseek-r1:free"
) -> KeenAgent:
    """
    Create a KeenAgent instance
    
    Args:
        api_key: OpenRouter API key
        model: Model ID (default: deepseek/deepseek-r1:free)
        
    Returns:
        KeenAgent instance
    """
    return KeenAgent(api_key=api_key, model=model)
