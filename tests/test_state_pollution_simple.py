from src.market_data.market_data_service import MarketDataService
from unittest.mock import patch

def test_no_state_pollution():
    """Тестирует что нет state pollution между разными символами."""
    service = MarketDataService()
    
    print("=== ТЕСТ: НЕТ STATE POLLUTION ===\n")
    
    # Mock API для разных символов
    btc_mock = [[1640995200000, "50000", "51000", "49000", "50500", "100"]] * 180
    eth_mock = [[1640995200000, "4000", "4100", "3900", "4050", "200"]] * 180
    
    with patch.object(service, '_get_klines') as mock_klines:
        # Настраиваем mock для возврата разных данных для разных символов
        def side_effect(symbol, interval, limit):
            import pandas as pd
            if symbol == "BTCUSDT":
                data = btc_mock[:limit]
            else:  # ETHUSDT
                data = eth_mock[:limit]
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume'
            ])
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
        mock_klines.side_effect = side_effect
        
        # Получаем данные для BTC
        btc_data = service.get_market_data("BTCUSDT")
        print(f"BTC Support Level: {btc_data.support_level}")
        print(f"BTC Resistance Level: {btc_data.resistance_level}")
        
        # Получаем данные для ETH
        eth_data = service.get_market_data("ETHUSDT")
        print(f"ETH Support Level: {eth_data.support_level}")
        print(f"ETH Resistance Level: {eth_data.resistance_level}")
        
        # Проверяем что данные разные
        if btc_data.support_level != eth_data.support_level:
            print("✅ НЕТ STATE POLLUTION: Данные не смешиваются между символами")
        else:
            print("❌ STATE POLLUTION: Данные смешиваются!")
        
        # Проверяем enhanced context (если будет работать)
        try:
            btc_enhanced = service.get_enhanced_context("BTCUSDT")
            print("✅ Enhanced context для BTC работает")
        except Exception as e:
            print(f"⚠️ Enhanced context ошибка: {e}")

if __name__ == "__main__":
    test_no_state_pollution()