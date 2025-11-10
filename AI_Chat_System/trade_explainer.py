"""
Trade Explainer for KeenAI-Quant
Explains trading decisions in natural language
"""

from openai import OpenAI
from typing import Optional, Dict
import asyncio


class TradeExplainer:
    """
    Explains trading decisions and signals
    Makes AI reasoning transparent and understandable
    """
    
    def __init__(self, api_key: str, model: str = "deepseek/deepseek-r1:free"):
        """
        Initialize trade explainer
        
        Args:
            api_key: OpenRouter API key
            model: Model to use
        """
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = model
    
    async def explain_trade(self, query: str, trade_data: Optional[Dict] = None) -> str:
        """
        Explain a trade decision
        
        Args:
            query: User query about the trade
            trade_data: Trade information
            
        Returns:
            Explanation
        """
        prompt = self._build_explanation_prompt(query, trade_data)
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a trading expert explaining decisions clearly and concisely."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=400
            )
        )
        
        return response.choices[0].message.content
    
    def _build_explanation_prompt(self, query: str, trade_data: Optional[Dict]) -> str:
        """Build prompt for trade explanation"""
        prompt = f"Question: {query}\n\n"
        
        if trade_data:
            prompt += "Trade Information:\n"
            prompt += f"- Pair: {trade_data.get('pair', 'N/A')}\n"
            prompt += f"- Direction: {trade_data.get('direction', 'N/A')}\n"
            prompt += f"- Entry Price: {trade_data.get('entry_price', 'N/A')}\n"
            prompt += f"- Confidence: {trade_data.get('confidence', 'N/A')}\n"
            
            if 'reasoning' in trade_data:
                prompt += f"- AI Reasoning: {trade_data['reasoning']}\n"
            
            if 'indicators' in trade_data:
                prompt += "\nKey Indicators:\n"
                for key, value in trade_data['indicators'].items():
                    prompt += f"- {key}: {value}\n"
        
        prompt += "\nProvide a clear, educational explanation of this trading decision."
        
        return prompt
    
    async def explain_signal(self, signal_data: Dict) -> str:
        """
        Explain a trading signal
        
        Args:
            signal_data: Signal information
            
        Returns:
            Signal explanation
        """
        return await self.explain_trade("Why was this signal generated?", signal_data)
    
    async def explain_indicators(self, indicators: Dict) -> str:
        """
        Explain what indicators are showing
        
        Args:
            indicators: Technical indicators
            
        Returns:
            Indicator explanation
        """
        prompt = "Explain what these technical indicators are telling us:\n\n"
        
        for key, value in indicators.items():
            prompt += f"- {key}: {value}\n"
        
        prompt += "\nProvide a clear interpretation of these indicators."
        
        return await self.explain_trade(prompt, None)
