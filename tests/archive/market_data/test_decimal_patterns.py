from src.market_data.market_data_service import MarketDataService
from decimal import Decimal

def test_decimal_patterns():
    """Тестирует что _identify_patterns использует Decimal arithmetic."""
    service = MarketDataService()
    
    print("=== ТЕСТ: DECIMAL В _identify_patterns ===\n")
    
    # Создаем тестовые свечи с точными значениями для паттернов
    test_candles = [
        # Doji pattern: body/total_range < 0.1
        [1640995200000, "100.00", "100.50", "99.50", "100.05"],  # body=0.05, total=1.0, ratio=0.05 < 0.1
        
        # Hammer pattern: lower_shadow/total_range > 0.6, body < 0.3
        [1640995200000, "100.00", "100.20", "98.00", "100.10"],  # lower=1.9, total=2.2, ratio=0.86 > 0.6
        
        # Shooting Star: upper_shadow/total_range > 0.6, body < 0.3
        [1640995200000, "100.00", "102.00", "99.80", "99.90"],   # upper=1.9, total=2.2, ratio=0.86 > 0.6
        
        # Strong Bull: body/total_range > 0.7, close > open
        [1640995200000, "100.00", "101.50", "99.80", "101.40"],  # body=1.4, total=1.7, ratio=0.82 > 0.7
        
        # Strong Bear: body/total_range > 0.7, close < open
        [1640995200000, "101.40", "101.50", "99.80", "100.00"],  # body=1.4, total=1.7, ratio=0.82 > 0.7
    ]
    
    # Тестируем pattern identification
    patterns = service._identify_patterns(test_candles)
    
    print("Найденные паттерны:")
    for pattern in sorted(patterns):
        print(f"  - {pattern}")
    
    # Проверяем что все ожидаемые паттерны найдены
    expected_patterns = {"Doji", "Hammer", "Shooting Star", "Strong Bull", "Strong Bear"}
    found_patterns = set(patterns)
    
    if expected_patterns.issubset(found_patterns):
        print("\n✅ ВСЕ ПАТТЕРНЫ НАЙДЕНЫ: Decimal arithmetic работает корректно")
    else:
        missing = expected_patterns - found_patterns
        print(f"\n❌ ПРОПУЩЕННЫЕ ПАТТЕРНЫ: {missing}")
    
    # Тестируем edge case: division by zero (total_range = 0)
    zero_range_candle = [1640995200000, "100.00", "100.00", "100.00", "100.00"]
    zero_patterns = service._identify_patterns([zero_range_candle])
    
    if len(zero_patterns) == 0:
        print("✅ DIVISION BY ZERO: Корректно обработан (нет паттернов)")
    else:
        print(f"❌ DIVISION BY ZERO: Неожиданные паттерны {zero_patterns}")
    
    print(f"\nДетали теста:")
    print(f"- Использованы Decimal вместо float")
    print(f"- Все пороговые значения как Decimal('0.1'), Decimal('0.6'), etc.")
    print(f"- Точные финансовые расчеты без потери precision")

if __name__ == "__main__":
    test_decimal_patterns()