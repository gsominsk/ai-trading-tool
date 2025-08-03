import pandas as pd
import numpy as np
from decimal import Decimal
from src.market_data.market_data_service import MarketDataService

# Проверим что происходит внутри RSI calculation
service = MarketDataService()

# Создаем данные где цена только растет
rising_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 
                110, 111, 112, 113, 114, 115]

df = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
    'close': rising_prices,
    'open': rising_prices,
    'high': [p + 0.5 for p in rising_prices],
    'low': [p - 0.5 for p in rising_prices],
    'volume': [1000] * 16
})

print("=== ОТЛАДКА RSI CALCULATION ===")
print("Исходные цены (только рост):")
print(df['close'].values)

# Копируем логику из _calculate_rsi
closes = df['close']
delta = closes.diff()
print(f"\nDelta (изменения цен): {delta.values}")

gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

print(f"\nGain (average): {gain.iloc[-1]}")
print(f"Loss (average): {loss.iloc[-1]}")
print(f"Loss == 0? {loss.iloc[-1] == 0}")

if loss.iloc[-1] == 0:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: Loss = 0, будет division by zero!")
    print("gain / loss =", gain.iloc[-1] / loss.iloc[-1])
else:
    rs = gain.iloc[-1] / loss.iloc[-1]
    print(f"RS = {rs}")

rsi = 100 - (100 / (1 + (gain / loss)))
print(f"RSI результат: {rsi.iloc[-1]}")

# Проверим что возвращает наш метод
method_rsi = service._calculate_rsi(df, 14)
print(f"Метод _calculate_rsi вернул: {method_rsi}")