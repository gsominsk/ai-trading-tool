import pandas as pd
from decimal import Decimal
from src.market_data.market_data_service import MarketDataService

def test_rsi_edge_cases():
    """Тестирует все edge cases для RSI calculation."""
    service = MarketDataService()
    
    print("=== КОМПЛЕКСНЫЙ ТЕСТ RSI EDGE CASES ===\n")
    
    # CASE 1: Только рост (gain > 0, loss = 0)
    rising_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 
                    110, 111, 112, 113, 114, 115]
    df_rising = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
        'close': rising_prices,
        'open': rising_prices,
        'high': [p + 0.5 for p in rising_prices],
        'low': [p - 0.5 for p in rising_prices],
        'volume': [1000] * 16
    })
    
    rsi_rising = service._calculate_rsi(df_rising, 14)
    print(f"1. Только рост: RSI = {rsi_rising}")
    assert rsi_rising == Decimal('100.00'), f"Expected 100.00, got {rsi_rising}"
    
    # CASE 2: Только падение (gain = 0, loss > 0)
    falling_prices = [115, 114, 113, 112, 111, 110, 109, 108, 107, 106,
                     105, 104, 103, 102, 101, 100]
    df_falling = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
        'close': falling_prices,
        'open': falling_prices,
        'high': [p + 0.5 for p in falling_prices],
        'low': [p - 0.5 for p in falling_prices],
        'volume': [1000] * 16
    })
    
    rsi_falling = service._calculate_rsi(df_falling, 14)
    print(f"2. Только падение: RSI = {rsi_falling}")
    assert rsi_falling == Decimal('0.00'), f"Expected 0.00, got {rsi_falling}"
    
    # CASE 3: Плоская цена (gain = 0, loss = 0)
    flat_prices = [100] * 16
    df_flat = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
        'close': flat_prices,
        'open': flat_prices,
        'high': [p + 0.1 for p in flat_prices],
        'low': [p - 0.1 for p in flat_prices],
        'volume': [1000] * 16
    })
    
    rsi_flat = service._calculate_rsi(df_flat, 14)
    print(f"3. Плоская цена: RSI = {rsi_flat}")
    assert rsi_flat == Decimal('50.00'), f"Expected 50.00, got {rsi_flat}"
    
    # CASE 4: Недостаточно данных
    short_prices = [100, 101, 102]  # Только 3 точки для RSI(14)
    df_short = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=3, freq='h'),
        'close': short_prices,
        'open': short_prices,
        'high': [p + 0.5 for p in short_prices],
        'low': [p - 0.5 for p in short_prices],
        'volume': [1000] * 3
    })
    
    rsi_short = service._calculate_rsi(df_short, 14)
    print(f"4. Недостаточно данных: RSI = {rsi_short}")
    assert rsi_short == Decimal('50.00'), f"Expected 50.00, got {rsi_short}"
    
    # CASE 5: Нормальные смешанные данные
    mixed_prices = [100, 101, 99, 102, 98, 103, 97, 104, 96, 105,
                   95, 106, 94, 107, 93, 108]
    df_mixed = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
        'close': mixed_prices,
        'open': mixed_prices,
        'high': [p + 0.5 for p in mixed_prices],
        'low': [p - 0.5 for p in mixed_prices],
        'volume': [1000] * 16
    })
    
    rsi_mixed = service._calculate_rsi(df_mixed, 14)
    print(f"5. Смешанные данные: RSI = {rsi_mixed}")
    assert 0 <= rsi_mixed <= 100, f"RSI должен быть между 0 и 100, got {rsi_mixed}"
    
    print("\n✅ ВСЕ RSI EDGE CASES ПРОШЛИ ТЕСТ!")
    return True

if __name__ == "__main__":
    test_rsi_edge_cases()