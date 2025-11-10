"""
Data Engine Module for KeenAI-Quant
Handles market data acquisition, technical analysis, and context building
"""

from .data_acquisition import data_acquisition, DataAcquisition
from .context_builder import context_builder, ContextBuilder
from .technical_analysis.indicators import calculate_indicators, TechnicalIndicators
from .technical_analysis.market_regime import MarketRegimeDetector

__all__ = [
    'data_acquisition',
    'DataAcquisition',
    'context_builder',
    'ContextBuilder',
    'calculate_indicators',
    'TechnicalIndicators',
    'MarketRegimeDetector'
]
