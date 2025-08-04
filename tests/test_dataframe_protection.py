import pandas as pd
from decimal import Decimal
from datetime import datetime
import pytest
from src.market_data.market_data_service import MarketDataSet
from src.market_data.exceptions import DataFrameValidationError

def test_dataframe_protection():
    """Комплексный тест защиты от некорректных DataFrames."""
    print("=== ТЕСТ: ЗАЩИТА ОТ НЕКОРРЕКТНЫХ DataFrames ===\n")
    
    # CASE 1: Полностью пустые DataFrames - должны быть отклонены
    empty_df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Тестируем, что пустые DataFrames отклоняются
    with pytest.raises(DataFrameValidationError) as exc_info:
        MarketDataSet(
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
    
    # Проверяем сообщение об ошибке
    if "cannot be empty" in str(exc_info.value):
        print("✅ ПУСТЫЕ DataFrames: Корректно отклонены валидацией")
    else:
        print("❌ ПУСТЫЕ DataFrames: Неожиданная ошибка")
    
    # CASE 2: DataFrames с недостаточными данными - тестируем отклонение
    short_data = [[1640995200000, 50000, 51000, 49000, 50500, 100]] * 10  # Только 10 строк
    df_short = pd.DataFrame(short_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df_short[col] = pd.to_numeric(df_short[col])
    df_short['timestamp'] = pd.to_datetime(df_short['timestamp'], unit='ms')
    df_short = df_short[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    # Тестируем, что короткие DataFrames отклоняются
    with pytest.raises(DataFrameValidationError) as exc_info2:
        MarketDataSet(
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
    
    if "must have at least" in str(exc_info2.value):
        print("✅ КОРОТКИЕ DataFrames: Корректно отклонены валидацией")
    else:
        print("❌ КОРОТКИЕ DataFrames: Неожиданная ошибка")
        
    # CASE 2B: Валидные DataFrames с достаточным количеством данных и согласованными ценами
    # Используем цены около 4000 для согласованности с MA20=4000
    valid_data = [[1640995200000 + i*3600000, 3950+i*2, 4050+i*2, 3900+i*2, 4000+i*2, 100+i] for i in range(35)]
    df_valid = pd.DataFrame(valid_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df_valid[col] = pd.to_numeric(df_valid[col])
    df_valid['timestamp'] = pd.to_datetime(df_valid['timestamp'], unit='ms')
    df_valid = df_valid[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    market_data_valid = MarketDataSet(
        symbol="ETHUSDT",
        timestamp=datetime.utcnow(),
        daily_candles=df_valid,
        h4_candles=df_valid[:15],  # 15 4H candles (минимум 10)
        h1_candles=df_valid[:20],  # 20 1H candles (минимум 10)
        rsi_14=Decimal('45.0'),
        macd_signal="bullish",
        ma_20=Decimal('4000.0'),
        ma_50=Decimal('3950.0'),
        ma_trend="uptrend",
        support_level=Decimal('3900.0'),
        resistance_level=Decimal('4100.0')
    )
    
    context_valid = market_data_valid.to_llm_context_basic()
    if "Current Price:" in context_valid and "24H Change:" in context_valid:
        print("✅ ВАЛИДНЫЕ DataFrames: Нормальная обработка")
    else:
        print("❌ ВАЛИДНЫЕ DataFrames: Проблема с обработкой")
    
    # CASE 3: Проверяем _calculate_24h_change с валидными данными
    change_valid = market_data_valid._calculate_24h_change()
    
    print(f"✅ 24H Change (валидные данные): {change_valid}")
    
    # CASE 4: DataFrame с NaN значениями - тестируем отклонение
    # Используем цены около 1.50 для согласованности с MA20=1.50
    nan_data = [[1640995200000 + i*3600000, 1.45, None, 1.40, 1.50, 100] for i in range(35)]
    df_nan = pd.DataFrame(nan_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df_nan[col] = pd.to_numeric(df_nan[col], errors='coerce')  # NaN для None
    df_nan['timestamp'] = pd.to_datetime(df_nan['timestamp'], unit='ms')
    df_nan = df_nan[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    # Тестируем, что DataFrames с NaN значениями отклоняются
    with pytest.raises(DataFrameValidationError) as exc_info3:
        MarketDataSet(
            symbol="ADAUSDT",
            timestamp=datetime.utcnow(),
            daily_candles=df_nan,
            h4_candles=df_nan[:15],   # 15 4H candles
            h1_candles=df_nan[:20],   # 20 1H candles
            rsi_14=Decimal('55.0'),
            macd_signal="bearish",
            ma_20=Decimal('1.50'),
            ma_50=Decimal('1.55'),    # MA50 > MA20 для downtrend
            ma_trend="downtrend",
            support_level=Decimal('1.40'),
            resistance_level=Decimal('1.60')
        )
    
    if "contains NaN values" in str(exc_info3.value):
        print("✅ NaN DataFrames: Корректно отклонены валидацией")
    else:
        print("❌ NaN DataFrames: Неожиданная ошибка")
    
    print("\n🎯 ВСЕ EDGE CASES ПРОТЕСТИРОВАНЫ!")

if __name__ == "__main__":
    test_dataframe_protection()