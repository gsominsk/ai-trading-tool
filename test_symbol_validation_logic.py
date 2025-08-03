from src.market_data.market_data_service import MarketDataService

def test_symbol_validation_logic():
    """Тестирует логику валидации символов."""
    service = MarketDataService()
    
    print("=== ТЕСТ: ЛОГИКА ВАЛИДАЦИИ СИМВОЛОВ ===\n")
    
    # VALID SYMBOLS - должны пройти валидацию
    valid_symbols = [
        "BTCUSDT",    # Основная крипта
        "ETHUSDT",    # Эфириум
        "ADAUSDT",    # Кардано
        "DOTUSDT",    # Полкадот
        "SOLUSDT",    # Солана
        "LINKUSDT",   # Чейнлинк
    ]
    
    print("ТЕСТ ВАЛИДНЫХ СИМВОЛОВ:")
    for symbol in valid_symbols:
        try:
            service._validate_symbol_input(symbol)
            base = symbol.replace("USDT", "")
            print(f"✅ {symbol}: base='{base}', isalpha={base.isalpha()}")
        except ValueError as e:
            print(f"❌ {symbol}: НЕОЖИДАННАЯ ОШИБКА - {e}")
    
    print("\n" + "="*50 + "\n")
    
    # INVALID SYMBOLS - должны упасть с ошибками
    invalid_symbols = [
        ("BTC", "No USDT suffix"),
        ("ETHBTC", "Wrong suffix"),  
        ("BTC123USDT", "Contains digits"),
        ("BTC-USDT", "Contains hyphen"),
        ("BTC_USDT", "Contains underscore"),
        ("123USDT", "Starts with digit"),
        ("BTCUSDT!", "Contains exclamation"),
        ("btcusdt", "Lowercase"),
        ("", "Empty string"),
        ("USDT", "Only USDT"),
        ("BTCUSDTEXTRA", "Too long - but should this fail?"),
    ]
    
    print("ТЕСТ НЕВАЛИДНЫХ СИМВОЛОВ:")
    for symbol, reason in invalid_symbols:
        try:
            service._validate_symbol_input(symbol)
            print(f"❌ {symbol}: ПРОБЛЕМА - прошел валидацию! ({reason})")
        except ValueError as e:
            base = symbol.replace("USDT", "") if "USDT" in symbol else symbol
            isalpha_check = base.isalpha() if base else False
            print(f"✅ {symbol}: правильно отклонен - {reason}")
            print(f"   base='{base}', isalpha={isalpha_check}, error='{e}'")
    
    print("\n" + "="*50 + "\n")
    
    # EDGE CASES - специальные случаи
    edge_cases = [
        "USDTUSDT",     # USDT в начале
        "BTCUSDTUSDT",  # Двойной USDT 
        "USDTBTC",      # Обратный порядок
        "BTCUSD",       # Почти правильный
    ]
    
    print("ТЕСТ EDGE CASES:")
    for symbol in edge_cases:
        try:
            service._validate_symbol_input(symbol)
            print(f"❌ {symbol}: прошел валидацию (может быть проблема)")
        except ValueError as e:
            print(f"✅ {symbol}: отклонен - {e}")

if __name__ == "__main__":
    test_symbol_validation_logic()