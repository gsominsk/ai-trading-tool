"""
MarketDataService - Multi-timeframe cryptocurrency market data aggregation.

Provides structured market data for LLM trading decisions with three data levels:
- Level 1: 6 months daily candles (global trend analysis)
- Level 2: 2 weeks 4H candles (medium-term patterns)
- Level 3: 100 hours 1H candles (short-term signals)

Includes technical indicators and market context for comprehensive analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, NamedTuple
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import time
import json
import os
import logging

# Updated exception and client imports
from src.infrastructure.exceptions import (
    ApiClientError,
    ValidationError,
    NetworkError,
    ProcessingError,
    SymbolValidationError,
    DataFrameValidationError,
    APIConnectionError,
    RateLimitError,
    APIResponseError,
    CalculationError,
    DataInsufficientError,
    ErrorContext
)
from src.infrastructure.binance_client import BinanceApiClient

# Direct logging imports - simplified approach
from src.logging_system import MarketDataLogger


@dataclass
class MarketDataSet:
    """Standardized market data structure for LLM analysis."""
    symbol: str
    timestamp: datetime
    
    # Multi-level price data
    daily_candles: pd.DataFrame      # 6 months daily (Level 1)
    h4_candles: pd.DataFrame         # 2 weeks 4H (Level 2)
    h1_candles: pd.DataFrame         # 100 hours 1H (Level 3)
    
    # Technical indicators (using Decimal for financial precision)
    rsi_14: Decimal
    macd_signal: str  # "bullish", "bearish", "neutral"
    ma_20: Decimal
    ma_50: Decimal
    ma_trend: str     # "uptrend", "downtrend", "sideways"
    
    # Market context
    btc_correlation: Optional[Decimal] = None
    fear_greed_index: Optional[int] = None
    volume_profile: str = "normal"  # "high", "low", "normal"
    
    # Enhanced analysis data (no state pollution)
    support_level: Optional[Decimal] = None
    resistance_level: Optional[Decimal] = None
    
    # Hierarchical tracing support
    trace_id: Optional[str] = None
    
    def __post_init__(self):
        """Comprehensive validation of all MarketDataSet fields."""
        self._validate_symbol()
        self._validate_timestamp()
        self._validate_dataframes()
        self._validate_technical_indicators()
        self._validate_decimal_fields()
        self._validate_optional_fields()
        self._validate_cross_field_consistency()
    
    def _validate_timestamp(self):
        """Validate timestamp is reasonable."""
        if not isinstance(self.timestamp, datetime):
            raise ValueError("Timestamp must be a datetime object")
        
        # Check if timestamp is not too far in the past or future
        now = datetime.now(timezone.utc)
        max_past = timedelta(days=30)  # Allow up to 30 days old data
        max_future = timedelta(hours=1)  # Allow up to 1 hour in future (timezone tolerance)
        
        if self.timestamp < now - max_past:
            raise ValueError(f"Timestamp too old: {self.timestamp}. Must be within last 30 days")
        if self.timestamp > now + max_future:
            raise ValueError(f"Timestamp too far in future: {self.timestamp}")
    
    def _validate_dataframes(self):
        """Validate all DataFrame structures and content."""
        dataframes = [
            ("daily_candles", self.daily_candles, 30),  # At least 30 days
            ("h4_candles", self.h4_candles, 10),        # At least 10 4H candles
            ("h1_candles", self.h1_candles, 10)         # At least 10 1H candles
        ]
        
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        for df_name, df, min_rows in dataframes:
            try:
                # Check DataFrame type
                if not isinstance(df, pd.DataFrame):
                    raise DataFrameValidationError(f"{df_name} must be a pandas DataFrame", df_name, "type_check")
                
                # Check for empty DataFrame
                if len(df) == 0:
                    raise DataFrameValidationError(f"{df_name} cannot be empty", df_name, "empty_check")
                
                # Check minimum row count for technical analysis
                if len(df) < min_rows:
                    raise DataFrameValidationError(f"{df_name} must have at least {min_rows} rows for analysis, got {len(df)}", df_name, "row_count")
                
                # Check required columns
                missing_cols = [col for col in required_columns if col not in df.columns]
                if missing_cols:
                    raise DataFrameValidationError(f"{df_name} missing required columns: {missing_cols}", df_name, "column_structure")
                
                # Check for numeric columns
                numeric_cols = ['open', 'high', 'low', 'close', 'volume']
                for col in numeric_cols:
                    if not pd.api.types.is_numeric_dtype(df[col]):
                        raise DataFrameValidationError(f"{df_name}.{col} must be numeric", df_name, "column_type")
                
                # Check for NaN values in critical columns
                for col in numeric_cols:
                    if df[col].isna().any():
                        raise DataFrameValidationError(f"{df_name}.{col} contains NaN values", df_name, "nan_values")
                
                # Check OHLC logic (high >= open/close, low <= open/close)
                if (df['high'] < df[['open', 'close']].max(axis=1)).any():
                    raise DataFrameValidationError(f"{df_name} has invalid OHLC data: high < max(open, close)", df_name, "ohlc_logic")
                if (df['low'] > df[['open', 'close']].min(axis=1)).any():
                    raise DataFrameValidationError(f"{df_name} has invalid OHLC data: low > min(open, close)", df_name, "ohlc_logic")
                
                # Check for non-negative volume
                if (df['volume'] < 0).any():
                    raise DataFrameValidationError(f"{df_name} has negative volume values", df_name, "volume_validation")
                    
            except DataFrameValidationError:
                # Re-raise DataFrameValidationError as-is to maintain rich context
                raise
            except Exception as e:
                # Wrap unexpected errors in DataFrameValidationError for consistency
                raise DataFrameValidationError(f"Unexpected error during {df_name} validation: {str(e)}", df_name, "unexpected_error")
    
    def _validate_symbol(self):
        """Validate symbol format."""
        try:
            if not self.symbol or not isinstance(self.symbol, str):
                raise SymbolValidationError("Symbol must be a non-empty string", symbol=str(self.symbol))
            if not self.symbol.endswith("USDT") or len(self.symbol) < 6:
                raise SymbolValidationError(f"Invalid symbol format: {self.symbol}. Expected XXXUSDT", symbol=self.symbol)
        except SymbolValidationError:
            # Re-raise SymbolValidationError as-is to maintain rich context
            raise
        except Exception as e:
            # Wrap unexpected errors in SymbolValidationError for consistency
            raise SymbolValidationError(f"Unexpected error during symbol validation: {str(e)}", symbol=str(self.symbol))
    
    def _validate_technical_indicators(self):
        """Validate technical indicator values."""
        if not (Decimal('0') <= self.rsi_14 <= Decimal('100')):
            raise ValueError(f"RSI must be between 0 and 100, got: {self.rsi_14}")
        if self.macd_signal not in ["bullish", "bearish", "neutral"]:
            raise ValueError(f"Invalid MACD signal: {self.macd_signal}")
        if self.ma_trend not in ["uptrend", "downtrend", "sideways"]:
            raise ValueError(f"Invalid MA trend: {self.ma_trend}")
    
    def _validate_decimal_fields(self):
        """Validate Decimal fields for reasonable ranges."""
        # RSI validation already done in _validate_technical_indicators
        
        # Validate MA values are positive and reasonable
        if self.ma_20 is not None:
            if not isinstance(self.ma_20, Decimal):
                raise ValueError(f"ma_20 must be Decimal, got {type(self.ma_20)}")
            if self.ma_20 <= Decimal('0'):
                raise ValueError(f"ma_20 must be positive, got {self.ma_20}")
            if self.ma_20 > Decimal('1000000'):  # Reasonable upper bound
                raise ValueError(f"ma_20 too large: {self.ma_20}")
        
        if self.ma_50 is not None:
            if not isinstance(self.ma_50, Decimal):
                raise ValueError(f"ma_50 must be Decimal, got {type(self.ma_50)}")
            if self.ma_50 <= Decimal('0'):
                raise ValueError(f"ma_50 must be positive, got {self.ma_50}")
            if self.ma_50 > Decimal('1000000'):  # Reasonable upper bound
                raise ValueError(f"ma_50 too large: {self.ma_50}")
    
    def _validate_optional_fields(self):
        """Validate optional fields when present."""
        # BTC correlation validation
        if self.btc_correlation is not None:
            if not isinstance(self.btc_correlation, Decimal):
                raise ValueError(f"btc_correlation must be Decimal, got {type(self.btc_correlation)}")
            if not (Decimal('-1') <= self.btc_correlation <= Decimal('1')):
                raise ValueError(f"btc_correlation must be between -1 and 1, got {self.btc_correlation}")
        
        # Fear & Greed Index validation
        if self.fear_greed_index is not None:
            if not isinstance(self.fear_greed_index, int):
                raise ValueError(f"fear_greed_index must be int, got {type(self.fear_greed_index)}")
            if not (0 <= self.fear_greed_index <= 100):
                raise ValueError(f"fear_greed_index must be between 0 and 100, got {self.fear_greed_index}")
        
        # Volume profile validation
        if self.volume_profile not in ["high", "low", "normal"]:
            raise ValueError(f"Invalid volume_profile: {self.volume_profile}")
        
        # Support/Resistance levels validation
        if self.support_level is not None:
            if not isinstance(self.support_level, Decimal):
                raise ValueError(f"support_level must be Decimal, got {type(self.support_level)}")
            if self.support_level <= Decimal('0'):
                raise ValueError(f"support_level must be positive, got {self.support_level}")
        
        if self.resistance_level is not None:
            if not isinstance(self.resistance_level, Decimal):
                raise ValueError(f"resistance_level must be Decimal, got {type(self.resistance_level)}")
            if self.resistance_level <= Decimal('0'):
                raise ValueError(f"resistance_level must be positive, got {self.resistance_level}")
    
    def _validate_cross_field_consistency(self):
        """Validate logical consistency between related fields."""
        # Support level should be lower than resistance level
        if (self.support_level is not None and self.resistance_level is not None):
            if self.support_level >= self.resistance_level:
                raise ValueError(f"Support level ({self.support_level}) must be lower than resistance level ({self.resistance_level})")
        
        # MA20 and MA50 trend consistency check
        if (self.ma_20 is not None and self.ma_50 is not None):
            ma_ratio = self.ma_20 / self.ma_50
            
            # Check trend consistency
            if self.ma_trend == "uptrend" and ma_ratio <= Decimal('1.01'):
                raise ValueError(f"MA trend is uptrend but MA20 ({self.ma_20}) not significantly above MA50 ({self.ma_50})")
            elif self.ma_trend == "downtrend" and ma_ratio >= Decimal('0.99'):
                raise ValueError(f"MA trend is downtrend but MA20 ({self.ma_20}) not significantly below MA50 ({self.ma_50})")
        
        # Validate price ranges in DataFrames are reasonable compared to MA values
        if len(self.h1_candles) > 0 and self.ma_20 is not None:
            recent_price = Decimal(str(self.h1_candles.iloc[-1]['close']))
            price_diff_ratio = abs(recent_price - self.ma_20) / self.ma_20
            
            # Price shouldn't be more than 50% away from MA20 (reasonable for production validation)
            if price_diff_ratio > Decimal('0.5'):
                raise ValueError(f"Recent price ({recent_price}) too far from MA20 ({self.ma_20}), ratio: {price_diff_ratio}")
    
    def to_json_context(self) -> str:
        """Serializes the dataset to a structured JSON string for LLM consumption."""
        
        def format_candles(df: pd.DataFrame) -> list:
            """Helper to format a DataFrame of candles into a list of dicts."""
            # Convert timestamp to UNIX epoch seconds for brevity
            df['unix_timestamp'] = (df['timestamp'] - pd.Timestamp("1970-01-01", tz='UTC')) // pd.Timedelta('1s')
            
            # Select and rename columns for brevity
            formatted_df = df[['unix_timestamp', 'open', 'high', 'low', 'close', 'volume']].copy()
            formatted_df.columns = ['t', 'o', 'h', 'l', 'c', 'v']
            
            # Convert to list of dicts
            return formatted_df.to_dict(orient='records')

        context_dict = {
            "symbol": self.symbol,
            "current_price": float(self.h1_candles.iloc[-1]['close']),
            "primary_indicators": {
                "rsi_14": float(self.rsi_14),
                "ma_20": float(self.ma_20) if self.ma_20 is not None else None,
                "ma_50": float(self.ma_50) if self.ma_50 is not None else None,
                "macd_signal": self.macd_signal,
                "ma_trend": self.ma_trend
            },
            "key_levels": {
                "support": float(self.support_level) if self.support_level is not None else None,
                "resistance": float(self.resistance_level) if self.resistance_level is not None else None
            },
            "market_sentiment": {
                "btc_correlation": float(self.btc_correlation) if self.btc_correlation is not None else None,
                "fear_greed_index": self.fear_greed_index,
                "volume_profile": self.volume_profile
            },
            "raw_candles": {
                "daily": format_candles(self.daily_candles),
                "h4": format_candles(self.h4_candles),
                "h1": format_candles(self.h1_candles)
            }
        }
        
        return json.dumps(context_dict, indent=2)

    
    def _analyze_trend(self, df: pd.DataFrame) -> str:
        """Analyze trend direction from price data."""
        if len(df) < 2:
            return "insufficient_data"
        
        start_price = df.iloc[0]['close']
        end_price = df.iloc[-1]['close']
        change_pct = ((end_price - start_price) / start_price) * 100
        
        if change_pct > 5:
            return f"BULLISH (+{change_pct:.1f}%)"
        elif change_pct < -5:
            return f"BEARISH ({change_pct:.1f}%)"
        else:
            return f"SIDEWAYS ({change_pct:.1f}%)"
    
    def _calculate_24h_change(self) -> Decimal:
        """Calculate 24-hour price change percentage."""
        if len(self.h1_candles) < 24:
            return Decimal('0.0')
        
        price_24h_ago = Decimal(str(self.h1_candles.iloc[-24]['close']))
        current_price = Decimal(str(self.h1_candles.iloc[-1]['close']))
        return ((current_price - price_24h_ago) / price_24h_ago) * Decimal('100')


class MarketDataService:
    """Service for aggregating multi-timeframe cryptocurrency market data."""
    
    def __init__(self, api_client: BinanceApiClient, logger: MarketDataLogger):
        """
        Initializes the MarketDataService.

        Args:
            api_client: An instance of BinanceApiClient.
            logger: A configured MarketDataLogger instance.
        """
        self.api_client = api_client
        self.logger = logger
        
        # Initialize metrics attributes to prevent AttributeError
        self._operation_metrics: Dict[str, Dict[str, int]] = {}
        self._degradation_history: List[Dict[str, Any]] = []
        self._current_trace_id: Optional[str] = None
        
    def _should_log(self, level: str) -> bool:
        """Check if message should be logged based on current log level."""
        log_levels = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
        current_level = log_levels.get(self._log_level, 20)  # Default to INFO
        message_level = log_levels.get(level.upper(), 20)
        return message_level >= current_level
    
    
    def _get_error_context(self, operation: str, trace_id: str) -> ErrorContext:
        """Creates an ErrorContext for a given operation and trace_id."""
        return ErrorContext(trace_id=trace_id, operation=operation)

    def _log_operation_start(self, operation: str, symbol: str = "", level: str = "INFO", trace_id: Optional[str] = None, **kwargs):
        """Direct logging: Log operation start with context and hierarchical tracing."""
        if self.logger:
            try:
                self.logger.log_operation_start(
                    operation=operation,
                    symbol=symbol,
                    context=kwargs,
                    trace_id=trace_id
                )
            except Exception:
                # Graceful degradation: logging failures should not crash operations
                pass
    
    def _log_operation_success(self, operation: str, symbol: str = "", level: str = "INFO", trace_id: Optional[str] = None, **kwargs):
        """Direct logging: Log successful operation completion with hierarchical tracing."""
        if self.logger:
            try:
                self.logger.log_operation_complete(
                    operation=operation,
                    processing_time_ms=kwargs.get('processing_time_ms', 0),
                    context={
                        'symbol': symbol,
                        'status': 'success',
                        **kwargs
                    },
                    trace_id=trace_id
                )
            except Exception:
                # Graceful degradation: logging failures should not crash operations
                pass
    
    def _log_operation_error(self, operation: str, error: Exception, symbol: str = "", level: str = "ERROR", trace_id: Optional[str] = None, **kwargs):
        """Direct logging: Log operation error with rich context."""
        if self.logger:
            try:
                self.logger.log_validation_error(
                    field=operation,
                    value=str(error),
                    expected="successful_operation",
                    error_msg=f"{kwargs.get('error_type', type(error).__name__)}: {str(error)}",
                    trace_id=trace_id
                )
            except Exception:
                # Graceful degradation: logging failures should not crash operations
                pass
        
    
    def get_market_data(self, symbol: str, trace_id: Optional[str] = None) -> MarketDataSet:
        """
        Get complete multi-timeframe market data for a symbol with structured error handling.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            trace_id: The master trace_id for the entire operation.
            
        Returns:
            MarketDataSet with all timeframes and indicators
        """
        self._log_operation_start("get_market_data", symbol=symbol, trace_id=trace_id)
        
        try:
            # Validate input parameters - may raise SymbolValidationError
            self._validate_symbol_input(symbol, trace_id=trace_id)
            
            if not trace_id:
                raise ValidationError("A trace_id is required for all market data operations.")
            
            # Fetch multi-timeframe data using the API client
            daily_data_raw = self.api_client.get_klines(symbol, "1d", 180, trace_id=trace_id)
            h4_data_raw = self.api_client.get_klines(symbol, "4h", 84, trace_id=trace_id)
            h1_data_raw = self.api_client.get_klines(symbol, "1h", 100, trace_id=trace_id)

            # Convert raw list data to DataFrame
            daily_data = self._create_dataframe_from_klines(daily_data_raw)
            h4_data = self._create_dataframe_from_klines(h4_data_raw)
            h1_data = self._create_dataframe_from_klines(h1_data_raw)
            
            # Defensive check for empty DataFrames before calculations
            if daily_data.empty or h4_data.empty or h1_data.empty:
                raise DataInsufficientError(
                    message="One or more required DataFrames are empty, cannot proceed with calculations.",
                    operation="get_market_data",
                    context=self._get_error_context("get_market_data", trace_id),
                    required_periods=1,  # We need at least one row
                    available_periods=min(len(daily_data), len(h4_data), len(h1_data)),
                    data_type="multi_timeframe_candles"
                )

            # Calculate support/resistance levels (no state pollution)
            # Ensure there is data to calculate min/max from to avoid NaN -> Decimal error
            min_low = daily_data['low'].tail(30).min()
            max_high = daily_data['high'].tail(30).max()

            if pd.isna(min_low) or pd.isna(max_high):
                raise CalculationError(
                    message="Cannot calculate support/resistance due to insufficient valid data in daily candles.",
                    operation="get_market_data",
                    context=self._get_error_context("get_market_data", trace_id),
                    calculation_type="support_resistance",
                    error_details="min() or max() on daily data returned NaN."
                )

            support_level = Decimal(str(min_low))
            resistance_level = Decimal(str(max_high))
            
            # Handle edge case where support equals resistance (zero volatility)
            if support_level >= resistance_level:
                price_buffer = resistance_level * Decimal('0.001')
                support_level = resistance_level - price_buffer
            
            # Calculate technical indicators with graceful degradation
            rsi = self._calculate_rsi(symbol, h1_data, 14, trace_id=trace_id)
            macd_signal = self._calculate_macd_signal(symbol, h1_data, trace_id=trace_id)
            ma_20 = self._calculate_ma(symbol, h1_data, 20, trace_id=trace_id)
            ma_50 = self._calculate_ma(symbol, h1_data, 50, trace_id=trace_id)
            ma_trend = self._determine_ma_trend(ma_20, ma_50, trace_id=trace_id)
            
            # Get market context
            btc_correlation = self._calculate_btc_correlation(symbol, h1_data, trace_id=trace_id) if symbol != "BTCUSDT" else None
            volume_profile = self._analyze_volume_profile(symbol, h1_data, trace_id=trace_id)
            
            market_data_set = MarketDataSet(
                symbol=symbol,
                timestamp=datetime.now(timezone.utc),
                daily_candles=daily_data,
                h4_candles=h4_data,
                h1_candles=h1_data,
                rsi_14=rsi,
                macd_signal=macd_signal,
                ma_20=ma_20,
                ma_50=ma_50,
                ma_trend=ma_trend,
                btc_correlation=btc_correlation,
                volume_profile=volume_profile,
                support_level=support_level,
                resistance_level=resistance_level,
                trace_id=trace_id
            )
            market_data_set.trace_id = trace_id
            
            self._log_operation_success("get_market_data", symbol=symbol, level="INFO", data_points=len(h1_data), trace_id=trace_id)
            
            if self.logger:
                self._log_market_analysis_complete(symbol, market_data_set, trace_id=trace_id)
            
            return market_data_set
            
        except ApiClientError as e:
            # Ensure the trace_id from the operation is attached to the exception
            if trace_id and (not hasattr(e.context, 'trace_id') or not e.context.trace_id.startswith('trd_')):
                 e.context.trace_id = trace_id
                 # Also update the trace_id in the string representation if it's an error-specific one
                 if "err_" in str(e):
                     e.message = str(e).split(' [')[0] # Keep original message

            self._log_operation_error(
                "get_market_data", e, symbol=symbol, trace_id=trace_id, error_type="ApiClientError"
            )
            raise
        except (ValidationError, ProcessingError) as e:
            self._log_operation_error(
                "get_market_data", e, symbol=symbol, trace_id=trace_id, error_type=type(e).__name__
            )
            raise
        except Exception as e:
            self._log_operation_error(
                "get_market_data", e, symbol=symbol, trace_id=trace_id, error_type="UnexpectedError", level="CRITICAL"
            )
            raise ProcessingError(
                message=f"Unexpected error during market data aggregation: {str(e)}",
                operation="get_market_data",
                context=self._get_error_context("get_market_data", trace_id),
                processing_stage="data_aggregation",
                error_details=str(e)
            )
    
    def _create_dataframe_from_klines(self, klines_data: list) -> pd.DataFrame:
        """Converts raw kline list data to a pandas DataFrame."""
        if not klines_data:
            return pd.DataFrame()
            
        df = pd.DataFrame(klines_data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col])
            
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC')
        
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

    def _validate_symbol_input(self, symbol: str, trace_id: Optional[str] = None):
        """Validate symbol input before processing."""
        try:
            error_context = self._get_error_context("symbol_validation", trace_id)
            if not symbol or not isinstance(symbol, str):
                raise SymbolValidationError("Symbol must be a non-empty string", symbol=str(symbol), context=error_context)
            if not symbol.endswith("USDT") or len(symbol) < 6:
                raise SymbolValidationError(f"Invalid symbol format: {symbol}. Expected XXXUSDT format", symbol=symbol, context=error_context)
            if len(symbol) > 12:  # Reasonable length limit
                raise SymbolValidationError(f"Symbol too long: {symbol}", symbol=symbol, context=error_context)
            
            # Extract base currency by removing only the trailing USDT
            if symbol.count("USDT") > 1:
                raise SymbolValidationError(f"Invalid symbol format: {symbol}. Multiple USDT occurrences not allowed", symbol=symbol, context=error_context)
            
            base_currency = symbol[:-4]  # Remove last 4 characters (USDT)
            if not base_currency or not base_currency.isalpha() or not base_currency.isupper():
                raise SymbolValidationError(f"Invalid base currency: '{base_currency}'. Must be uppercase letters only", symbol=symbol, context=error_context)
            
            # Validate base currency length (cryptocurrency standards)
            if len(base_currency) < 3:
                raise SymbolValidationError(f"Base currency too short: '{base_currency}'. Must be at least 3 characters", symbol=symbol, context=error_context)
            if len(base_currency) > 5:
                raise SymbolValidationError(f"Base currency too long: '{base_currency}'. Must be 5 characters or less", symbol=symbol, context=error_context)
        except SymbolValidationError:
            # Re-raise SymbolValidationError as-is to maintain rich context
            raise
        except Exception as e:
            # Wrap unexpected errors in SymbolValidationError for consistency
            raise SymbolValidationError(f"Unexpected error during symbol validation: {str(e)}", symbol=str(symbol), context=error_context)
    
    def get_enhanced_context(self, market_data: MarketDataSet) -> str:
        """Get enhanced market context with a strict 'Fail-Fast' error handling policy."""
        symbol = market_data.symbol
        trace_id = market_data.trace_id
        self._log_operation_start(
            "get_enhanced_context",
            symbol=symbol,
            trace_id=trace_id
        )

        try:
            # --- All analysis is now within a single try block ---
            key_candles = self._select_key_candles(
                market_data.daily_candles.values.tolist(),
                market_data.support_level,
                market_data.resistance_level
            )

            analysis = f"--- Enhanced Analysis for {symbol} ---\n"
            analysis += f"Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            analysis += "=== CANDLESTICK ANALYSIS ===\n"

            recent_trend = self._analyze_recent_trend(key_candles[:5])
            analysis += f"Recent Trend: {recent_trend}\n"

            patterns = self._identify_patterns(key_candles)
            analysis += f"Patterns: {', '.join(patterns) if patterns else 'No significant patterns detected'}\n"

            if market_data.support_level is not None and market_data.resistance_level is not None:
                sr_tests = self._analyze_sr_tests(key_candles, market_data.support_level, market_data.resistance_level)
                analysis += f"S/R Tests: {sr_tests or 'No recent support/resistance tests'}\n"
            else:
                analysis += "S/R Tests: Support/resistance levels unavailable\n"

            volume_analysis = self._analyze_volume_relationship(key_candles)
            analysis += f"Volume Analysis: {volume_analysis}\n"

            total_candles = len(market_data.daily_candles)
            analysis += f"Key Candles Analyzed: {len(key_candles)} of {total_candles} total"

            self._log_operation_success("get_enhanced_context", symbol=symbol, trace_id=trace_id)
            return analysis

        except Exception as e:
            # If any part of the analysis fails, wrap it in ProcessingError and re-raise.
            self._log_operation_error(
                "get_enhanced_context", e, symbol=symbol, trace_id=trace_id, error_type="EnhancedAnalysisFailed"
            )
            raise ProcessingError(
                message=f"Enhanced context analysis failed: {str(e)}",
                operation="get_enhanced_context",
                context=self._get_error_context("get_enhanced_context", trace_id),
                processing_stage="candlestick_analysis",
                error_details=str(e)
            )
    
    
    def _calculate_rsi(self, symbol: str, df: pd.DataFrame, period: int = 14, trace_id: Optional[str] = None) -> Decimal:
        """Calculate RSI indicator with Decimal precision and division by zero protection."""
        self._log_operation_start(
            "rsi_calculation",
            symbol=symbol,
            period=period,
            data_points=len(df),
            trace_id=trace_id
        )
        
        if len(df) < period + 1:
            if self.logger:
                self.logger.log_raw_data(
                    data_type="rsi_calculation",
                    data_sample={
                        "result": "insufficient_data",
                        "required_periods": period + 1,
                        "available_periods": len(df),
                        "fallback_value": 50.0
                    },
                    data_stats={"status": "fallback"},
                    trace_id=trace_id
                )
            return Decimal('50.0')  # Default neutral RSI
        
        closes = df['close']
        delta = closes.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Get the final values
        final_gain = gain.iloc[-1]
        final_loss = loss.iloc[-1]
        
        # Handle division by zero cases
        if final_loss == 0:
            if final_gain == 0:
                # No price movement at all
                rsi_value = 50.0
            else:
                # Only gains, no losses (maximum RSI)
                rsi_value = 100.0
        elif final_gain == 0:
            # Only losses, no gains (minimum RSI)
            rsi_value = 0.0
        else:
            # Normal RSI calculation
            rs = final_gain / final_loss
            rsi_value = 100 - (100 / (1 + rs))
        
        # Convert to Decimal with proper precision
        result = Decimal(str(rsi_value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Log RSI calculation completion
        if self.logger:
            self.logger.log_operation_complete(
                operation="rsi_calculation",
                processing_time_ms=0,  # Fast calculation
                context={
                    "rsi_value": float(result),
                    "final_gain": float(final_gain),
                    "final_loss": float(final_loss),
                    "period": period,
                    "data_quality": "normal" if len(df) >= period + 10 else "minimal"
                },
                trace_id=trace_id
            )
        
        return result
    
    def _calculate_macd_signal(self, symbol: str, df: pd.DataFrame, trace_id: Optional[str] = None) -> str:
        """Calculate MACD signal (bullish/bearish/neutral)."""
        self._log_operation_start(
            "macd_calculation",
            symbol=symbol,
            data_points=len(df),
            trace_id=trace_id
        )
        
        if len(df) < 26:
            if self.logger:
                self.logger.log_raw_data(
                    data_type="macd_calculation",
                    data_sample={
                        "result": "insufficient_data",
                        "required_periods": 26,
                        "available_periods": len(df),
                        "fallback_signal": "neutral"
                    },
                    data_stats={"status": "fallback"},
                    trace_id=trace_id
                )
            return "neutral"
        
        closes = df['close']
        ema_12 = closes.ewm(span=12).mean()
        ema_26 = closes.ewm(span=26).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9).mean()
        
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        
        if current_macd > current_signal:
            result = "bullish"
        elif current_macd < current_signal:
            result = "bearish"
        else:
            result = "neutral"
        
        # Log MACD calculation completion
        if self.logger:
            self.logger.log_operation_complete(
                operation="macd_calculation",
                processing_time_ms=0,  # Fast calculation
                context={
                    "macd_signal": result,
                    "current_macd": float(current_macd),
                    "current_signal": float(current_signal),
                    "ema_12": float(ema_12.iloc[-1]),
                    "ema_26": float(ema_26.iloc[-1]),
                    "data_quality": "normal" if len(df) >= 35 else "minimal"
                },
                trace_id=trace_id
            )
        
        return result
    
    def _calculate_ma(self, symbol: str, df: pd.DataFrame, period: int, trace_id: Optional[str] = None) -> Decimal:
        """Calculate moving average with Decimal precision."""
        self._log_operation_start(
            "ma_calculation",
            symbol=symbol,
            period=period,
            data_points=len(df),
            trace_id=trace_id
        )
        
        if len(df) < period:
            avg_value = df['close'].mean()
            if pd.isna(avg_value):
                result = Decimal('0.0')
            else:
                result = Decimal(str(avg_value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            if self.logger:
                self.logger.log_raw_data(
                    data_type="ma_calculation",
                    data_sample={
                        "result": "insufficient_data_fallback",
                        "required_periods": period,
                        "available_periods": len(df),
                        "fallback_method": "simple_average",
                        "ma_value": float(result)
                    },
                    data_stats={"status": "fallback"},
                    trace_id=trace_id
                )
                
                # Добавляем логирование завершения операции для fallback случая
                self.logger.log_operation_complete(
                    operation="ma_calculation",
                    processing_time_ms=0,  # Быстрый fallback расчет
                    context={
                        "period": period,
                        "ma_value": float(result),
                        "data_points_used": len(df),
                        "data_quality": "fallback",
                        "calculation_method": "simple_average_fallback"
                    },
                    trace_id=trace_id
                )
            return result
        
        ma_value = df['close'].rolling(window=period).mean().iloc[-1]
        if pd.notna(ma_value):
            result = Decimal(str(float(ma_value))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            avg_value = df['close'].mean()
            if pd.isna(avg_value):
                result = Decimal('0.0')
            else:
                result = Decimal(str(avg_value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Log MA calculation completion
        if self.logger:
            self.logger.log_operation_complete(
                operation="ma_calculation",
                processing_time_ms=0,  # Fast calculation
                context={
                    "period": period,
                    "ma_value": float(result),
                    "data_points_used": period,
                    "data_quality": "normal" if len(df) >= period + 5 else "minimal",
                    "calculation_method": "rolling_average" if pd.notna(ma_value) else "simple_average"
                },
                trace_id=trace_id
            )
        
        return result
    
    def _determine_ma_trend(self, ma_20: Decimal, ma_50: Decimal, trace_id: Optional[str] = None) -> str:
        """Determine trend based on moving averages."""
        if ma_20 is None or ma_50 is None:
            return "sideways"
        
        threshold_up = ma_50 * Decimal('1.02')  # 2% threshold
        threshold_down = ma_50 * Decimal('0.98')
        
        if ma_20 > threshold_up:
            return "uptrend"
        elif ma_20 < threshold_down:
            return "downtrend"
        else:
            return "sideways"
    
    def _calculate_btc_correlation(self, symbol: str, df: pd.DataFrame, trace_id: Optional[str] = None) -> Optional[Decimal]:
        """Calculate correlation with BTC using actual price data with structured error handling."""
        # Skip correlation calculation for BTC itself
        if symbol == "BTCUSDT":
            return None

        self._log_operation_start(
            "btc_correlation",
            symbol=symbol,
            data_points=len(df),
            trace_id=trace_id
        )
        error_context = self._get_error_context("btc_correlation", trace_id)

        try:
            # Fetch BTC data for correlation calculation, passing the trace_id
            btc_data_raw = self.api_client.get_klines("BTCUSDT", "1h", len(df), trace_id=trace_id)
            btc_data = self._create_dataframe_from_klines(btc_data_raw)

            # Ensure we have enough data points for meaningful correlation
            if len(btc_data) < 10 or len(df) < 10:
                if self.logger:
                    self.logger.log_raw_data(
                        data_type="btc_correlation_calculation",
                        data_sample={
                            "result": "insufficient_data",
                            "btc_data_points": len(btc_data),
                            "symbol_data_points": len(df),
                            "required_minimum": 10,
                            "correlation_value": None
                        },
                        data_stats={"status": "insufficient_data"},
                        trace_id=trace_id
                    )
                raise DataInsufficientError(
                    message=f"Insufficient data for BTC correlation: BTC={len(btc_data)}, {symbol}={len(df)} (need 10+ each)",
                    required_periods=10,
                    available_periods=min(len(btc_data), len(df)),
                    data_type="btc_correlation",
                    operation="btc_correlation",
                    context=error_context
                )

            # Align data by taking minimum length
            min_length = min(len(df), len(btc_data))
            symbol_prices = df['close'].tail(min_length).values
            btc_prices = btc_data['close'].tail(min_length).values

            # Calculate Pearson correlation coefficient
            correlation = pd.Series(symbol_prices).corr(pd.Series(btc_prices))

            # Handle NaN correlation (can happen with constant prices)
            if pd.isna(correlation):
                if self.logger:
                    self.logger.log_raw_data(
                        data_type="btc_correlation_calculation",
                        data_sample={
                            "result": "nan_correlation",
                            "reason": "constant_prices_or_no_variance",
                            "fallback_correlation": 0.0,
                            "data_points_used": min_length
                        },
                        data_stats={"status": "fallback"},
                        trace_id=trace_id
                    )
                # This is not necessarily an error - constant prices can produce NaN correlation
                return Decimal('0.0')

            # Convert to Decimal and clamp to valid range [-1, 1]
            correlation_decimal = Decimal(str(float(correlation))).quantize(Decimal('0.001'))

            # Ensure correlation is within valid bounds
            if correlation_decimal > Decimal('1.0'):
                correlation_decimal = Decimal('1.0')
            elif correlation_decimal < Decimal('-1.0'):
                correlation_decimal = Decimal('-1.0')

            # Log BTC correlation calculation completion
            self._log_operation_success(
                "btc_correlation",
                symbol=symbol,
                correlation_value=float(correlation_decimal),
                data_points_used=min_length,
                trace_id=trace_id
            )

            return correlation_decimal

        except (NetworkError, DataInsufficientError, ProcessingError):
            # Re-raise our custom exceptions to preserve error context chain
            raise
        except Exception as e:
            # Wrap unexpected errors in ProcessingError with preserved context
            raise ProcessingError(
                message=f"Unexpected error during BTC correlation calculation: {str(e)}",
                operation="btc_correlation",
                context=error_context,
                processing_stage="correlation_calculation",
                error_details=str(e)
            )
    

    
    def _get_market_data_with_fallback(self, symbol: str) -> dict:
        """
        Get market data with graceful degradation fallback strategy.
        
        Returns a dictionary with basic data and enhanced features that succeeded,
        setting failed components to None for graceful degradation.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Dict with basic_data and enhanced features (correlation, volume_profile, etc.)
        """
        try:
            # Use existing trace_id (inherited from master operation) and pass master as parent
            master_trace_id = self._current_trace_id
            error_context = self._get_error_context("get_market_data_with_fallback", trace_id=master_trace_id)
            
            # Try to get basic market data with manual graceful degradation
            try:
                # Get core data first (timeframes - critical)
                daily_data = self._get_klines(symbol, "1d", 180)  # 6 months
                h4_data = self._get_klines(symbol, "4h", 84)      # 2 weeks
                h1_data = self._get_klines(symbol, "1h", 100)     # 100 hours
                
                # Calculate support/resistance levels (no state pollution)
                support_level = Decimal(str(daily_data['low'].tail(30).min()))
                resistance_level = Decimal(str(daily_data['high'].tail(30).max()))
                
                # Calculate technical indicators with graceful degradation
                rsi = self._calculate_rsi_with_fallback(h1_data, 14)
                macd_signal = self._calculate_macd_signal_with_fallback(h1_data)
                ma_20 = self._calculate_ma_with_fallback(h1_data, 20)
                ma_50 = self._calculate_ma_with_fallback(h1_data, 50)
                ma_trend = self._determine_ma_trend_with_fallback(ma_20, ma_50)
                
                # Create basic market data with graceful defaults for enhanced features
                market_data = MarketDataSet(
                    symbol=symbol,
                    timestamp=datetime.now(timezone.utc),
                    daily_candles=daily_data,
                    h4_candles=h4_data,
                    h1_candles=h1_data,
                    rsi_14=rsi,
                    macd_signal=macd_signal,
                    ma_20=ma_20,
                    ma_50=ma_50,
                    ma_trend=ma_trend,
                    btc_correlation=None,  # Will be calculated below with graceful degradation
                    volume_profile="normal",  # Will be calculated below with graceful degradation
                    support_level=support_level,
                    resistance_level=resistance_level
                )
                
                result = {
                    "basic_data": market_data,
                    "symbol": symbol,
                    "timestamp": market_data.timestamp
                }
            except Exception as e:
                # If basic data fails, this is a critical failure
                self._log_operation_error("get_market_data_with_fallback", e,
                                        symbol=symbol, error_type="critical_basic_data_failure")
                raise
            
            # Try enhanced features with graceful degradation
            enhanced_features = {}
            
            # BTC Correlation (graceful degradation)
            try:
                if symbol != "BTCUSDT":
                    correlation = self._calculate_btc_correlation(symbol, market_data.h1_candles)
                    enhanced_features["correlation"] = correlation
                else:
                    enhanced_features["correlation"] = None
            except Exception as e:
                enhanced_features["correlation"] = None
                self._log_graceful_degradation(
                    "get_market_data_with_fallback",
                    failed_component="btc_correlation",
                    fallback_used="no_correlation_data",
                    trace_id=self._current_trace_id
                )
            
            # Volume Profile (graceful degradation)
            try:
                volume_profile = self._analyze_volume_profile(market_data.h1_candles)
                enhanced_features["volume_profile"] = volume_profile
            except Exception as e:
                enhanced_features["volume_profile"] = None
                self._log_graceful_degradation(
                    "get_market_data_with_fallback",
                    failed_component="volume_profile",
                    fallback_used="no_volume_analysis",
                    trace_id=self._current_trace_id
                )
            
            # Technical Indicators (graceful degradation)
            try:
                technical_indicators = self._calculate_technical_indicators(market_data.h1_candles)
                enhanced_features["technical_indicators"] = technical_indicators
            except Exception as e:
                enhanced_features["technical_indicators"] = None
                self._log_graceful_degradation(
                    "get_market_data_with_fallback",
                    failed_component="technical_indicators",
                    fallback_used="basic_indicators_only",
                    trace_id=self._current_trace_id
                )
            
            # Merge enhanced features into result
            result.update(enhanced_features)
            
            # Log successful operation completion
            self._log_operation_success("get_market_data_with_fallback", symbol=symbol,
                                      enhanced_features_count=len([f for f in enhanced_features.values() if f is not None]))
            
            return result
            
        except Exception as e:
            # Log the error
            self._log_operation_error("get_market_data_with_fallback", e, symbol=symbol, error_type=type(e).__name__)
            # Re-raise for caller to handle
            raise
    
    def _log_graceful_degradation(self, operation: str, failed_component: str = None,
                                fallback_used: str = None, trace_id: str = None, **kwargs):
        """
        Log graceful degradation events for non-critical operation failures.
        
        Args:
            operation: Name of the operation experiencing degradation
            failed_component: Component that failed (e.g., 'btc_correlation', 'volume_profile')
            fallback_used: Description of fallback strategy used
            trace_id: Optional trace ID for correlation
            **kwargs: Additional context for logging
        """
        if self.logger:
            # Future logging implementation will go here
            # For now, this is a placeholder that maintains current functionality
            pass
        
        # Store degradation metrics for future logging integration
        if operation not in self._operation_metrics:
            self._operation_metrics[operation] = {"count": 0, "errors": 0, "degradations": 0}
        
        # Track degradation event
        if "degradations" not in self._operation_metrics[operation]:
            self._operation_metrics[operation]["degradations"] = 0
        self._operation_metrics[operation]["degradations"] += 1
        
        # Store degradation context for debugging
        if not hasattr(self, '_degradation_history'):
            self._degradation_history = []
        
        self._degradation_history.append({
            "operation": operation,
            "failed_component": failed_component,
            "fallback_used": fallback_used,
            "trace_id": trace_id or self._current_trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs
        })
        
        # Keep only last 100 degradation events to prevent memory growth
        if len(self._degradation_history) > 100:
            self._degradation_history = self._degradation_history[-100:]
    
    def _log_market_analysis_complete(self, symbol: str, market_data: MarketDataSet, trace_id: str = None):
        """Log complete market analysis for AI trading strategy optimization."""
        if not self.logger:
            return
            
        try:
            # Prepare comprehensive analysis data for AI
            analysis_data = {
                "technical_indicators": {
                    "rsi_14": float(market_data.rsi_14),
                    "macd_signal": market_data.macd_signal,
                    "ma_20": float(market_data.ma_20) if market_data.ma_20 else None,
                    "ma_50": float(market_data.ma_50) if market_data.ma_50 else None,
                    "ma_trend": market_data.ma_trend
                },
                "market_context": {
                    "btc_correlation": float(market_data.btc_correlation) if market_data.btc_correlation else None,
                    "volume_profile": market_data.volume_profile,
                    "support_level": float(market_data.support_level) if market_data.support_level else None,
                    "resistance_level": float(market_data.resistance_level) if market_data.resistance_level else None
                },
                "data_quality": {
                    "daily_candles_count": len(market_data.daily_candles),
                    "h4_candles_count": len(market_data.h4_candles),
                    "h1_candles_count": len(market_data.h1_candles),
                    "timestamp": market_data.timestamp.isoformat()
                }
            }
            
            # Calculate basic trading decision confidence
            confidence = self._calculate_analysis_confidence(market_data)
            decision = self._get_basic_trading_decision(market_data)
            
            # Direct logging: market analysis with trading context
            self.logger.log_raw_data(
                data_type="market_analysis",
                data_sample={
                    "symbol": symbol,
                    "analysis_data": analysis_data,
                    "decision": decision,
                    "confidence": confidence,
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat()
                },
                data_stats={
                    "symbol": symbol,
                    "decision": decision,
                    "confidence_level": "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
                },
                trace_id=trace_id
            )
            
        except Exception as e:
            # Don't let logging errors affect main functionality
            self._log_operation_error("market_analysis_logging", e, symbol=symbol)
    
    def _calculate_analysis_confidence(self, market_data: MarketDataSet) -> float:
        """Calculate confidence level of market analysis based on data quality and indicators."""
        confidence_factors = []
        
        # Data quality factor (30% weight)
        data_quality = min(len(market_data.h1_candles) / 100.0, 1.0) # Full confidence at 100+ candles
        confidence_factors.append(data_quality * 0.3)
        
        # Technical indicators confidence (40% weight)
        rsi_confidence = 1.0 if 20 <= market_data.rsi_14 <= 80 else 0.5  # RSI in normal range
        macd_confidence = 1.0 if market_data.macd_signal != "neutral" else 0.5
        ma_confidence = 1.0 if market_data.ma_trend != "sideways" else 0.5
        
        tech_avg = (rsi_confidence + macd_confidence + ma_confidence) / 3
        confidence_factors.append(tech_avg * 0.4)
        
        # Market context factor (30% weight)
        context_confidence = 0.8  # Base confidence
        if market_data.btc_correlation is not None:
            context_confidence += 0.1  # Bonus for BTC correlation data
        if market_data.volume_profile in ["high", "low"]:  # Clear volume signal
            context_confidence += 0.1
        
        confidence_factors.append(min(context_confidence, 1.0) * 0.3)
        
        return min(sum(confidence_factors), 1.0)
    
    def _get_basic_trading_decision(self, market_data: MarketDataSet) -> str:
        """Get basic trading decision based on technical indicators."""
        bullish_signals = 0
        bearish_signals = 0
        
        # RSI signals
        if market_data.rsi_14 < Decimal('30'):
            bullish_signals += 1  # Oversold
        elif market_data.rsi_14 > Decimal('70'):
            bearish_signals += 1  # Overbought
        
        # MACD signals
        if market_data.macd_signal == "bullish":
            bullish_signals += 1
        elif market_data.macd_signal == "bearish":
            bearish_signals += 1
        
        # MA trend signals
        if market_data.ma_trend == "uptrend":
            bullish_signals += 1
        elif market_data.ma_trend == "downtrend":
            bearish_signals += 1
        
        # Decision logic
        if bullish_signals > bearish_signals:
            return "buy"
        elif bearish_signals > bullish_signals:
            return "sell"
        else:
            return "hold"
    
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> dict:
        """
        Calculate comprehensive technical indicators for enhanced analysis.
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            Dict with technical indicators (RSI, MACD, Bollinger Bands, etc.)
        """
        if len(df) < 20:
            raise CalculationError(
                "Insufficient data for technical indicators calculation",
                calculation_type="technical_indicators",
                operation="technical_analysis",
                required_periods=20,
                available_periods=len(df)
            )
        
        try:
            indicators = {}
            
            # RSI calculation
            indicators['rsi_14'] = self._calculate_rsi(df, 14)
            indicators['rsi_7'] = self._calculate_rsi(df, 7) if len(df) >= 8 else None
            
            # MACD calculation
            indicators['macd_signal'] = self._calculate_macd_signal(df)
            
            # Moving averages
            indicators['ma_10'] = self._calculate_ma(df, 10) if len(df) >= 10 else None
            indicators['ma_20'] = self._calculate_ma(df, 20)
            indicators['ma_50'] = self._calculate_ma(df, 50) if len(df) >= 50 else None
            
            # Bollinger Bands (if enough data)
            if len(df) >= 20:
                bb_data = self._calculate_bollinger_bands(df, 20)
                indicators.update(bb_data)
            
            # Volume indicators
            if 'volume' in df.columns:
                indicators['volume_sma_10'] = df['volume'].rolling(10).mean().iloc[-1] if len(df) >= 10 else None
                indicators['volume_ratio'] = (df['volume'].iloc[-1] / df['volume'].rolling(10).mean().iloc[-1]) if len(df) >= 10 else None
            
            return indicators
            
        except Exception as e:
            raise CalculationError(
                f"Technical indicators calculation failed: {str(e)}",
                calculation_type="comprehensive_technical_indicators",
                operation="technical_analysis",
                error_details=str(e)
            )
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20) -> dict:
        """Calculate Bollinger Bands with Decimal precision."""
        if len(df) < period:
            return {"bb_upper": None, "bb_middle": None, "bb_lower": None}
        
        closes = df['close']
        sma = closes.rolling(period).mean()
        std = closes.rolling(period).std()
        
        bb_upper = sma + (std * 2)
        bb_middle = sma
        bb_lower = sma - (std * 2)
        
        return {
            "bb_upper": Decimal(str(bb_upper.iloc[-1])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            "bb_middle": Decimal(str(bb_middle.iloc[-1])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            "bb_lower": Decimal(str(bb_lower.iloc[-1])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        }
    
    def _execute_with_strategy(self, operation_type: str, operation_func, fallback_value=None):
        """Execute operation with fail-fast vs recovery strategy."""
        try:
            return operation_func()
        except Exception as e:
            # Determine strategy based on operation type and configuration
            if self._fail_fast or operation_type in self._critical_failures:
                # Fail-fast: Re-raise the exception immediately
                self._log_operation_error(f"{operation_type}_fail_fast", e,
                                        strategy="fail_fast", operation_type=operation_type)
                raise
            elif operation_type in self._recoverable_operations:
                # Recovery: Log error and return fallback value
                self._log_operation_error(f"{operation_type}_recovery", e,
                                        strategy="recovery", operation_type=operation_type,
                                        fallback_value=fallback_value)
                return fallback_value
            else:
                # Default: fail-fast for unknown operations
                self._log_operation_error(f"{operation_type}_unknown_fail_fast", e,
                                        strategy="fail_fast_default", operation_type=operation_type)
                raise
    
    def _analyze_volume_profile(self, symbol: str, df: pd.DataFrame, trace_id: Optional[str] = None) -> str:
        """Analyze volume profile (high/normal/low)."""
        self._log_operation_start(
            "volume_analysis",
            symbol=symbol,
            data_points=len(df),
            trace_id=trace_id
        )

        if len(df) < 24:  # Need at least 24 hours for basic comparison
            if self.logger:
                self.logger.log_raw_data(
                    data_type="volume_analysis",
                    data_sample={
                        "result": "insufficient_data",
                        "required_periods": 24,
                        "available_periods": len(df),
                        "fallback_profile": "normal"
                    },
                    data_stats={"status": "fallback"},
                    trace_id=trace_id
                )
            return "normal"

        # Recent volume: last 24 hours
        recent_volume = df['volume'].tail(24).mean()

        # Historical volume: exclude recent 24 hours to avoid overlap
        historical_data = df['volume'].iloc[:-24]  # All data except last 24 hours
        if len(historical_data) == 0:
            if self.logger:
                self.logger.log_raw_data(
                    data_type="volume_analysis",
                    data_sample={
                        "result": "no_historical_data",
                        "recent_volume": float(recent_volume),
                        "fallback_profile": "normal"
                    },
                    data_stats={"status": "fallback"},
                    trace_id=trace_id
                )
            return "normal"

        historical_volume = historical_data.mean()

        # Prevent division by zero
        if historical_volume == 0:
            if self.logger:
                self.logger.log_raw_data(
                    data_type="volume_analysis",
                    data_sample={
                        "result": "zero_historical_volume",
                        "recent_volume": float(recent_volume),
                        "historical_volume": 0.0,
                        "fallback_profile": "normal"
                    },
                    data_stats={"status": "fallback"},
                    trace_id=trace_id
                )
            return "normal"

        ratio = recent_volume / historical_volume

        if ratio > 1.5:
            result = "high"
        elif ratio < 0.5:
            result = "low"
        else:
            result = "normal"

        # Log volume analysis completion
        self._log_operation_success(
            "volume_analysis",
            symbol=symbol,
            volume_profile=result,
            recent_volume=float(recent_volume),
            historical_volume=float(historical_volume),
            volume_ratio=float(ratio),
            trace_id=trace_id
        )

        return result
    
    def _select_key_candles(self, daily_candles: list, support_level: Optional[Decimal] = None, resistance_level: Optional[Decimal] = None) -> list:
        """Select key candlesticks using 7-algorithm approach."""
        if not daily_candles or len(daily_candles) < 10:
            return []
        
        candles = daily_candles.copy()
        key_candles = []
        
        # 1. Recent 5 candles (most important for current context)
        recent_candles = candles[-5:]
        key_candles.extend(recent_candles)
        
        # 2. Extreme candles (highest highs, lowest lows in last 30 days)
        if len(candles) >= 30:
            last_30 = candles[-30:]
            highest_high = max(last_30, key=lambda x: x[2])  # high price
            lowest_low = min(last_30, key=lambda x: x[3])    # low price
            key_candles.extend([highest_high, lowest_low])
        
        # 3. High volume candles (top 10% volume in last 20 days)
        if len(candles) >= 20:
            last_20 = candles[-20:]
            volumes = [float(c[5]) for c in last_20]  # volume
            volume_threshold = sorted(volumes, reverse=True)[int(len(volumes) * 0.1)]
            high_vol_candles = [c for c in last_20 if float(c[5]) >= volume_threshold]
            key_candles.extend(high_vol_candles[:3])  # Top 3 high volume
        
        # 4. Big moves (>3% daily change)
        big_move_candles = []
        for candle in candles[-20:]:  # Last 20 days
            open_price = Decimal(str(candle[1]))
            close_price = Decimal(str(candle[4]))
            change_pct = abs((close_price - open_price) / open_price * Decimal('100'))
            if change_pct > Decimal('3.0'):
                big_move_candles.append(candle)
        key_candles.extend(big_move_candles[-3:])  # Last 3 big moves
        
        # 5. Pattern candles (doji, hammer, shooting star)
        pattern_candles = self._find_pattern_candles(candles[-15:])
        key_candles.extend(pattern_candles)
        
        # 6. Support/Resistance test candles (now active with proper parameters)
        if support_level is not None and resistance_level is not None:
            sr_test_candles = self._find_sr_test_candles(candles[-20:], support_level, resistance_level)
            key_candles.extend(sr_test_candles)
        
        # 7. Remove duplicates and sort by timestamp
        unique_candles = []
        seen_timestamps = set()
        for candle in key_candles:
            timestamp = candle[0]
            if timestamp not in seen_timestamps:
                unique_candles.append(candle)
                seen_timestamps.add(timestamp)
        
        # Sort by timestamp and limit to reasonable number
        unique_candles.sort(key=lambda x: x[0])
        return unique_candles[-15:]  # Keep last 15 key candles
    
    def _find_pattern_candles(self, candles: list) -> list:
        """Identify candlestick patterns with Decimal precision and error handling."""
        pattern_candles = []
        
        try:
            for candle in candles:
                try:
                    open_price = Decimal(str(candle[1]))
                    high_price = Decimal(str(candle[2]))
                    low_price = Decimal(str(candle[3]))
                    close_price = Decimal(str(candle[4]))
                    
                    body = abs(close_price - open_price)
                    upper_shadow = high_price - max(open_price, close_price)
                    lower_shadow = min(open_price, close_price) - low_price
                    total_range = high_price - low_price
                    
                    # Only proceed if we have a valid price range
                    if total_range <= 0:
                        continue
                    
                    # Doji pattern (small body)
                    if body / total_range < Decimal('0.1'):
                        pattern_candles.append(candle)
                    
                    # Hammer/Shooting star (long shadow)
                    elif lower_shadow / total_range > Decimal('0.6'):  # Hammer
                        pattern_candles.append(candle)
                    elif upper_shadow / total_range > Decimal('0.6'):  # Shooting star
                        pattern_candles.append(candle)
                        
                except Exception:
                    # Skip individual candle if processing fails
                    continue
                    
        except Exception:
            # If entire pattern analysis fails, return empty list
            pass
        
        return pattern_candles
    
    def _find_sr_test_candles(self, candles: list, support_level: Decimal, resistance_level: Decimal) -> list:
        """Find candles that test support/resistance levels with Decimal precision."""
        sr_test_candles = []
        
        for candle in candles:
            high_price = Decimal(str(candle[2]))
            low_price = Decimal(str(candle[3]))
            
            # Test resistance level (within 1%)
            if abs(high_price - resistance_level) / resistance_level < Decimal('0.01'):
                sr_test_candles.append(candle)
            
            # Test support level (within 1%)
            elif abs(low_price - support_level) / support_level < Decimal('0.01'):
                sr_test_candles.append(candle)
        
        return sr_test_candles
    
    def _identify_patterns(self, candles: list) -> list:
        """Identify candlestick patterns in key candles with Decimal precision and error handling."""
        patterns = []
        
        try:
            for candle in candles:
                try:
                    open_price = Decimal(str(candle[1]))
                    high_price = Decimal(str(candle[2]))
                    low_price = Decimal(str(candle[3]))
                    close_price = Decimal(str(candle[4]))
                    
                    body = abs(close_price - open_price)
                    upper_shadow = high_price - max(open_price, close_price)
                    lower_shadow = min(open_price, close_price) - low_price
                    total_range = high_price - low_price
                    
                    # Skip candles with no price range
                    if total_range <= 0:
                        continue
                        
                    # Pattern identification with Decimal thresholds (specific patterns first)
                    if lower_shadow / total_range > Decimal('0.6') and body / total_range < Decimal('0.3'):
                        patterns.append("Hammer")
                    elif upper_shadow / total_range > Decimal('0.6') and body / total_range < Decimal('0.3'):
                        patterns.append("Shooting Star")
                    elif body / total_range > Decimal('0.7'):
                        if close_price > open_price:
                            patterns.append("Strong Bull")
                        else:
                            patterns.append("Strong Bear")
                    elif body / total_range < Decimal('0.1'):
                        patterns.append("Doji")
                        
                except Exception:
                    # Skip individual candle if processing fails
                    continue
                    
        except Exception:
            # If entire pattern identification fails, return empty list
            pass
        
        return list(set(patterns))  # Remove duplicates
    
    def _analyze_recent_trend(self, recent_candles: list) -> str:
        """Analyze trend from recent candles with Decimal precision and error handling."""
        try:
            if len(recent_candles) < 3:
                return "Insufficient data"
            
            # Use Decimal for financial precision instead of float
            closes = []
            for c in recent_candles:
                try:
                    closes.append(Decimal(str(c[4])))
                except Exception:
                    continue  # Skip invalid candles
            
            if len(closes) < 3:
                return "Insufficient valid data"
            
            if closes[-1] > closes[-2] > closes[-3]:
                return "Strong Uptrend"
            elif closes[-1] < closes[-2] < closes[-3]:
                return "Strong Downtrend"
            elif closes[-1] > closes[-3]:
                return "Upward bias"
            elif closes[-1] < closes[-3]:
                return "Downward bias"
            else:
                return "Sideways"
                
        except Exception:
            return "Trend analysis failed"
    
    def _analyze_sr_tests(self, candles: list, support_level: Decimal, resistance_level: Decimal) -> str:
        """Analyze support/resistance tests with Decimal precision and error handling."""
        try:
            # Validate inputs
            if not candles or support_level is None or resistance_level is None:
                return "Invalid data for S/R analysis"
            
            if support_level <= 0 or resistance_level <= 0:
                return "Invalid S/R levels"
            
            resistance_tests = 0
            support_tests = 0
            
            for candle in candles:
                try:
                    high_price = Decimal(str(candle[2]))
                    low_price = Decimal(str(candle[3]))
                    
                    # Test resistance level (within 1%) using Decimal arithmetic
                    if resistance_level > 0:  # Additional safety check
                        if abs(high_price - resistance_level) / resistance_level < Decimal('0.01'):
                            resistance_tests += 1
                    
                    # Test support level (within 1%) using Decimal arithmetic
                    if support_level > 0:  # Additional safety check
                        if abs(low_price - support_level) / support_level < Decimal('0.01'):
                            support_tests += 1
                            
                except Exception:
                    # Skip individual candle if processing fails
                    continue
            
            if resistance_tests > 0 and support_tests > 0:
                return f"R:{resistance_tests} tests, S:{support_tests} tests"
            elif resistance_tests > 0:
                return f"Resistance tested {resistance_tests} times"
            elif support_tests > 0:
                return f"Support tested {support_tests} times"
            else:
                return "No recent S/R tests"
                
        except Exception:
            return "S/R analysis failed"
    
    def _analyze_volume_relationship(self, candles: list) -> str:
        """Analyze volume-price relationship with Decimal precision and error handling."""
        try:
            if len(candles) < 3:
                return "Insufficient data"
            
            # Use Decimal for financial precision instead of float
            recent_volumes = []
            recent_closes = []
            
            for c in candles[-3:]:
                try:
                    recent_volumes.append(Decimal(str(c[5])))
                    recent_closes.append(Decimal(str(c[4])))
                except Exception:
                    continue  # Skip invalid candles
            
            if len(recent_volumes) < 3 or len(recent_closes) < 3:
                return "Insufficient valid data"
            
            # Calculate average volume using Decimal arithmetic
            if len(recent_volumes) == 0:
                return "No volume data available"
            
            avg_volume = sum(recent_volumes) / Decimal(str(len(recent_volumes)))
            
            # Determine trends using Decimal comparisons
            price_trend = "up" if recent_closes[-1] > recent_closes[0] else "down"
            volume_trend = "increasing" if recent_volumes[-1] > avg_volume else "decreasing"
            
            if price_trend == "up" and volume_trend == "increasing":
                return "Strong bullish confirmation"
            elif price_trend == "down" and volume_trend == "increasing":
                return "Strong bearish confirmation"
            elif price_trend == "up" and volume_trend == "decreasing":
                return "Weak bullish signal"
            elif price_trend == "down" and volume_trend == "decreasing":
                return "Weak bearish signal"
            else:
                return "Mixed signals"
                
        except Exception:
            return "Volume analysis failed"


# Factory function for easy instantiation
def create_market_data_service(cache_dir: str = "data/cache") -> MarketDataService:
    """Create a MarketDataService instance."""
    return MarketDataService(cache_dir=cache_dir)


if __name__ == "__main__":
    # Test the service
    service = create_market_data_service()
    
    try:
        # Test with BTC basic context
        btc_data = service.get_market_data("BTCUSDT", trace_id="test_trace_id_123")
        print("=== BTC Market Data Test (Basic) ===")
        print(btc_data.to_llm_context())
        
        print("\n" + "="*60 + "\n")
        
        # Test with enhanced candlestick analysis
        print("=== BTC Market Data Test (Enhanced) ===")
        print(service.get_enhanced_context(btc_data))
        
    except Exception as e:
        print(f"Test failed: {e}")