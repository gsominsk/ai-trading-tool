#!/usr/bin/env python3
"""
Phase 5 Logging Demo - Market Data Service Flow
Простой запуск MarketDataService для демонстрации исправленного логирования
"""

import sys
import os
sys.path.append('.')

from src.logging_system.logger_config import configure_ai_logging
from src.market_data.market_data_service import MarketDataService

print('🎯 Phase 5 Logging Demo - Market Data Service')
print('=' * 50)

# Configure DEBUG logging for FULL log with raw data
configure_ai_logging(
    log_level="DEBUG",  # DEBUG для полного лога с сырыми данными
    log_file="logs/demo_marketdata_full.log",
    console_output=True,
    filter_http_noise=True
)

# Create service
service = MarketDataService(enable_logging=True, fail_fast=False)

# Run market data flow
symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]

for symbol in symbols:
    print(f'\n📊 Getting market data for {symbol}...')
    try:
        data = service.get_market_data(symbol)
        print(f'✅ {symbol}: RSI={data.rsi_14:.2f}, Price=${data.h1_candles.iloc[-1]["close"]:.2f}')
    except Exception as e:
        print(f'❌ {symbol}: Error - {e}')

print(f'\n🎉 Demo completed! Check stderr for structured logs.')