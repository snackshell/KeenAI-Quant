import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class QwenHandler:
    def __init__(self, api_key=None, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"):
        if api_key is None:
            api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            raise ValueError("Qwen API key not found. Set the QWEN_API_KEY environment variable.")

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def analyze_market(self, market_data, news_data):
        response = self.client.chat.completions.create(
            model="qwen-max",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Analyze the following market data and news: {market_data}, {news_data}"},
            ],
            stream=False,
        )
        return response.choices[0].message.content

    def explain(self, prompt):
        response = self.client.chat.completions.create(
            model="qwen-max",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=False,
        )
        return response.choices[0].message.content

    def analyze_sentiment_batch(self, news_texts):
        # Placeholder for batch sentiment analysis
        return {"score": 0.2}
