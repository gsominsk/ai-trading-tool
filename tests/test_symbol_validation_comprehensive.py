import pytest
from src.market_data.market_data_service import MarketDataService

def test_symbol_validation_comprehensive():
    """Комплексные тесты валидации символов с покрытием всех edge cases."""
    service = MarketDataService()
    
    print("=== КОМПЛЕКСНЫЙ ТЕСТ ВАЛИДАЦИИ СИМВОЛОВ ===\n")
    
    # GROUP 1: Valid symbols - должны пройти все проверки
    valid_test_cases = [
        ("BTCUSDT", "Bitcoin"),
        ("ETHUSDT", "Ethereum"),
        ("ADAUSDT", "Cardano"),
        ("DOTUSDT", "Polkadot"),
        ("SOLUSDT", "Solana"),
        ("LINKUSDT", "Chainlink"),
        ("ATOMUSDT", "Cosmos"),
        ("AVAXUSDT", "Avalanche"),
        ("MATICUSDT", "Polygon"),
        ("ALGOUSDT", "Algorand"),
    ]
    
    print("✅ ВАЛИДНЫЕ СИМВОЛЫ:")
    passed_valid = 0
    for symbol, name in valid_test_cases:
        try:
            service._validate_symbol_input(symbol)
            print(f"  ✓ {symbol} ({name})")
            passed_valid += 1
        except Exception as e:
            print(f"  ✗ {symbol} FAILED: {e}")
    
    # GROUP 2: Invalid format - общие ошибки формата
    format_error_cases = [
        ("", "Empty string"),
        ("BTC", "No USDT suffix"),
        ("ETHBTC", "Wrong suffix (BTC)"),
        ("BTCUSD", "Wrong suffix (USD)"),
        ("btcusdt", "Lowercase"),
        ("BTCUSDT!", "Special char at end"),
        ("USDT", "Only USDT"),
        ("ABCDEFGHIJKLMNOPUSDT", "Too long"),
    ]
    
    print(f"\n❌ ОШИБКИ ФОРМАТА:")
    passed_format = 0
    for symbol, reason in format_error_cases:
        try:
            service._validate_symbol_input(symbol)
            print(f"  ✗ {symbol} SHOULD FAIL: {reason}")
        except ValueError:
            print(f"  ✓ {symbol} correctly rejected ({reason})")
            passed_format += 1
    
    # GROUP 3: Invalid characters - проблемы с символами
    character_error_cases = [
        ("BTC123USDT", "Contains digits"),
        ("BTC-USDT", "Contains hyphen"), 
        ("BTC_USDT", "Contains underscore"),
        ("BTC.USDT", "Contains dot"),
        ("BTC@USDT", "Contains at-sign"),
        ("123USDT", "Starts with digit"),
        ("1BTCUSDT", "Digit at start"),
        ("BTC1USDT", "Digit in middle"),
        ("B2CUSDT", "Digit in middle"),
    ]
    
    print(f"\n🔤 ОШИБКИ СИМВОЛОВ:")
    passed_chars = 0
    for symbol, reason in character_error_cases:
        try:
            service._validate_symbol_input(symbol)
            print(f"  ✗ {symbol} SHOULD FAIL: {reason}")
        except ValueError:
            print(f"  ✓ {symbol} correctly rejected ({reason})")
            passed_chars += 1
    
    # GROUP 4: Edge cases - специальные случаи
    edge_cases = [
        ("USDTUSDT", "USDT at start"),
        ("BTCUSDTUSDT", "Double USDT"),
        ("USDTBTC", "Reverse order"),
        ("BTCUSDTEXTRA", "Text after USDT"),
        ("AAAAAAUSDT", "Very long base (6 chars)"),
        ("TOOLONGUSDT", "Very long base (7 chars)"),
        ("AUSDT", "Single letter base"),
        ("ABUSDT", "Two letter base"),
    ]
    
    print(f"\n🎯 EDGE CASES:")
    passed_edge = 0
    for symbol, reason in edge_cases:
        try:
            service._validate_symbol_input(symbol)
            print(f"  ✗ {symbol} SHOULD FAIL: {reason}")
        except ValueError:
            print(f"  ✓ {symbol} correctly rejected ({reason})")
            passed_edge += 1
    
    # SUMMARY
    total_valid = len(valid_test_cases)
    total_invalid = len(format_error_cases) + len(character_error_cases) + len(edge_cases)
    
    print(f"\n📊 СВОДКА РЕЗУЛЬТАТОВ:")
    print(f"Valid symbols: {passed_valid}/{total_valid} passed")
    print(f"Invalid symbols: {passed_format + passed_chars + passed_edge}/{total_invalid} correctly rejected")
    
    # Assertions for pytest
    assert passed_valid == total_valid, f"Not all valid symbols passed: {passed_valid}/{total_valid}"
    assert passed_format == len(format_error_cases), f"Format errors not caught properly"
    assert passed_chars == len(character_error_cases), f"Character errors not caught properly"
    assert passed_edge == len(edge_cases), f"Edge cases not handled properly"
    
    print(f"\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ! Валидация символов работает идеально.")
    
    return {
        "valid_passed": passed_valid,
        "valid_total": total_valid,
        "invalid_rejected": passed_format + passed_chars + passed_edge,
        "invalid_total": total_invalid
    }

if __name__ == "__main__":
    test_symbol_validation_comprehensive()