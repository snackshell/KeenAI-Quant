"""
Natural Language Processing for KeenAI-Quant
Intent recognition and query understanding
"""

from typing import Dict, List
import re


class NaturalLanguageProcessor:
    """
    Simple NLP for understanding user queries
    Classifies intent and extracts entities
    """
    
    def __init__(self):
        """Initialize NLP processor"""
        self.intent_patterns = {
            'explain_trade': [
                r'why.*trade',
                r'explain.*decision',
                r'why.*buy',
                r'why.*sell',
                r'what.*reason'
            ],
            'market_analysis': [
                r'market.*condition',
                r'what.*market',
                r'analyze.*market',
                r'market.*trend',
                r'price.*action'
            ],
            'strategy_question': [
                r'what.*strategy',
                r'how.*strategy',
                r'explain.*strategy',
                r'strategy.*work'
            ],
            'performance': [
                r'how.*perform',
                r'profit',
                r'loss',
                r'win.*rate',
                r'performance'
            ],
            'risk': [
                r'risk',
                r'drawdown',
                r'stop.*loss',
                r'position.*size'
            ]
        }
    
    def analyze_intent(self, message: str) -> str:
        """
        Analyze user intent from message
        
        Args:
            message: User message
            
        Returns:
            Intent category
        """
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent
        
        return 'general'
    
    def extract_pair(self, message: str) -> str:
        """
        Extract trading pair from message
        
        Args:
            message: User message
            
        Returns:
            Trading pair or empty string
        """
        pairs = ['EUR/USD', 'XAU/USD', 'BTC/USD', 'ETH/USD']
        
        message_upper = message.upper()
        for pair in pairs:
            if pair in message_upper or pair.replace('/', '') in message_upper:
                return pair
        
        return ''
    
    def extract_timeframe(self, message: str) -> str:
        """
        Extract timeframe from message
        
        Args:
            message: User message
            
        Returns:
            Timeframe or empty string
        """
        timeframes = {
            '1m': ['1 minute', '1m', '1min'],
            '5m': ['5 minute', '5m', '5min'],
            '15m': ['15 minute', '15m', '15min'],
            '1h': ['1 hour', '1h', 'hourly'],
            '4h': ['4 hour', '4h'],
            '1d': ['daily', '1d', '1 day']
        }
        
        message_lower = message.lower()
        for tf, patterns in timeframes.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return tf
        
        return ''
    
    def is_question(self, message: str) -> bool:
        """Check if message is a question"""
        question_words = ['what', 'why', 'how', 'when', 'where', 'who', 'which']
        message_lower = message.lower()
        
        return (
            message.strip().endswith('?') or
            any(message_lower.startswith(word) for word in question_words)
        )
    
    def extract_entities(self, message: str) -> Dict[str, str]:
        """
        Extract all entities from message
        
        Args:
            message: User message
            
        Returns:
            Dictionary of entities
        """
        return {
            'intent': self.analyze_intent(message),
            'pair': self.extract_pair(message),
            'timeframe': self.extract_timeframe(message),
            'is_question': self.is_question(message)
        }
