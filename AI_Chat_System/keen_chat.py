"""
KeenChat - AI Chat Interface for KeenAI-Quant
Provides conversational AI for trading assistance
"""

from openai import OpenAI
from typing import Optional, Dict
import asyncio


class KeenChat:
    """
    AI chat assistant for trading
    Uses OpenRouter for flexible model selection
    """
    
    def __init__(self, api_key: str, model: str = "deepseek/deepseek-r1:free"):
        """
        Initialize KeenChat
        
        Args:
            api_key: OpenRouter API key
            model: Model to use
        """
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = model
        self.system_prompt = """You are KeenAI, an expert trading assistant for the KeenAI-Quant system.
You help traders understand market conditions, explain trading decisions, and provide insights.
Be concise, accurate, and helpful. Use trading terminology appropriately."""
    
    async def general_chat(self, message: str, context: Optional[Dict] = None) -> str:
        """
        General chat interaction
        
        Args:
            message: User message
            context: Optional context
            
        Returns:
            AI response
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": message}
        ]
        
        if context:
            context_str = f"\n\nContext: {context}"
            messages[-1]["content"] += context_str
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
        )
        
        return response.choices[0].message.content
    
    async def analyze_market(self, query: str, market_data: Optional[Dict] = None) -> str:
        """
        Analyze market conditions
        
        Args:
            query: User query about market
            market_data: Current market data
            
        Returns:
            Market analysis
        """
        prompt = f"Market Analysis Query: {query}"
        
        if market_data:
            prompt += f"\n\nCurrent Market Data:\n{self._format_market_data(market_data)}"
        
        return await self.general_chat(prompt)
    
    async def answer_strategy_question(self, question: str, context: Optional[Dict] = None) -> str:
        """
        Answer questions about trading strategies
        
        Args:
            question: Strategy question
            context: Optional context
            
        Returns:
            Strategy explanation
        """
        prompt = f"Strategy Question: {question}\n\nProvide a clear, educational answer about this trading strategy concept."
        return await self.general_chat(prompt, context)
    
    def _format_market_data(self, data: Dict) -> str:
        """Format market data for prompt"""
        formatted = []
        for key, value in data.items():
            if isinstance(value, (int, float)):
                formatted.append(f"- {key}: {value:.4f}")
            else:
                formatted.append(f"- {key}: {value}")
        return "\n".join(formatted)
