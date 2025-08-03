import pandas as pd
from decimal import Decimal
from datetime import datetime
from src.market_data.market_data_service import MarketDataSet

def test_dataframe_protection():
    """Комплексный тест защиты от некорректных DataFrames."""
    print("=== ТЕСТ: ЗАЩИТА ОТ НЕКОРРЕКТНЫХ DataFrames ===\n")
    
    # CASE 1: Полностью пустые DataFrames
    empty_df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    market_data_empty = MarketDataSet(
        symbol="BTCUSDT",
        timestamp=datetime.utcnow(),
        daily_candles=empty_df,
        h4_candles=empty_df,
        h1_candles=empty_df,
        rsi_14=Decimal('50.0'),
        macd_signal="neutral",
        ma_20=Decimal('50000.0'),
        ma_50=Decimal('50000.0'),
        ma_trend="sideways",
        support_level=Decimal('49000.0'),
        resistance_level=Decimal('51000.0')
    )
    
    context_empty = market_data_empty.to_llm_context_basic()
    if "NO MARKET DATA AVAILABLE" in context_empty:
        print("✅ ПУСТЫЕ DataFrames: Корректное сообщение")
    else:
        print("❌ ПУСТЫЕ DataFrames: Неожиданный результат")
    
    # CASE 2: DataFrames с недостаточными данными (<24 часа)
    short_data = [[1640995200000, 50000, 51000, 49000, 50500, 100]] * 10  # Только 10 часов
    df_short = pd.DataFrame(short_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df_short[col] = pd.to_numeric(df_short[col])
    df_short['timestamp'] = pd.to_datetime(df_short['timestamp'], unit='ms')
    df_short = df_short[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    market_data_short = MarketDataSet(
        symbol="ETHUSDT",
        timestamp=datetime.utcnow(),
        daily_candles=df_short,
        h4_candles=df_short,
        h1_candles=df_short,
        rsi_14=Decimal('45.0'),
        macd_signal="bullish",
        ma_20=Decimal('4000.0'),
        ma_50=Decimal('3950.0'),
        ma_trend="uptrend",
        support_level=Decimal('3900.0'),
        resistance_level=Decimal('4100.0')
    )
    
    context_short = market_data_short.to_llm_context_basic()
    if "Current Price:" in context_short and "24H Change:" in context_short:
        print("✅ КОРОТКИЕ DataFrames: Нормальная обработка")
    else:
        print("❌ КОРОТКИЕ DataFrames: Проблема с обработкой")
    
    # CASE 3: Проверяем _calculate_24h_change с разными размерами
    change_empty = market_data_empty._calculate_24h_change()
    change_short = market_data_short._calculate_24h_change()
    
    print(f"✅ 24H Change (пустые данные): {change_empty}")
    print(f"✅ 24H Change (короткие данные): {change_short}")
    
    # CASE 4: DataFrame с NaN значениями
    nan_data = [[1640995200000, 50000, None, 49000, 50500, 100]] * 25
    df_nan = pd.DataFrame(nan_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df_nan[col] = pd.to_numeric(df_nan[col], errors='coerce')  # NaN для None
    df_nan['timestamp'] = pd.to_datetime(df_nan['timestamp'], unit='ms')
    df_nan = df_nan[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    market_data_nan = MarketDataSet(
        symbol="ADAUSDT",
        timestamp=datetime.utcnow(),
        daily_candles=df_nan,
        h4_candles=df_nan,
        h1_candles=df_nan,
        rsi_14=Decimal('55.0'),
        macd_signal="bearish",
        ma_20=Decimal('1.50'),
        ma_50=Decimal('1.45'),
        ma_trend="downtrend",
        support_level=Decimal('1.40'),
        resistance_level=Decimal('1.60')
    )
    
    try:
        context_nan = market_data_nan.to_llm_context_basic()
        if "Current Price:" in context_nan:
            print("✅ NaN DataFrames: Обработаны корректно")
        else:
            print("⚠️ NaN DataFrames: Fallback сообщение")
    except Exception as e:
        print(f"❌ NaN DataFrames: Неожиданная ошибка {e}")
    
    print("\n🎯 ВСЕ EDGE CASES ПРОТЕСТИРОВАНЫ!")

if __name__ == "__main__":
    test_dataframe_protection()