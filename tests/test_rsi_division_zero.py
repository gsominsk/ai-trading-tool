import pandas as pd
from decimal import Decimal
from src.market_data.market_data_service import MarketDataService

# Создаем данные где цена только растет (только gains, нет losses)
rising_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 
                110, 111, 112, 113, 114, 115]  # 16 точек для RSI(14)

# Создаем DataFrame с постоянно растущими ценами
df = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-01', periods=16, freq='H'),
    'open': rising_prices,
    'high': [p + 0.5 for p in rising_prices],
    'low': [p - 0.5 for p in rising_prices],
    'close': rising_prices,
    'volume': [1000] * 16
})

print("=== ТЕСТ: RSI Division by Zero ===")
print("Данные (только рост):")
print(df[['close']].tail(10))

service = MarketDataService()

try:
    # Попытка вычислить RSI на данных с только gains
    rsi = service._calculate_rsi(df, 14)
    print(f"\nRSI результат: {rsi}")
    print("❌ ПРОБЛЕМА: RSI должен был упасть с division by zero!")
except Exception as e:
    print(f"\n✅ ОШИБКА ПОЙМАНА: {e}")
    print("Это и есть проблема division by zero в RSI!")