"""
Chat Orchestrator for KeenAI-Quant
Manages AI chat interactions and coordinates responses
"""

from typing import Optional, List, Dict
from datetime import datetime

from .keen_chat import KeenChat
from .trade_explainer import TradeExplainer
from .natural_language import NaturalLanguageProcessor


class ChatOrchestrator:
    """
    Orchestrates AI chat system
    Handles user queries, trade explanations, and natural language processing
    """
    
    def __init__(self, api_key: str):
        """
        Initialize chat orchestrator
        
        Args:
            api_key: OpenRouter API key
        """
        self.chat = KeenChat(api_key)
        self.explainer = TradeExplainer(api_key)
        self.nlp = NaturalLanguageProcessor()
        self.conversation_history: List[Dict] = []
    
    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Process user message and generate response
        
        Args:
            message: User message
            context: Optional context (market data, trades, etc.)
            
        Returns:
            AI response
        """
        # Analyze intent
        intent = self.nlp.analyze_intent(message)
        
        # Route to appropriate handler
        if intent == 'explain_trade':
            response = await self.explainer.explain_trade(message, context)
        elif intent == 'market_analysis':
            response = await self.chat.analyze_market(message, context)
        elif intent == 'strategy_question':
            response = await self.chat.answer_strategy_question(message, context)
        else:
            response = await self.chat.general_chat(message, context)
        
        # Record conversation
        self._record_conversation(message, response)
        
        return response
    
    def _record_conversation(self, user_message: str, ai_response: str):
        """Record conversation for context"""
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'user': user_message,
            'ai': ai_response
        })
        
        # Keep last 50 messages
        if len(self.conversation_history) > 50:
            self.conversation_history.pop(0)
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
