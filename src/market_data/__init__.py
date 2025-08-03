"""
Market Data Service - Multi-timeframe cryptocurrency data aggregation.

Provides structured market data for LLM analysis:
- Level 1: 6 months daily candles (global trend)
- Level 2: 2 weeks 4H candles (medium-term analysis)  
- Level 3: 48 hours 1H candles (short-term signals)
- Technical indicators: RSI, MACD, MA(20/50)
- Market context: BTC correlation, Fear & Greed Index
"""

from .market_data_service import MarketDataService, MarketDataSet

__all__ = ["MarketDataService", "MarketDataSet"]