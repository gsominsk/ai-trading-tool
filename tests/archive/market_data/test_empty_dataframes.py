import pandas as pd
from decimal import Decimal
from datetime import datetime, timezone
from src.market_data.market_data_service import MarketDataSet

def test_empty_dataframes():
    """Тестирует поведение с пустыми DataFrames."""
    print("=== ТЕСТ: ПУСТЫЕ DataFrames ===\n")
    
    # Создаем пустые DataFrames
    empty_df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    try:
        # Попытка создать MarketDataSet с пустыми данными
        market_data = MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.now(timezone.utc),
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
        
        print("✅ MarketDataSet создан с пустыми DataFrames")
        
        # Попытка сгенерировать LLM context
        context = market_data.to_llm_context_basic()
        print("❌ ПРОБЛЕМА: to_llm_context_basic() не упал!")
        print("Контекст:", context[:100] + "...")
        
    except Exception as e:
        print(f"✅ ОШИБКА ПОЙМАНА: {type(e).__name__}: {e}")
        print("Это и есть проблема с пустыми DataFrames!")
    
    print("\n" + "="*50 + "\n")
    
    # Тестируем _calculate_24h_change с пустыми данными
    try:
        market_data = MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.now(timezone.utc),
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
        
        change_24h = market_data._calculate_24h_change()
        print(f"✅ _calculate_24h_change с пустыми данными: {change_24h}")
        
    except Exception as e:
        print(f"❌ _calculate_24h_change упал: {e}")

if __name__ == "__main__":
    test_empty_dataframes()