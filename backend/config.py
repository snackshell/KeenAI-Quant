"""
Configuration management for KeenAI-Quant
Loads settings from config.yaml and environment variables
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
from pydantic_settings import BaseSettings
from pydantic import Field


class AIServiceConfig(BaseSettings):
    """AI service configuration"""
    model: str
    timeout: int
    weight: float
    enabled: bool = True


class RiskConfig(BaseSettings):
    """Risk management configuration"""
    max_position_size: float = Field(default=0.25, description="Maximum position size as fraction of account")
    max_daily_loss: float = Field(default=0.05, description="Maximum daily loss as fraction of account")
    max_drawdown: float = Field(default=0.15, description="Maximum drawdown from peak")
    min_risk_reward: float = Field(default=1.5, description="Minimum risk-reward ratio")
    risk_per_trade: float = Field(default=0.02, description="Risk per trade as fraction of account")


class TradingConfig(BaseSettings):
    """Trading configuration"""
    pairs: List[str] = Field(default=["EUR/USD", "XAU/USD", "BTC/USD", "ETH/USD"])
    update_frequency: int = Field(default=1, description="Update frequency in seconds")
    trading_hours: Dict[str, str] = Field(default={"start": "00:00", "end": "23:59"})
    enabled: bool = True


class Config:
    """Main configuration class"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        # Replace environment variable placeholders
        self._replace_env_vars(self._config)
    
    def _replace_env_vars(self, config: Dict[str, Any]):
        """Recursively replace ${VAR} with environment variables"""
        for key, value in config.items():
            if isinstance(value, dict):
                self._replace_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                config[key] = os.getenv(env_var, value)
    
    @property
    def trading(self) -> TradingConfig:
        """Get trading configuration"""
        return TradingConfig(**self._config.get('trading', {}))
    
    @property
    def risk(self) -> RiskConfig:
        """Get risk configuration"""
        return RiskConfig(**self._config.get('risk', {}))
    
    @property
    def ai_services(self) -> Dict[str, AIServiceConfig]:
        """Get AI service configurations"""
        ai_config = self._config.get('ai', {})
        return {
            name: AIServiceConfig(**config)
            for name, config in ai_config.items()
        }
    
    @property
    def broker(self) -> Dict[str, Any]:
        """Get broker configuration"""
        return self._config.get('broker', {})
    
    @property
    def database(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self._config.get('database', {})
    
    @property
    def logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self._config.get('logging', {})
    
    @property
    def strategies(self) -> Dict[str, Any]:
        """Get strategy configurations"""
        return self._config.get('strategies', {})
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default


# Global configuration instance
config = Config()
