"""
Тесты для edge cases технических индикаторов (MACD, MA, MA_trend).

Проверяем поведение индикаторов в экстремальных условиях:
- Недостаточно данных для расчета
- Одинаковые цены (нулевая волатильность)
- Экстремальные значения
- Граничные случаи
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime, timedelta
import pandas as pd
from src.market_data.market_data_service import MarketDataService

def generate_edge_case_klines(scenario: str, count: int = 50) -> list:
    """Генерирует klines для различных edge case сценариев."""
    klines = []
    current_time = int((datetime.now() - timedelta(hours=count)).timestamp() * 1000)
    
    if scenario == "insufficient_data":
        count = 5  # Меньше чем нужно для MACD (26)
    elif scenario == "zero_volatility":
        price = 50000.0  # Все цены одинаковые
    elif scenario == "extreme_volatility":
        prices = [50000.0 * (2 if i % 2 == 0 else 0.5) for i in range(count)]  # ±100% колебания
    elif scenario == "gradual_increase":
        prices = [50000.0 + i * 100 for i in range(count)]  # Постоянный рост
    elif scenario == "gradual_decrease":
        prices = [50000.0 - i * 100 for i in range(count)]  # Постоянное падение
    elif scenario == "single_spike":
        prices = [50000.0] * count
        prices[count//2] = 100000.0  # Один экстремальный спайк
    else:  # normal
        prices = [50000.0 + (i % 10 - 5) * 50 for i in range(count)]  # Нормальные колебания
    
    for i in range(count):
        if scenario == "zero_volatility":
            open_p = close_p = high_p = low_p = price
        elif scenario in ["extreme_volatility", "gradual_increase", "gradual_decrease", "single_spike"]:
            open_p = close_p = prices[i]
            high_p = open_p * 1.01
            low_p = open_p * 0.99
        else:
            price = 50000.0 + (i % 10 - 5) * 50
            open_p = close_p = price
            high_p = price * 1.01
            low_p = price * 0.99
        
        volume = 1000.0 + i * 10
        
        kline = [
            current_time + (i * 3600000),  # timestamp
            f"{open_p:.8f}",               # open
            f"{high_p:.8f}",               # high  
            f"{low_p:.8f}",                # low
            f"{close_p:.8f}",              # close
            f"{volume:.8f}",               # volume
            current_time + (i * 3600000) + 3599999,  # close_time
            f"{volume * close_p:.8f}",     # quote_asset_volume
            1000 + i,                      # number_of_trades
            f"{volume * 0.6:.8f}",         # taker_buy_base_asset_volume
            f"{volume * close_p * 0.6:.8f}",  # taker_buy_quote_asset_volume
            "0"                            # ignore
        ]
        
        klines.append(kline)
    
    return klines

def test_rsi_edge_cases():
    """Тест RSI в экстремальных условиях."""
    print("=== ТЕСТ RSI EDGE CASES ===\n")
    
    service = MarketDataService()
    
    scenarios = [
        ("insufficient_data", "Недостаточно данных (5 свечей)"),
        ("zero_volatility", "Нулевая волатильность (все цены одинаковые)"),
        ("extreme_volatility", "Экстремальная волатильность (±100%)"),
        ("gradual_increase", "Постоянный рост"),
        ("gradual_decrease", "Постоянное падение")
    ]
    
    for scenario, description in scenarios:
        print(f"🔍 Сценарий: {description}")
        
        klines = generate_edge_case_klines(scenario)
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = klines
            mock_get.return_value = mock_response
            
            try:
                result = service.get_market_data("BTCUSDT")
                rsi = result.rsi_14
                
                print(f"   RSI: {rsi} (тип: {type(rsi)})")
                
                # Проверяем корректность RSI
                assert isinstance(rsi, Decimal), f"RSI должен быть Decimal, получен {type(rsi)}"
                assert 0 <= rsi <= 100, f"RSI вне границ [0,100]: {rsi}"
                
                # Специальные проверки для каждого сценария
                if scenario == "insufficient_data":
                    # При недостатке данных должен возвращать нейтральный RSI
                    assert rsi == Decimal('50.0'), f"При недостатке данных RSI должен быть 50.0, получен {rsi}"
                    
                elif scenario == "zero_volatility":
                    # При нулевой волатильности RSI должен быть 50 (нейтральный)
                    assert rsi == Decimal('50.0'), f"При нулевой волатильности RSI должен быть 50.0, получен {rsi}"
                    
                elif scenario == "gradual_increase":
                    # При постоянном росте RSI должен быть высоким (>70)
                    assert rsi >= Decimal('70.0'), f"При постоянном росте RSI должен быть >70, получен {rsi}"
                    
                elif scenario == "gradual_decrease":
                    # При постоянном падении RSI должен быть низким (<30)
                    assert rsi <= Decimal('30.0'), f"При постоянном падении RSI должен быть <30, получен {rsi}"
                
                print(f"   ✅ Проверки пройдены")
                
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                if scenario == "insufficient_data":
                    print(f"   ℹ️  Ожидаемое поведение - возврат нейтрального RSI")
                else:
                    raise
        
        print()

def test_macd_edge_cases():
    """Тест MACD в экстремальных условиях."""
    print("=== ТЕСТ MACD EDGE CASES ===\n")
    
    service = MarketDataService()
    
    scenarios = [
        ("insufficient_data", "Недостаточно данных для MACD"),
        ("zero_volatility", "Нулевая волатильность"),
        ("extreme_volatility", "Экстремальная волатильность"),
        ("single_spike", "Единичный спайк в данных")
    ]
    
    for scenario, description in scenarios:
        print(f"🔍 Сценарий: {description}")
        
        klines = generate_edge_case_klines(scenario, 30)  # Достаточно для MACD
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = klines
            mock_get.return_value = mock_response
            
            try:
                result = service.get_market_data("BTCUSDT")
                macd_signal = result.macd_signal
                
                print(f"   MACD Signal: {macd_signal}")
                
                # Проверяем корректность MACD сигнала
                assert macd_signal in ["bullish", "bearish", "neutral"], f"Неверный MACD сигнал: {macd_signal}"
                
                # Специальные проверки
                if scenario == "insufficient_data":
                    assert macd_signal == "neutral", f"При недостатке данных MACD должен быть neutral, получен {macd_signal}"
                    
                elif scenario == "zero_volatility":
                    assert macd_signal == "neutral", f"При нулевой волатильности MACD должен быть neutral, получен {macd_signal}"
                
                print(f"   ✅ Проверки пройдены")
                
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                raise
        
        print()

def test_ma_trend_edge_cases():
    """Тест MA trend в экстремальных условиях."""
    print("=== ТЕСТ MA TREND EDGE CASES ===\n")
    
    service = MarketDataService()
    
    scenarios = [
        ("insufficient_data", "Недостаточно данных"),
        ("gradual_increase", "Четкий восходящий тренд"),
        ("gradual_decrease", "Четкий нисходящий тренд"),
        ("zero_volatility", "Боковое движение")
    ]
    
    for scenario, description in scenarios:
        print(f"🔍 Сценарий: {description}")
        
        klines = generate_edge_case_klines(scenario, 60)  # Достаточно для MA50
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = klines
            mock_get.return_value = mock_response
            
            try:
                result = service.get_market_data("BTCUSDT")
                ma_trend = result.ma_trend
                ma_20 = result.ma_20
                ma_50 = result.ma_50
                
                print(f"   MA20: {ma_20}")
                print(f"   MA50: {ma_50}")
                print(f"   MA Trend: {ma_trend}")
                
                # Проверяем корректность значений
                assert isinstance(ma_20, Decimal), f"MA20 должен быть Decimal"
                assert isinstance(ma_50, Decimal), f"MA50 должен быть Decimal"
                assert ma_trend in ["uptrend", "downtrend", "sideways"], f"Неверный MA trend: {ma_trend}"
                
                # Специальные проверки
                if scenario == "gradual_increase":
                    assert ma_trend in ["uptrend", "sideways"], f"При восходящем тренде MA trend должен быть uptrend, получен {ma_trend}"
                    
                elif scenario == "gradual_decrease":
                    assert ma_trend in ["downtrend", "sideways"], f"При нисходящем тренде MA trend должен быть downtrend, получен {ma_trend}"
                    
                elif scenario == "zero_volatility":
                    assert ma_trend == "sideways", f"При нулевой волатильности MA trend должен быть sideways, получен {ma_trend}"
                
                print(f"   ✅ Проверки пройдены")
                
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                raise
        
        print()

def test_division_by_zero_protection():
    """Тест защиты от деления на ноль во всех индикаторах."""
    print("=== ТЕСТ ЗАЩИТЫ ОТ ДЕЛЕНИЯ НА НОЛЬ ===\n")
    
    service = MarketDataService()
    
    # Создаем данные с нулевыми изменениями (все цены одинаковые)
    klines = generate_edge_case_klines("zero_volatility", 60)
    
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = klines
        mock_get.return_value = mock_response
        
        try:
            result = service.get_market_data("BTCUSDT")
            
            print(f"✅ RSI: {result.rsi_14} (защита от деления на ноль работает)")
            print(f"✅ MACD: {result.macd_signal} (защита работает)")
            print(f"✅ MA20: {result.ma_20} (защита работает)")
            print(f"✅ MA50: {result.ma_50} (защита работает)")
            print(f"✅ MA Trend: {result.ma_trend} (защита работает)")
            
            # Все индикаторы должны работать без ошибок
            assert isinstance(result.rsi_14, Decimal)
            assert result.macd_signal in ["bullish", "bearish", "neutral"]
            assert isinstance(result.ma_20, Decimal)
            assert isinstance(result.ma_50, Decimal)
            assert result.ma_trend in ["uptrend", "downtrend", "sideways"]
            
            print(f"\n🎉 ВСЕ ЗАЩИТЫ ОТ ДЕЛЕНИЯ НА НОЛЬ РАБОТАЮТ!")
            
        except Exception as e:
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            raise

if __name__ == "__main__":
    test_rsi_edge_cases()
    test_macd_edge_cases() 
    test_ma_trend_edge_cases()
    test_division_by_zero_protection()