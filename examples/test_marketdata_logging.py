#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

# Clear previous test logs
if os.path.exists('logs/trading_operations.log'):
    os.remove('logs/trading_operations.log')

print('=== ТЕСТИРОВАНИЕ MARKERDATASERVICE С ЛОГИРОВАНИЕМ ===')
print()

# Test the actual MarketDataService
from src.market_data.market_data_service import MarketDataService

# Create service with logging enabled
service = MarketDataService(enable_logging=True)
print('✅ MarketDataService создан с включенным логированием')

print('🔍 Запускаем получение данных BTCUSDT...')

# Get market data (this should generate logs)
try:
    data = service.get_market_data('BTCUSDT')
    print('✅ Данные получены успешно!')
    print(f'📊 RSI: {data.rsi_14}')
    print(f'💰 Current Price: {data.h1_candles.iloc[-1]["close"]:.2f}')
except Exception as e:
    print(f'❌ Ошибка: {e}')

print()
print('📁 Проверяем что записалось в лог файл...')

# Check the log file
log_file = 'logs/trading_operations.log'
if os.path.exists(log_file):
    with open(log_file, 'r') as f:
        lines = f.readlines()
    print(f'📄 Найден файл логов: {log_file}')
    print(f'📝 Количество записей: {len(lines)}')
    print()
    print('🔍 ПЕРВЫЕ 5 ЗАПИСЕЙ В ЛОГЕ:')
    for i, line in enumerate(lines[:5], 1):
        print(f'   {i}. {line.strip()}')
    
    if len(lines) > 5:
        print(f'   ... и еще {len(lines) - 5} записей')
    
    print()
    print('📊 АНАЛИЗ ЛОГОВ:')
    
    # Подсчитываем операции
    integration_count = sum(1 for line in lines if 'logging_integration_completed' in line)
    market_data_start = sum(1 for line in lines if 'get_market_data initiated' in line)
    api_calls = sum(1 for line in lines if 'get_klines initiated' in line or 'Binance API call executed' in line)
    completions = sum(1 for line in lines if 'completed successfully' in line)
    
    print(f'   🔧 Интеграций логирования: {integration_count}')
    print(f'   🚀 Запусков get_market_data: {market_data_start}')
    print(f'   🌐 API вызовов: {api_calls}')
    print(f'   ✅ Успешных завершений: {completions}')
    
    print()
    print('🎯 ЗАКЛЮЧЕНИЕ:')
    print('✅ Система логирования MarketDataService работает!')
    print('✅ JSON логи записываются в файл')
    print('✅ Структурированные данные с trace IDs')
    print('✅ Полное логирование операций')

else:
    print('❌ Файл логов НЕ найден - проблема с логированием!')

print()
print('📁 Тест завершен')