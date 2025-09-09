"""
MeridianAlgo - Advanced Algorithmic Trading and Statistical Analysis

A comprehensive Python library for algorithmic trading, featuring advanced 
statistical analysis, machine learning integration, and financial modeling 
tools for quantitative finance.

Version: 2.2.0
"""

__version__ = '2.2.0'

# Core modules
from .core import *
from .statistics import *
from .ml import *
from .utils import *

# Import main classes and functions
__all__ = [
    'PortfolioOptimizer',
    'TimeSeriesAnalyzer',
    'StatisticalArbitrage',
    'RiskManager',
    'get_market_data',
    'calculate_metrics'
]
