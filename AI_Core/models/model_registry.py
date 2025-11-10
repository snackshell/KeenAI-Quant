"""
Model Registry for KeenAI-Quant
Manages available OpenRouter models and their configurations
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ModelInfo:
    """Information about an available model"""
    id: str
    name: str
    provider: str
    context_length: int
    cost_per_1m_tokens: float
    description: str
    is_free: bool = False


class ModelRegistry:
    """
    Registry of available OpenRouter models
    Makes it easy to switch between different AI models
    """
    
    def __init__(self):
        """Initialize model registry with available DeepSeek models"""
        self.models: Dict[str, ModelInfo] = {
            # Free Model (Primary)
            "deepseek/deepseek-r1:free": ModelInfo(
                id="deepseek/deepseek-r1:free",
                name="DeepSeek R1 Free",
                provider="DeepSeek",
                context_length=64000,
                cost_per_1m_tokens=0.0,
                description="Free reasoning model, excellent for trading analysis (PRIMARY)",
                is_free=True
            ),
            
            # Paid Model (For Production)
            "deepseek/deepseek-v3.2-exp": ModelInfo(
                id="deepseek/deepseek-v3.2-exp",
                name="DeepSeek V3.2 Exp",
                provider="DeepSeek",
                context_length=64000,
                cost_per_1m_tokens=0.27,
                description="Ultra-cheap, fast, and powerful (for production use)"
            ),
        }
    
    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Get model information by ID"""
        return self.models.get(model_id)
    
    def list_models(self, free_only: bool = False) -> List[ModelInfo]:
        """
        List available models
        
        Args:
            free_only: If True, only return free models
            
        Returns:
            List of ModelInfo objects
        """
        models = list(self.models.values())
        if free_only:
            models = [m for m in models if m.is_free]
        return models
    
    def get_free_models(self) -> List[ModelInfo]:
        """Get list of free models"""
        return self.list_models(free_only=True)
    
    def get_cheapest_models(self, limit: int = 5) -> List[ModelInfo]:
        """Get cheapest models sorted by cost"""
        models = list(self.models.values())
        return sorted(models, key=lambda m: m.cost_per_1m_tokens)[:limit]


# Global registry instance
model_registry = ModelRegistry()
