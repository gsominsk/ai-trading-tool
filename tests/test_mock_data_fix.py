"""
Fix для недостаточных mock данных в тестах MarketDataService.

Проблема: Текущие тесты используют 1-2 свечи, но RSI требует 14+ периодов,
а MA требует достаточно данных для корректного расчета.

Решение: Создать реалистичные mock данные с 50+ свечами для всех timeframes.
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime, timedelta
from src.market_data.market_data_service import MarketDataService, MarketDataSet

def generate_realistic_klines(count: int, start_price: float = 50000.0) -> list:
    """Генерирует реалистичные klines данные для тестирования.
    
    Args:
        count: Количество свечей для генерации
        start_price: Начальная цена
        
    Returns:
        List of klines в формате Binance API
    """
    klines = []
    current_price = start_price
    current_time = int((datetime.now() - timedelta(hours=count)).timestamp() * 1000)
    
    for i in range(count):
        # Реалистичные изменения цены (-2% до +2% за час)
        price_change = (i % 10 - 5) * 0.004  # -2% to +2%
        new_price = current_price * (1 + price_change)
        
        # OHLC данные
        open_price = current_price
        close_price = new_price
        high_price = max(open_price, close_price) * 1.005  # +0.5% высокий
        low_price = min(open_price, close_price) * 0.995   # -0.5% низкий
        
        # Объем (1000-5000 базовых единиц)
        volume = 1000 + (i % 40) * 100
        
        # Binance klines формат: [timestamp, open, high, low, close, volume, close_time, quote_volume, count, taker_buy_base, taker_buy_quote, ignore]
        kline = [
            current_time + (i * 3600000),  # timestamp (каждый час)
            f"{open_price:.8f}",
            f"{high_price:.8f}",
            f"{low_price:.8f}",
            f"{close_price:.8f}",
            f"{volume:.8f}",
            current_time + (i * 3600000) + 3599999,  # close_time
            f"{volume * close_price:.8f}",  # quote_asset_volume
            1000 + i,  # number_of_trades
            f"{volume * 0.6:.8f}",  # taker_buy_base_asset_volume
            f"{volume * close_price * 0.6:.8f}",  # taker_buy_quote_asset_volume
            "0"  # ignore
        ]
        
        klines.append(kline)
        current_price = new_price
    
    return klines

def test_mock_data_generation():
    """Тест генерации mock данных."""
    print("=== ТЕСТ ГЕНЕРАЦИИ MOCK ДАННЫХ ===\n")
    
    # Генерируем данные для разных timeframes
    daily_data = generate_realistic_klines(180, 50000.0)  # 6 месяцев
    h4_data = generate_realistic_klines(84, 50000.0)      # 2 недели
    h1_data = generate_realistic_klines(60, 50000.0)      # 60 часов (достаточно для MA50)
    
    print(f"✅ Daily data: {len(daily_data)} свечей")
    print(f"✅ 4H data: {len(h4_data)} свечей")
    print(f"✅ 1H data: {len(h1_data)} свечей")
    
    # Проверяем структуру первой свечи
    sample_kline = daily_data[0]
    print(f"\n📊 Структура kline:")
    print(f"   Timestamp: {sample_kline[0]}")
    print(f"   OHLC: {sample_kline[1]}-{sample_kline[2]}-{sample_kline[3]}-{sample_kline[4]}")
    print(f"   Volume: {sample_kline[5]}")
    print(f"   Всего полей: {len(sample_kline)}")
    
    # Проверяем достаточность для RSI (14 периодов)
    assert len(h1_data) >= 15, f"Недостаточно данных для RSI: {len(h1_data)} < 15"
    
    # Проверяем достаточность для MA (20, 50 периодов)
    assert len(h1_data) >= 50, f"Недостаточно данных для MA50: {len(h1_data)} < 50"
    
    print(f"\n✅ RSI calculation: {len(h1_data)} >= 15 ✓")
    print(f"✅ MA20 calculation: {len(h1_data)} >= 20 ✓")
    print(f"✅ MA50 calculation: {len(h1_data)} >= 50 ✓")
    
    return daily_data, h4_data, h1_data

def test_market_data_service_with_sufficient_mock():
    """Тест MarketDataService с достаточными mock данными."""
    print("\n=== ТЕСТ MARKETDATASERVICE С ДОСТАТОЧНЫМИ ДАННЫМИ ===\n")
    
    service = MarketDataService()
    
    # Генерируем достаточные данные
    daily_data, h4_data, h1_data = test_mock_data_generation()
    
    with patch('requests.get') as mock_get:
        # Mock response для всех API вызовов
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        
        # Возвращаем разные данные для разных endpoints
        def side_effect(*args, **kwargs):
            params = kwargs.get('params', {})
            interval = params.get('interval', '1h')
            
            mock_response_copy = Mock()
            mock_response_copy.status_code = 200
            mock_response_copy.raise_for_status.return_value = None
            
            if interval == '1d':
                mock_response_copy.json.return_value = daily_data
            elif interval == '4h':
                mock_response_copy.json.return_value = h4_data
            elif interval == '1h':
                mock_response_copy.json.return_value = h1_data
            else:
                mock_response_copy.json.return_value = h1_data
                
            return mock_response_copy
        
        mock_get.side_effect = side_effect
        
        # Тестируем получение market data
        try:
            result = service.get_market_data("BTCUSDT")
            
            print(f"✅ MarketDataSet создан успешно")
            print(f"✅ Symbol: {result.symbol}")
            print(f"✅ RSI: {result.rsi_14} (тип: {type(result.rsi_14)})")
            print(f"✅ MA20: {result.ma_20} (тип: {type(result.ma_20)})")
            print(f"✅ MA50: {result.ma_50} (тип: {type(result.ma_50)})")
            print(f"✅ MACD: {result.macd_signal}")
            print(f"✅ MA Trend: {result.ma_trend}")
            
            # Проверяем типы данных
            assert isinstance(result.rsi_14, Decimal), f"RSI должен быть Decimal, получен {type(result.rsi_14)}"
            assert isinstance(result.ma_20, Decimal), f"MA20 должен быть Decimal, получен {type(result.ma_20)}"
            assert isinstance(result.ma_50, Decimal), f"MA50 должен быть Decimal, получен {type(result.ma_50)}"
            
            # Проверяем границы RSI
            assert 0 <= result.rsi_14 <= 100, f"RSI вне границ: {result.rsi_14}"
            
            print(f"\n🎉 ТЕСТ ПРОШЕЛ! Достаточные mock данные позволяют корректно рассчитывать индикаторы.")
            
        except Exception as e:
            print(f"❌ ОШИБКА: {e}")
            raise

def test_api_structure_validation():
    """Тест корректности структуры API mock."""
    print("\n=== ТЕСТ СТРУКТУРЫ API MOCK ===\n")
    
    # Генерируем корректную структуру klines
    klines = generate_realistic_klines(5)
    
    print("🔍 Проверяем соответствие Binance API format:")
    for i, kline in enumerate(klines[:2]):  # Показываем первые 2
        print(f"   Kline {i+1}: {len(kline)} полей")
        print(f"     Timestamp: {kline[0]} ({'✓ int' if str(kline[0]).isdigit() else '✗ не int'})")
        print(f"     OHLC: {kline[1:5]} ({'✓ str' if all(isinstance(x, str) for x in kline[1:5]) else '✗ не str'})")
        print(f"     Volume: {kline[5]} ({'✓ str' if isinstance(kline[5], str) else '✗ не str'})")
    
    # Проверяем структуру
    sample_kline = klines[0]
    assert len(sample_kline) == 12, f"Kline должен содержать 12 полей, получено {len(sample_kline)}"
    assert str(sample_kline[0]).isdigit(), f"Timestamp должен быть числом: {sample_kline[0]}"
    assert all(isinstance(x, str) for x in sample_kline[1:6]), "OHLCV должны быть строками"
    
    print(f"\n✅ API структура корректна: {len(sample_kline)} полей, правильные типы данных")

if __name__ == "__main__":
    test_mock_data_generation()
    test_market_data_service_with_sufficient_mock()
    test_api_structure_validation()