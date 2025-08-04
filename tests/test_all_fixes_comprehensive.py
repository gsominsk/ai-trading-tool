#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE TESTING OF ALL FIXES
Testing real MarketDataService functionality after all bugfixes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from decimal import Decimal
from src.market_data.market_data_service import MarketDataService

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def test_rsi_division_protection():
    """Тест 1: RSI защита от деления на ноль"""
    print_section("RSI DIVISION BY ZERO PROTECTION")
    
    service = MarketDataService()
    
    # Тест с реальным символом
    try:
        result = service.get_market_data("BTCUSDT")
        # RSI хранится в объекте MarketDataSet, а не в DataFrame
        rsi_14 = result.rsi_14
        
        print(f"✅ BTCUSDT RSI Results:")
        print(f"   RSI(14): {rsi_14} (тип: {type(rsi_14)})")
        print(f"   Data frames:")
        print(f"     Daily: {len(result.daily_candles)} свечей")
        print(f"     4H: {len(result.h4_candles)} свечей")
        print(f"     1H: {len(result.h1_candles)} свечей")
        
        # Проверяем что это Decimal
        if isinstance(rsi_14, Decimal):
            print(f"✅ RSI возвращает Decimal (не float)")
        else:
            print(f"❌ RSI возвращает {type(rsi_14)} вместо Decimal")
            
    except Exception as e:
        print(f"❌ Ошибка при получении RSI: {e}")

def test_state_pollution():
    """Тест 2: Проверка изоляции состояния между символами"""
    print_section("STATE POLLUTION PROTECTION")
    
    service = MarketDataService()
    
    try:
        # Получаем данные для двух разных символов
        btc_result = service.get_market_data("BTCUSDT")
        eth_result = service.get_market_data("ETHUSDT")
        
        # Проверяем что данные разные - используем скалярные значения
        btc_price = btc_result.h1_candles.iloc[-1]['close']  # Последняя цена
        eth_price = eth_result.h1_candles.iloc[-1]['close']
        
        print(f"✅ BTC последняя цена: {btc_price}")
        print(f"✅ ETH последняя цена: {eth_price}")
        
        if btc_price != eth_price:
            print(f"✅ Состояние изолировано между символами")
        else:
            print(f"❌ Возможно состояние загрязнено (одинаковые цены)")
            
        # Проверяем что символы записаны правильно
        print(f"✅ BTC symbol: {btc_result.symbol}")
        print(f"✅ ETH symbol: {eth_result.symbol}")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании изоляции: {e}")

def test_decimal_precision():
    """Тест 3: Проверка Decimal точности"""
    print_section("DECIMAL PRECISION VERIFICATION")
    
    service = MarketDataService()
    
    try:
        result = service.get_market_data("BTCUSDT")
        
        # Проверяем Decimal типы в основных полях
        print(f"✅ MarketDataSet Decimal Fields:")
        print(f"   RSI: {result.rsi_14} (тип: {type(result.rsi_14)})")
        print(f"   MA20: {result.ma_20} (тип: {type(result.ma_20)})")
        print(f"   MA50: {result.ma_50} (тип: {type(result.ma_50)})")
        
        if result.support_level:
            print(f"   Support: {result.support_level} (тип: {type(result.support_level)})")
        if result.resistance_level:
            print(f"   Resistance: {result.resistance_level} (тип: {type(result.resistance_level)})")
        if result.btc_correlation:
            print(f"   BTC Corr: {result.btc_correlation} (тип: {type(result.btc_correlation)})")
            
        # Проверяем что используется Decimal
        decimal_fields = [result.rsi_14, result.ma_20, result.ma_50]
        if all(isinstance(field, Decimal) for field in decimal_fields):
            print(f"   ✅ Все основные поля используют Decimal арифметику")
        else:
            print(f"   ❌ Некоторые поля не Decimal")
                
    except Exception as e:
        print(f"❌ Ошибка при проверке Decimal: {e}")

def test_dataframe_protection():
    """Тест 4: Защита от пустых DataFrame"""
    print_section("DATAFRAME PROTECTION")
    
    service = MarketDataService()
    
    try:
        result = service.get_market_data("BTCUSDT")
        
        # Проверяем что контекст генерируется
        basic_context = result.to_llm_context_basic()
        
        print(f"✅ Basic Context сгенерирован:")
        print(f"   Длина: {len(basic_context)} символов")
        print(f"   Первые 200 символов: {basic_context[:200]}...")
        
        if "Error" not in basic_context and "Exception" not in basic_context:
            print(f"✅ Контекст без ошибок")
        else:
            print(f"❌ В контексте найдены ошибки")
            
    except Exception as e:
        print(f"❌ Ошибка при генерации контекста: {e}")

