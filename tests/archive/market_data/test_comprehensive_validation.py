"""
Comprehensive validation tests for MarketDataSet.__post_init__ method.
Tests all validation categories: timestamp, dataframes, technical indicators, 
decimal fields, optional fields, and cross-field consistency.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from src.market_data.market_data_service import MarketDataSet


class TestMarketDataSetValidation:
    """Test comprehensive validation in MarketDataSet.__post_init__"""
    
    def _create_valid_dataframe(self, num_rows=50):
        """Create a valid DataFrame for testing."""
        data = []
        base_price = 100.0
        
        for i in range(num_rows):
            # Create realistic OHLC data
            open_price = base_price + (i * 0.1)
            high_price = open_price + 2.0
            low_price = open_price - 1.5
            close_price = open_price + 0.5
            volume = 1000.0 + (i * 10)
            
            data.append({
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=num_rows-i),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })
        
        return pd.DataFrame(data)
    
    def _create_valid_market_data_set(self):
        """Create a valid MarketDataSet for testing."""
        daily_df = self._create_valid_dataframe(50)
        h4_df = self._create_valid_dataframe(30)
        h1_df = self._create_valid_dataframe(20)
        
        return MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.now(timezone.utc),
            daily_candles=daily_df,
            h4_candles=h4_df,
            h1_candles=h1_df,
            rsi_14=Decimal('55.0'),
            macd_signal="bullish",
            ma_20=Decimal('102.50'),  # Significantly above MA50 for uptrend
            ma_50=Decimal('99.80'),
            ma_trend="uptrend",
            btc_correlation=Decimal('0.75'),
            fear_greed_index=60,
            volume_profile="normal",
            support_level=Decimal('95.00'),
            resistance_level=Decimal('105.00')
        )
    
    def test_valid_market_data_set_creation(self):
        """Test that valid MarketDataSet can be created successfully."""
        market_data = self._create_valid_market_data_set()
        assert market_data.symbol == "BTCUSDT"
        assert market_data.rsi_14 == Decimal('55.0')
    
    # ========== TIMESTAMP VALIDATION TESTS ==========
    
    def test_timestamp_validation_invalid_type(self):
        """Test timestamp validation with invalid type."""
        with pytest.raises(ValueError, match="Timestamp must be a datetime object"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp="2025-01-01",  # String instead of datetime
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways"
            )
    
    def test_timestamp_validation_too_old(self):
        """Test timestamp validation with too old timestamp."""
        old_timestamp = datetime.now(timezone.utc) - timedelta(days=35)
        
        with pytest.raises(ValueError, match="Timestamp too old"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=old_timestamp,
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways"
            )
    
    def test_timestamp_validation_too_future(self):
        """Test timestamp validation with future timestamp."""
        future_timestamp = datetime.now(timezone.utc) + timedelta(hours=2)
        
        with pytest.raises(ValueError, match="Timestamp too far in future"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=future_timestamp,
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways"
            )
    
    # ========== DATAFRAME VALIDATION TESTS ==========
    
    def test_dataframe_validation_wrong_type(self):
        """Test DataFrame validation with wrong type."""
        with pytest.raises(ValueError, match="daily_candles must be a pandas DataFrame"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=[],  # List instead of DataFrame
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways"
            )
    
    def test_dataframe_validation_empty(self):
        """Test DataFrame validation with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="daily_candles cannot be empty"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=empty_df,
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways"
            )
    
    def test_dataframe_validation_insufficient_rows(self):
        """Test DataFrame validation with insufficient rows."""
        small_df = self._create_valid_dataframe(5)  # Less than minimum 30 for daily
        
        with pytest.raises(ValueError, match="daily_candles must have at least 30 rows"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=small_df,
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways"
            )
    
    def test_dataframe_validation_missing_columns(self):
        """Test DataFrame validation with missing required columns."""
        # Create DataFrame with enough rows but missing columns
        data = []
        for i in range(40):  # Enough rows to pass minimum check
            data.append({
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=40-i),
                'open': 100.0 + i,
                'high': 101.0 + i
                # Missing 'low', 'close', 'volume'
            })
        df_missing_cols = pd.DataFrame(data)
        
        with pytest.raises(ValueError, match="daily_candles missing required columns"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=df_missing_cols,
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways"
            )
    
    def test_dataframe_validation_invalid_ohlc(self):
        """Test DataFrame validation with invalid OHLC logic."""
        # Create DataFrame with enough rows but invalid OHLC
        data = []
        for i in range(40):  # Enough rows to pass minimum check
            if i == 0:  # First row has invalid OHLC
                data.append({
                    'timestamp': datetime.now(timezone.utc) - timedelta(hours=40-i),
                    'open': 100.0,
                    'high': 99.0,   # High less than open (invalid)
                    'low': 98.0,
                    'close': 101.0,  # Close higher than high (invalid)
                    'volume': 1000.0
                })
            else:  # Other rows are valid
                data.append({
                    'timestamp': datetime.now(timezone.utc) - timedelta(hours=40-i),
                    'open': 100.0 + i,
                    'high': 102.0 + i,
                    'low': 99.0 + i,
                    'close': 101.0 + i,
                    'volume': 1000.0 + i
                })
        invalid_df = pd.DataFrame(data)
        
        with pytest.raises(ValueError, match="has invalid OHLC data: high < max"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=invalid_df,
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways"
            )
    
    def test_dataframe_validation_negative_volume(self):
        """Test DataFrame validation with negative volume."""
        # Create DataFrame with enough rows but negative volume
        data = []
        for i in range(40):  # Enough rows to pass minimum check
            volume = -1000.0 if i == 0 else 1000.0 + i  # First row has negative volume
            data.append({
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=40-i),
                'open': 100.0 + i,
                'high': 102.0 + i,
                'low': 99.0 + i,
                'close': 101.0 + i,
                'volume': volume
            })
        df_negative_vol = pd.DataFrame(data)
        
        with pytest.raises(ValueError, match="has negative volume values"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=df_negative_vol,
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways"
            )
    
    # ========== DECIMAL FIELDS VALIDATION TESTS ==========
    
    def test_decimal_validation_wrong_type(self):
        """Test Decimal field validation with wrong type."""
        with pytest.raises(ValueError, match="ma_20 must be Decimal"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=100.0,  # Float instead of Decimal
                ma_50=Decimal('100.0'),
                ma_trend="sideways"
            )
    
    def test_decimal_validation_negative_value(self):
        """Test Decimal field validation with negative value."""
        with pytest.raises(ValueError, match="ma_20 must be positive"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('-100.0'),  # Negative value
                ma_50=Decimal('100.0'),
                ma_trend="sideways"
            )
    
    def test_decimal_validation_too_large(self):
        """Test Decimal field validation with unreasonably large value."""
        with pytest.raises(ValueError, match="ma_20 too large"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('2000000.0'),  # Too large
                ma_50=Decimal('100.0'),
                ma_trend="sideways"
            )
    
    # ========== OPTIONAL FIELDS VALIDATION TESTS ==========
    
    def test_btc_correlation_validation_wrong_type(self):
        """Test BTC correlation validation with wrong type."""
        with pytest.raises(ValueError, match="btc_correlation must be Decimal"):
            MarketDataSet(
                symbol="ETHUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways",
                btc_correlation=0.75  # Float instead of Decimal
            )
    
    def test_btc_correlation_validation_out_of_range(self):
        """Test BTC correlation validation with out of range value."""
        with pytest.raises(ValueError, match="btc_correlation must be between -1 and 1"):
            MarketDataSet(
                symbol="ETHUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways",
                btc_correlation=Decimal('1.5')  # Out of range
            )
    
    def test_fear_greed_validation_wrong_type(self):
        """Test Fear & Greed index validation with wrong type."""
        with pytest.raises(ValueError, match="fear_greed_index must be int"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways",
                fear_greed_index=60.5  # Float instead of int
            )
    
    def test_fear_greed_validation_out_of_range(self):
        """Test Fear & Greed index validation with out of range value."""
        with pytest.raises(ValueError, match="fear_greed_index must be between 0 and 100"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways",
                fear_greed_index=150  # Out of range
            )
    
    # ========== CROSS-FIELD CONSISTENCY VALIDATION TESTS ==========
    
    def test_support_resistance_consistency(self):
        """Test support/resistance level consistency validation."""
        with pytest.raises(ValueError, match="Support level .* must be lower than resistance level"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),
                ma_50=Decimal('100.0'),
                ma_trend="sideways",
                support_level=Decimal('110.0'),    # Higher than resistance
                resistance_level=Decimal('105.0')
            )
    
    def test_ma_trend_consistency_uptrend(self):
        """Test MA trend consistency validation for uptrend."""
        with pytest.raises(ValueError, match="MA trend is uptrend but MA20.*not significantly above MA50"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),  # Not significantly above MA50
                ma_50=Decimal('99.9'),
                ma_trend="uptrend"  # Inconsistent with MA values
            )
    
    def test_ma_trend_consistency_downtrend(self):
        """Test MA trend consistency validation for downtrend."""
        with pytest.raises(ValueError, match="MA trend is downtrend but MA20.*not significantly below MA50"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=self._create_valid_dataframe(),
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),  # Not significantly below MA50
                ma_50=Decimal('100.1'),
                ma_trend="downtrend"  # Inconsistent with MA values
            )
    
    def test_price_ma_sanity_check(self):
        """Test price vs MA sanity check validation."""
        # Create DataFrame with enough rows but price very different from MA
        data = []
        for i in range(15):  # Enough rows to pass minimum check
            if i == 14:  # Last row (recent price) very different from MA
                data.append({
                    'timestamp': datetime.now(timezone.utc) - timedelta(hours=15-i),
                    'open': 200.0,    # Price around 200
                    'high': 201.0,
                    'low': 199.0,
                    'close': 200.5,   # Recent price = 200.5
                    'volume': 1000.0
                })
            else:  # Other rows are normal
                data.append({
                    'timestamp': datetime.now(timezone.utc) - timedelta(hours=15-i),
                    'open': 100.0 + i,
                    'high': 102.0 + i,
                    'low': 99.0 + i,
                    'close': 101.0 + i,
                    'volume': 1000.0 + i
                })
        h1_df = pd.DataFrame(data)
        
        with pytest.raises(ValueError, match="Recent price.*too far from MA20"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=self._create_valid_dataframe(),
                h4_candles=self._create_valid_dataframe(),
                h1_candles=h1_df,
                rsi_14=Decimal('50.0'),
                macd_signal="neutral",
                ma_20=Decimal('100.0'),  # MA20 = 100, price = 200.5 (100% difference)
                ma_50=Decimal('100.0'),
                ma_trend="sideways"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])