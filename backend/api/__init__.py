"""
API Module
FastAPI routes and dependencies
"""

from backend.api.routes import trading, agents, data, performance

__all__ = ['trading', 'agents', 'data', 'performance']