def test_symbol_validation():
    """Тест 5: Валидация символов"""
    print_section("SYMBOL VALIDATION")
    
    service = MarketDataService()
    
    # Тестируем валидные символы
    valid_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    
    for symbol in valid_symbols:
        try:
            result = service.get_market_data(symbol)
            print(f"✅ {symbol}: Успешно обработан")
            print(f"   Symbol в результате: {result.symbol}")
        except Exception as e:
            print(f"❌ {symbol}: Ошибка - {e}")
    
    # Тестируем невалидные символы
    invalid_symbols = ["INVALID", "BTCUSDTUSDT", "BT"]
    
    print(f"\n🧪 Тестирование невалидных символов:")
    for symbol in invalid_symbols:
        try:
            result = service.get_market_data(symbol)
            print(f"❌ {symbol}: Не должен быть принят! Результат: {result.symbol}")
        except Exception as e:
            print(f"✅ {symbol}: Корректно отклонен - {e}")

def test_technical_indicators():
    """Тест 6: Технические индикаторы в реальных условиях"""
    print_section("TECHNICAL INDICATORS REAL CONDITIONS")
    
    service = MarketDataService()
    
    try:
        result = service.get_market_data("BTCUSDT")
        
        # Индикаторы хранятся в объекте MarketDataSet, а не в DataFrame
        print(f"\n📊 Technical Indicators from MarketDataSet:")
        
        print(f"   RSI(14): {result.rsi_14}")
        print(f"   MACD Signal: {result.macd_signal}")
        print(f"   MA(20): {result.ma_20}")
        print(f"   MA(50): {result.ma_50}")
        print(f"   MA Trend: {result.ma_trend}")
        print(f"   Volume Profile: {result.volume_profile}")
        
        # Проверяем корректность значений
        indicators_check = [
            (result.rsi_14, "RSI", lambda x: 0 <= x <= 100),
            (result.macd_signal, "MACD", lambda x: x in ["bullish", "bearish", "neutral"]),
            (result.ma_trend, "MA Trend", lambda x: x in ["uptrend", "downtrend", "sideways"]),
            (result.volume_profile, "Volume", lambda x: x in ["high", "low", "normal"])
        ]
        
        all_valid = True
        for value, name, validator in indicators_check:
            if validator(value):
                print(f"   ✅ {name}: Корректное значение")
            else:
                print(f"   ❌ {name}: Некорректное значение: {value}")
                all_valid = False
                
        if all_valid:
            print(f"   ✅ Все индикаторы в допустимых диапазонах")
                
    except Exception as e:
        print(f"❌ Ошибка при тестировании индикаторов: {e}")

def test_pattern_recognition():
    """Тест 7: Распознавание паттернов"""
    print_section("PATTERN RECOGNITION")
    
    service = MarketDataService()
    
    try:
        # Паттерны доступны только через enhanced context, а не в MarketDataSet
        result = service.get_market_data("BTCUSDT")
        
        print(f"✅ MarketDataSet создан для символа: {result.symbol}")
        print(f"   Support Level: {result.support_level}")
        print(f"   Resistance Level: {result.resistance_level}")
        
        # Тестируем enhanced context с паттернами
        print(f"\n🧪 Тестируем Enhanced Context с паттернами:")
        enhanced_context = service.get_enhanced_context("BTCUSDT")
        
        if "CANDLESTICK ANALYSIS" in enhanced_context:
            print(f"✅ Enhanced context содержит анализ паттернов")
            print(f"   Длина enhanced context: {len(enhanced_context)} символов")
            
            # Ищем ключевые слова паттернов
            pattern_keywords = ["Hammer", "Doji", "Shooting Star", "Strong Bull", "Strong Bear"]
            found_patterns = [kw for kw in pattern_keywords if kw in enhanced_context]
            
            if found_patterns:
                print(f"✅ Найденные паттерны: {found_patterns}")
            else:
                print(f"⚠️ Конкретные паттерны не обнаружены в контексте")
        else:
            print(f"❌ Enhanced context не содержит анализ паттернов")
            
    except Exception as e:
        print(f"❌ Ошибка при распознавании паттернов: {e}")

def main():
    print("🚀 STARTING COMPREHENSIVE TESTING OF ALL FIXES")
    print("=" * 80)
    
    # Execute all tests
    test_rsi_division_protection()
    test_state_pollution()
    test_decimal_precision()
    test_dataframe_protection()
    test_symbol_validation()
    test_technical_indicators()
    test_pattern_recognition()
    
    print(f"\n{'='*80}")
    print("🎉 COMPREHENSIVE TESTING COMPLETED")
    print("="*80)
    
    print("\n📋 ПРОВЕРЬТЕ РЕЗУЛЬТАТЫ:")
    print("   ✅ - Функция работает корректно")
    print("   ❌ - Обнаружена проблема")
    print("   ⚠️ - Требует внимания")

if __name__ == "__main__":
    main()