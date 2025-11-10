"""
KeenHandler - Unified AI Handler for KeenAI-Quant
Uses OpenRouter with DeepSeek models
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class KeenHandler:
    """
    Unified AI handler using OpenRouter
    Supports DeepSeek R1 (free) and DeepSeek V3.2 (paid)
    """
    
    def __init__(self, api_key=None, model="deepseek/deepseek-r1:free"):
        """
        Initialize KeenHandler
        
        Args:
            api_key: OpenRouter API key (or from OPENROUTER_API_KEY env var)
            model: Model to use (default: deepseek/deepseek-r1:free)
        """
        if api_key is None:
            api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OpenRouter API key not found. Set the OPENROUTER_API_KEY environment variable.")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = model

    def analyze_market(self, market_data, news_data):
        """
        Analyze market data and news
        
        Args:
            market_data: Market data dictionary
            news_data: News data
            
        Returns:
            Analysis string
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert trading analyst."},
                {"role": "user", "content": f"Analyze the following market data and news: {market_data}, {news_data}"},
            ],
            stream=False,
        )
        return response.choices[0].message.content

    def explain(self, prompt):
        """
        Explain a trading concept or decision
        
        Args:
            prompt: Question or topic to explain
            
        Returns:
            Explanation string
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful trading assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=False,
        )
        return response.choices[0].message.content

    def analyze_sentiment_batch(self, news_texts):
        """
        Analyze sentiment of news texts
        
        Args:
            news_texts: List of news text strings
            
        Returns:
            Sentiment score dictionary
        """
        # Simple sentiment analysis using AI
        prompt = f"Analyze the sentiment of these news items and return a score from -1 (very negative) to 1 (very positive):\n\n{news_texts}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a sentiment analysis expert. Return only a number between -1 and 1."},
                {"role": "user", "content": prompt},
            ],
            stream=False,
        )
        
        try:
            score = float(response.choices[0].message.content.strip())
            return {"score": max(-1.0, min(1.0, score))}
        except:
            return {"score": 0.0}
