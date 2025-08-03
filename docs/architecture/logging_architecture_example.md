# Real Logging Architecture for MarketDataService


## Цепочка логов для диагностики MarketDataService

### **Как выглядит типичная цепочка логов:**

#### **Нормальный flow (BTCUSDT):**
```
17:47:00.000 INFO  → get_market_data("BTCUSDT") start [flow_btc_174700]
17:47:00.023 DEBUG → symbol validation passed [trd_001_...0023]
17:47:01.123 TRACE → raw Binance API response [180 candles received]
17:47:01.145 DEBUG → data validation completed [no anomalies]
17:47:02.200 TRACE → RSI input: close prices array [48 values]
17:47:02.223 DEBUG → RSI calculated: 35.17
17:47:02.245 TRACE → MACD input: EMA values [12/26 periods]
17:47:02.267 DEBUG → MACD signal: bearish
17:47:04.123 INFO  → MarketDataSet created successfully [4123ms total]
```

#### **Ошибка валидации:**
```
17:50:15.234 TRACE → validation input: RSI=105.67, MACD=bullish [raw data]
17:50:15.234 ERROR → validation failed: RSI must be 0-100, got 105.67
                  → flow terminated [flow_doge_175015]
```

#### **Enhanced context с частичными ошибками:**
```
17:47:05.800 DEBUG → 7-algorithm selection: 15 candles from 180
17:47:06.123 WARN  → pattern analysis failed, continuing with fallback
17:47:06.456 ERROR → complete enhanced failure → basic context returned
```

#### **Edge cases:**
```
17:47:07.000 WARN → empty h1_candles detected → minimal context mode
17:47:07.234 WARN → insufficient RSI periods (8<14) → fallback to 50.0
```

### **Принципы навигации:**

- **trace_id**: Последовательная нумерация для пошагового следования (trd_001_...0000 → trd_001_...0800)
- **flow_id**: Группировка всех логов одного запроса (flow_btc_20250803174700)
- **timestamp**: Точная временная последовательность (17:47:00.000 → 17:47:08.000)
- **level**: TRACE (сырые данные) → DEBUG → INFO → ERROR
- **context**: Входные данные + результаты + ошибки с полным контекстом

**ИИ может**: Найти проблему по trace_id → понять контекст по flow_id → увидеть сырые данные в TRACE → точно определить место и причину ошибки.

---

Этот документ демонстрирует структурированное логирование для MarketDataService на основе **фактически существующих методов и полей** в коде. Все примеры соответствуют реальной реализации [`src/market_data/market_data_service.py`](../../src/market_data/market_data_service.py).

## 1. Logging Levels и их применение

### CRITICAL - Системные сбои, требующие немедленного вмешательства
```json
{
  "timestamp": "2025-08-03T17:45:00.123Z",
  "level": "CRITICAL",
  "service": "MarketDataService",
  "operation": "get_market_data",
  "message": "Binance API completely unreachable",
  "context": {
    "symbol": "BTCUSDT",
    "error_type": "ConnectionError",
    "consecutive_failures": 15,
    "last_successful_call": "2025-08-03T16:30:00.000Z"
  },
  "tags": ["api_failure", "trading_halt", "emergency"],
  "trace_id": "trd_001_2025080317450012"
}
```

### ERROR - Операционные ошибки, влияющие на функциональность
```json
{
  "timestamp": "2025-08-03T17:45:15.456Z",
  "level": "ERROR", 
  "service": "MarketDataService",
  "operation": "_calculate_rsi",
  "message": "RSI calculation failed due to insufficient data",
  "context": {
    "symbol": "ETHUSDT",
    "required_periods": 14,
    "available_periods": 8,
    "fallback_value": "50.0"
  },
  "tags": ["calculation_error", "data_insufficiency", "fallback_used"],
  "trace_id": "trd_001_2025080317451545"
}
```

### WARNING - Потенциальные проблемы, не блокирующие работу
```json
{
  "timestamp": "2025-08-03T17:45:30.789Z",
  "level": "WARNING",
  "service": "MarketDataService",
  "operation": "_validate_symbol_input",
  "message": "Symbol validation edge case detected",
  "context": {
    "symbol": "MATICUSDT",
    "base_currency": "MATIC",
    "base_length": 5,
    "validation_result": "passed"
  },
  "tags": ["symbol_validation", "edge_case", "passed"],
  "trace_id": "trd_001_2025080317453078"
}
```

### INFO - Основные операции и состояния системы
```json
{
  "timestamp": "2025-08-03T17:45:45.234Z",
  "level": "INFO",
  "service": "MarketDataService",
  "operation": "get_enhanced_context",
  "message": "Enhanced context generated successfully",
  "context": {
    "symbol": "BTCUSDT",
    "processing_time_ms": 245,
    "key_candles_selected": 15,
    "total_candles_available": 180,
    "patterns_found": ["Shooting Star", "Hammer", "Strong Bear", "Doji"],
    "analysis_components": ["recent_trend", "patterns", "sr_tests", "volume_analysis"]
  },
  "tags": ["enhanced_context", "pattern_analysis", "success"],
  "trace_id": "trd_001_2025080317454523"
}
```

### DEBUG - Детальная отладочная информация
```json
{
  "timestamp": "2025-08-03T17:46:00.567Z",
  "level": "DEBUG",
  "service": "MarketDataService", 
  "operation": "_select_key_candles",
  "message": "Smart candlestick selection algorithm executed",
  "context": {
    "symbol": "BTCUSDT",
    "algorithm_results": {
      "recent_5": 5,
      "extremes": 4,
      "high_volume": 8,
      "big_moves": 3,
      "patterns": 6,
      "after_deduplication": 15
    },
    "selection_efficiency": "91.7%",
    "processing_time_ms": 45
  },
  "tags": ["algorithm_debug", "candlestick_selection", "optimization"],
  "trace_id": "trd_001_2025080317460056"
}
```

### TRACE - Максимальная детализация для глубокой отладки
```json
{
  "timestamp": "2025-08-03T17:46:15.890Z",
  "level": "TRACE",
  "service": "MarketDataService",
  "operation": "_identify_patterns",
  "message": "Pattern identification step-by-step analysis",
  "context": {
    "symbol": "BTCUSDT",
    "candle_index": 142,
    "candle_data": {
      "open": "112500.00",
      "high": "113200.00", 
      "low": "112100.00",
      "close": "112650.00",
      "volume": "234.56789"
    },
    "pattern_calculations": {
      "body_size": "150.00",
      "total_range": "1100.00",
      "body_ratio": "0.136",
      "upper_shadow": "550.00",
      "lower_shadow": "400.00",
      "upper_shadow_ratio": "0.500",
      "lower_shadow_ratio": "0.364"
    },
    "pattern_result": "No significant pattern"
  },
  "tags": ["pattern_trace", "calculation_details", "candle_analysis"],
  "trace_id": "trd_001_2025080317461589"
}
```

## 2. Data Flow Tracing реальных методов

### Начало обработки - get_market_data()
```json
{
  "timestamp": "2025-08-03T17:47:00.000Z",
  "level": "INFO",
  "service": "MarketDataService",
  "operation": "get_market_data",
  "message": "Market data request initiated",
  "context": {
    "symbol": "BTCUSDT",
    "cache_dir": "data/cache",
    "request_id": "req_12345"
  },
  "flow": {
    "stage": "initiation",
    "next_stage": "symbol_validation",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["flow_start", "market_data"],
  "trace_id": "trd_001_2025080317470000"
}
```

### Этап валидации символа - _validate_symbol_input()
```json
{
  "timestamp": "2025-08-03T17:47:00.234Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "_validate_symbol_input",
  "message": "Symbol validation completed",
  "context": {
    "symbol": "BTCUSDT",
    "base_currency": "BTC",
    "base_length": 3,
    "validation_checks": {
      "non_empty": true,
      "usdt_suffix": true,
      "length_valid": true,
      "alpha_uppercase": true,
      "single_usdt": true
    }
  },
  "flow": {
    "stage": "symbol_validation",
    "previous_stage": "initiation",
    "next_stage": "data_collection",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["symbol_validation", "success"],
  "trace_id": "trd_001_2025080317470023"
}
```

### Этап сбора данных - _get_klines() (API Calls)
```json
{
  "timestamp": "2025-08-03T17:47:01.000Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "_get_klines",
  "message": "Initiating Binance API calls",
  "context": {
    "symbol": "BTCUSDT",
    "api_calls_planned": {
      "daily_180": {"interval": "1d", "limit": 180},
      "h4_84": {"interval": "4h", "limit": 84}, 
      "h1_48": {"interval": "1h", "limit": 48}
    }
  },
  "flow": {
    "stage": "data_collection",
    "previous_stage": "symbol_validation",
    "next_stage": "raw_data_processing",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["api_initiation", "data_collection"],
  "trace_id": "trd_001_2025080317470100"
}
```

### Raw Binance API Response - TRACE level
```json
{
  "timestamp": "2025-08-03T17:47:01.234Z",
  "level": "TRACE",
  "service": "MarketDataService",
  "operation": "_get_klines",
  "message": "Raw Binance API response received",
  "context": {
    "symbol": "BTCUSDT",
    "interval": "1d",
    "limit": 180,
    "request_url": "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=180",
    "response_status": 200,
    "response_headers": {
      "content-type": "application/json",
      "x-mbx-uuid": "12345678-abcd-efgh-ijkl-123456789012"
    },
    "raw_data_sample": [
      [
        1704067200000,  // Open time
        "42850.01000000",  // Open
        "43200.50000000",  // High
        "42500.75000000",  // Low
        "42980.25000000",  // Close
        "234.56789012",    // Volume
        1704153599999,     // Close time
        "10054321.12345678",  // Quote asset volume
        5234,             // Number of trades
        "123.45678901",   // Taker buy base asset volume
        "5289765.43210987",  // Taker buy quote asset volume
        "0"               // Ignore
      ],
      [
        1704153600000,
        "42980.25000000",
        "43450.80000000", 
        "42750.10000000",
        "43125.60000000",
        "345.67890123",
        1704239999999,
        "14876543.21098765",
        6789,
        "178.90123456",
        "7654321.09876543",
        "0"
      ]
    ],
    "total_candles_received": 180,
    "data_integrity": {
      "all_arrays_length_12": true,
      "no_null_values": true,
      "timestamps_sequential": true,
      "prices_positive": true,
      "volumes_positive": true
    }
  },
  "flow": {
    "stage": "raw_data_processing",
    "previous_stage": "data_collection",
    "next_stage": "data_validation",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["raw_api_data", "binance_response", "data_integrity"],
  "trace_id": "trd_001_2025080317470123"
}
```

### Raw Data Validation - DEBUG level
```json
{
  "timestamp": "2025-08-03T17:47:01.456Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "_get_klines",
  "message": "Raw data validation and conversion",
  "context": {
    "symbol": "BTCUSDT",
    "interval": "1d",
    "validation_results": {
      "expected_fields": 12,
      "actual_fields": 12,
      "timestamp_format": "unix_milliseconds",
      "price_format": "string_decimal",
      "volume_format": "string_decimal",
      "data_anomalies": []
    },
    "conversion_process": {
      "timestamps_converted": 180,
      "prices_converted": 720,  // 180 * 4 (OHLC)
      "volumes_converted": 180,
      "decimal_precision_maintained": true,
      "conversion_errors": 0
    },
    "data_quality_checks": {
      "price_consistency": "OHLC relationships valid",
      "volume_sanity": "All volumes > 0",
      "timestamp_gaps": "No missing periods",
      "extreme_values": "No outliers detected"
    }
  },
  "flow": {
    "stage": "data_validation",
    "previous_stage": "raw_data_processing",
    "next_stage": "technical_indicators",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["data_validation", "conversion", "quality_check"],
  "trace_id": "trd_001_2025080317470145"
}
```

### API Calls Completion Summary
```json
{
  "timestamp": "2025-08-03T17:47:01.789Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "_get_klines",
  "message": "All Binance API calls completed successfully",
  "context": {
    "symbol": "BTCUSDT",
    "api_calls_completed": {
      "daily_180": {"interval": "1d", "limit": 180, "status": "SUCCESS", "response_time_ms": 145},
      "h4_84": {"interval": "4h", "limit": 84, "status": "SUCCESS", "response_time_ms": 98}, 
      "h1_48": {"interval": "1h", "limit": 48, "status": "SUCCESS", "response_time_ms": 76}
    },
    "total_candles_received": 312,
    "total_api_time_ms": 319
  },
  "flow": {
    "stage": "data_validation",
    "previous_stage": "raw_data_processing",
    "next_stage": "technical_indicators",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["api_success", "data_collection_complete"],
  "trace_id": "trd_001_2025080317470178"
}
```

## 3. Technical Indicators с Raw Data Input

### RSI Calculation with Raw Data - _calculate_rsi()
```json
{
  "timestamp": "2025-08-03T17:47:02.000Z",
  "level": "TRACE",
  "service": "MarketDataService",
  "operation": "_calculate_rsi",
  "message": "Raw price data for RSI calculation",
  "context": {
    "symbol": "BTCUSDT",
    "calculation_input": {
      "period": 14,
      "total_data_points": 48,
      "price_series_sample": [
        {"timestamp": "2025-07-20T00:00:00Z", "close": "42980.25"},
        {"timestamp": "2025-07-21T00:00:00Z", "close": "43125.60"},
        {"timestamp": "2025-07-22T00:00:00Z", "close": "42850.75"},
        {"timestamp": "2025-07-23T00:00:00Z", "close": "43200.10"},
        {"timestamp": "2025-07-24T00:00:00Z", "close": "43050.50"}
      ],
      "full_close_prices": [
        "42980.25", "43125.60", "42850.75", "43200.10", "43050.50",
        "43180.25", "42920.80", "43315.40", "43125.75", "42995.60",
        "43220.15", "43085.90", "42875.25", "43165.80", "43045.35"
      ],
      "price_changes": [
        "145.35", "-274.85", "349.35", "-149.60", "129.75",
        "-259.45", "394.60", "-189.65", "-130.15", "224.55",
        "-134.25", "-210.65", "290.55", "-120.45"
      ]
    },
    "data_preparation": {
      "gains_count": 8,
      "losses_count": 6,
      "zero_changes": 0,
      "average_gain": "234.567890",
      "average_loss": "432.109876"
    }
  },
  "flow": {
    "stage": "technical_indicators",
    "previous_stage": "data_validation",
    "next_stage": "rsi_calculation_complete",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["calculation_input", "rsi_data", "price_series"],
  "trace_id": "trd_001_2025080317470200"
}
```

### RSI Calculation Complete - DEBUG level
```json
{
  "timestamp": "2025-08-03T17:47:02.234Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "_calculate_rsi",
  "message": "RSI calculation with division by zero protection",
  "context": {
    "symbol": "BTCUSDT",
    "period": 14,
    "data_length": 48,
    "calculation_data": {
      "final_gain": "234.567890",
      "final_loss": "432.109876",
      "relative_strength": "0.542857",
      "rsi_value": "35.17"
    },
    "edge_case_handling": {
      "zero_loss": false,
      "zero_gain": false,
      "insufficient_data": false
    },
    "precision": "decimal_2_places",
    "calculation_time_ms": 8
  },
  "flow": {
    "stage": "rsi_calculation_complete",
    "previous_stage": "technical_indicators",
    "next_stage": "macd_calculation",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["rsi_calculation", "technical_analysis", "financial_precision"],
  "trace_id": "trd_001_2025080317470223"
}
```

### MACD with Raw Data Input - _calculate_macd_signal()
```json
{
  "timestamp": "2025-08-03T17:47:02.456Z",
  "level": "TRACE",
  "service": "MarketDataService", 
  "operation": "_calculate_macd_signal",
  "message": "Raw price data for MACD calculation",
  "context": {
    "symbol": "BTCUSDT",
    "calculation_input": {
      "ema_12_period": 12,
      "ema_26_period": 26,
      "signal_period": 9,
      "total_data_points": 48,
      "close_prices_for_ema": [
        "42980.25", "43125.60", "42850.75", "43200.10", "43050.50",
        "43180.25", "42920.80", "43315.40", "43125.75", "42995.60",
        "43220.15", "43085.90", "42875.25", "43165.80", "43045.35",
        "43275.20", "42945.85", "43195.60", "43080.25", "42925.70"
      ],
      "ema_12_values": [
        "42980.25", "43052.93", "42951.84", "43075.97", "43063.23",
        "43121.74", "43021.27", "43168.34", "43147.04", "43071.32"
      ],
      "ema_26_values": [
        "42980.25", "43020.87", "42965.45", "43048.23", "43049.89",
        "43089.56", "43055.18", "43125.79", "43125.77", "43089.95"
      ]
    },
    "intermediate_calculations": {
      "macd_line_values": [
        "0.00", "32.06", "-13.61", "27.74", "13.34",
        "32.18", "-33.91", "42.55", "21.27", "-18.63"
      ],
      "signal_line_values": [
        "0.00", "8.02", "-5.58", "6.58", "8.46",
        "14.82", "8.91", "17.73", "18.50", "8.94"
      ]
    }
  },
  "flow": {
    "stage": "macd_calculation",
    "previous_stage": "rsi_calculation_complete",
    "next_stage": "macd_signal_complete",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["macd_input", "ema_calculation", "signal_data"],
  "trace_id": "trd_001_2025080317470245"
}
```

### MACD Signal Complete - DEBUG level
```json
{
  "timestamp": "2025-08-03T17:47:02.678Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "_calculate_macd_signal",
  "message": "MACD signal determined",
  "context": {
    "symbol": "BTCUSDT",
    "data_length": 48,
    "ema_calculations": {
      "ema_12": "112756.45",
      "ema_26": "113123.78",
      "macd_line": "-367.33",
      "signal_line": "-234.56"
    },
    "signal_result": "bearish",
    "calculation_time_ms": 12
  },
  "flow": {
    "stage": "macd_signal_complete",
    "previous_stage": "macd_calculation",
    "next_stage": "moving_averages",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["macd_calculation", "signal_determination"],
  "trace_id": "trd_001_2025080317470267"
}
```

### Moving Average - _calculate_ma()
```json
{
  "timestamp": "2025-08-03T17:47:02.890Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "_calculate_ma",
  "message": "Moving average calculated with Decimal precision",
  "context": {
    "symbol": "BTCUSDT",
    "period": 20,
    "data_length": 48,
    "calculation_method": "rolling_window",
    "ma_value": "113450.25",
    "fallback_used": false,
    "calculation_time_ms": 5
  },
  "flow": {
    "stage": "moving_averages",
    "previous_stage": "macd_signal_complete",
    "next_stage": "btc_correlation",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["ma_calculation", "decimal_precision"],
  "trace_id": "trd_001_2025080317470289"
}
```

### BTC Correlation with Raw Data - _calculate_btc_correlation()
```json
{
  "timestamp": "2025-08-03T17:47:03.100Z",
  "level": "TRACE",
  "service": "MarketDataService",
  "operation": "_calculate_btc_correlation",
  "message": "Raw price series for correlation calculation",
  "context": {
    "symbol": "ETHUSDT",
    "correlation_input": {
      "btc_price_series": [
        "42980.25", "43125.60", "42850.75", "43200.10", "43050.50",
        "43180.25", "42920.80", "43315.40", "43125.75", "42995.60",
        "43220.15", "43085.90", "42875.25", "43165.80", "43045.35",
        "43275.20", "42945.85", "43195.60", "43080.25", "42925.70"
      ],
      "symbol_price_series": [
        "2654.30", "2678.45", "2642.15", "2685.20", "2661.85",
        "2689.50", "2639.75", "2701.30", "2673.60", "2648.90",
        "2692.45", "2669.20", "2641.85", "2688.75", "2663.40",
        "2695.80", "2645.30", "2691.15", "2665.85", "2643.20"
      ]
    },
    "statistical_calculation": {
      "data_length": 20,
      "btc_mean": "43086.64",
      "symbol_mean": "2666.87",
      "btc_variance": "19234.56",
      "symbol_variance": "567.89",
      "covariance": "3456.78",
      "correlation_coefficient": "0.8923",
      "calculation_method": "pearson"
    },
    "data_quality": {
      "missing_values": 0,
      "data_alignment": "synchronized",
      "outliers_detected": 0,
      "correlation_strength": "strong_positive"
    }
  },
  "flow": {
    "stage": "btc_correlation",
    "previous_stage": "moving_averages",
    "next_stage": "correlation_complete",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["correlation_input", "btc_comparison", "statistical_data"],
  "trace_id": "trd_001_2025080317470310"
}
```

### BTC Correlation Complete - DEBUG level
```json
{
  "timestamp": "2025-08-03T17:47:03.334Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "_calculate_btc_correlation",
  "message": "BTC correlation analysis completed",
  "context": {
    "symbol": "ETHUSDT",
    "btc_data_length": 48,
    "symbol_data_length": 48,
    "min_length": 48,
    "correlation_value": "0.892",
    "pearson_method": true,
    "calculation_time_ms": 18
  },
  "flow": {
    "stage": "correlation_complete",
    "previous_stage": "btc_correlation",
    "next_stage": "volume_analysis",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["correlation_analysis", "btc_relationship"],
  "trace_id": "trd_001_2025080317470333"
}
```

### Volume Analysis with Raw Data - _analyze_volume_profile()
```json
{
  "timestamp": "2025-08-03T17:47:03.556Z",
  "level": "TRACE",
  "service": "MarketDataService",
  "operation": "_analyze_volume_profile",
  "message": "Raw volume data for analysis",
  "context": {
    "symbol": "BTCUSDT",
    "volume_data_input": {
      "total_periods": 48,
      "recent_24h_volumes": [
        "234.56789012", "345.67890123", "456.78901234", "567.89012345",
        "123.45678901", "234.56789012", "345.67890123", "456.78901234",
        "567.89012345", "678.90123456", "789.01234567", "890.12345678",
        "901.23456789", "012.34567890", "123.45678901", "234.56789012",
        "345.67890123", "456.78901234", "567.89012345", "678.90123456",
        "789.01234567", "890.12345678", "901.23456789", "012.34567890"
      ],
      "historical_baseline_volumes": [
        "198.76543210", "287.65432109", "376.54321098", "465.43210987",
        "554.32109876", "643.21098765", "732.10987654", "821.09876543",
        "910.98765432", "109.87654321", "298.76543210", "387.65432109",
        "476.54321098", "565.43210987", "654.32109876", "743.21098765",
        "832.10987654", "921.09876543", "210.98765432", "309.87654321",
        "498.76543210", "587.65432109", "676.54321098", "765.43210987"
      ]
    },
    "statistical_analysis": {
      "recent_avg": "1234567.89",
      "historical_avg": "987654.32", 
      "volume_ratio": "1.25",
      "std_deviation": "234.56",
      "volume_spikes": [
        {"index": 15, "volume": "890.12345678", "spike_ratio": "2.34"},
        {"index": 22, "volume": "901.23456789", "spike_ratio": "2.18"}
      ]
    }
  },
  "flow": {
    "stage": "volume_analysis",
    "previous_stage": "correlation_complete",
    "next_stage": "volume_complete",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["volume_raw_data", "statistical_analysis", "market_activity"],
  "trace_id": "trd_001_2025080317470355"
}
```

### Volume Profile Complete - DEBUG level
```json
{
  "timestamp": "2025-08-03T17:47:03.789Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "_analyze_volume_profile",
  "message": "Volume profile analysis completed",
  "context": {
    "symbol": "BTCUSDT",
    "data_length": 48,
    "recent_24h_avg": "1234567.89",
    "historical_avg": "987654.32",
    "volume_ratio": "1.25",
    "profile_result": "normal",
    "thresholds": {
      "high_threshold": "1.5",
      "low_threshold": "0.5"
    }
  },
  "flow": {
    "stage": "volume_complete",
    "previous_stage": "volume_analysis",
    "next_stage": "market_context_creation",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["volume_analysis", "market_profile"],
  "trace_id": "trd_001_2025080317470378"
}
```

### MarketDataSet Creation Complete
```json
{
  "timestamp": "2025-08-03T17:47:04.123Z",
  "level": "INFO",
  "service": "MarketDataService",
  "operation": "get_market_data",
  "message": "MarketDataSet created successfully",
  "context": {
    "symbol": "BTCUSDT",
    "timestamp": "2025-08-03T17:47:04.123Z",
    "rsi_14": "35.17",
    "macd_signal": "bearish",
    "ma_20": "113450.25",
    "ma_50": "115200.75",
    "ma_trend": "downtrend",
    "btc_correlation": "0.892",
    "volume_profile": "normal",
    "support_level": "110500.00",
    "resistance_level": "115800.00",
    "total_processing_time_ms": 4123
  },
  "flow": {
    "stage": "completion",
    "previous_stage": "market_context_creation",
    "flow_completion": true,
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["flow_complete", "market_data_set"],
  "trace_id": "trd_001_2025080317470412"
}
```

## 4. Enhanced Context Analysis - get_enhanced_context()

### Enhanced Context Generation
```json
{
  "timestamp": "2025-08-03T17:47:05.000Z",
  "level": "INFO",
  "service": "MarketDataService",
  "operation": "get_enhanced_context",
  "message": "Enhanced context with candlestick analysis",
  "context": {
    "symbol": "BTCUSDT",
    "basic_context_length": 850,
    "enhanced_components": {
      "recent_trend": "Downward bias",
      "patterns": ["Shooting Star", "Hammer", "Strong Bear", "Doji"],
      "sr_tests": "R:1 tests, S:1 tests",
      "volume_analysis": "Weak bearish signal"
    },
    "key_candles_analyzed": 15,
    "total_context_length": 1200,
    "processing_time_ms": 189
  },
  "flow": {
    "stage": "enhanced_context_init",
    "next_stage": "pattern_analysis",
    "flow_id": "flow_enh_20250803174705"
  },
  "tags": ["enhanced_context", "candlestick_analysis", "success"],
  "trace_id": "trd_002_2025080317470500"
}
```

### Pattern Analysis with Raw Data - _identify_patterns()
```json
{
  "timestamp": "2025-08-03T17:47:05.234Z",
  "level": "TRACE", 
  "service": "MarketDataService",
  "operation": "_identify_patterns",
  "message": "Raw candlestick data for pattern identification",
  "context": {
    "symbol": "BTCUSDT",
    "candle_raw_data": [
      {
        "index": 140,
        "timestamp": "2025-08-02T20:00:00Z",
        "ohlcv": {
          "open": "112500.00000000",
          "high": "113200.00000000", 
          "low": "112100.00000000",
          "close": "112650.00000000",
          "volume": "234.56789012"
        },
        "calculated_metrics": {
          "body_size": "150.00",
          "total_range": "1100.00",
          "upper_shadow": "550.00",
          "lower_shadow": "400.00",
          "body_ratio": "0.136364",
          "upper_shadow_ratio": "0.500000",
          "lower_shadow_ratio": "0.363636"
        }
      },
      {
        "index": 141,
        "timestamp": "2025-08-03T00:00:00Z", 
        "ohlcv": {
          "open": "112650.00000000",
          "high": "112750.00000000",
          "low": "111800.00000000", 
          "close": "111950.00000000",
          "volume": "345.67890123"
        },
        "calculated_metrics": {
          "body_size": "700.00",
          "total_range": "950.00",
          "upper_shadow": "100.00", 
          "lower_shadow": "150.00",
          "body_ratio": "0.736842",
          "upper_shadow_ratio": "0.105263",
          "lower_shadow_ratio": "0.157895"
        }
      }
    ],
    "pattern_thresholds": {
      "doji_body_threshold": "0.1",
      "hammer_shadow_threshold": "0.6", 
      "shooting_star_threshold": "0.6",
      "strong_body_threshold": "0.7",
      "minimal_range": "100.00"
    },
    "pattern_detection_results": [
      {
        "candle_index": 140,
        "detected_patterns": [],
        "rejection_reasons": ["body_ratio_too_high", "shadows_not_significant"]
      },
      {
        "candle_index": 141,
        "detected_patterns": ["Strong Bear"],
        "pattern_confidence": "high",
        "pattern_strength": "0.737"
      }
    ]
  },
  "flow": {
    "stage": "pattern_analysis",
    "previous_stage": "enhanced_context_init",
    "next_stage": "pattern_complete",
    "flow_id": "flow_enh_20250803174705"
  },
  "tags": ["pattern_raw_data", "candlestick_metrics", "pattern_detection"],
  "trace_id": "trd_002_2025080317470523"
}
```

### Pattern Analysis Complete - DEBUG level
```json
{
  "timestamp": "2025-08-03T17:47:05.456Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "_identify_patterns",
  "message": "Candlestick pattern identification",
  "context": {
    "symbol": "BTCUSDT",
    "candles_processed": 15,
    "patterns_found": {
      "Hammer": 2,
      "Shooting Star": 1,
      "Strong Bear": 1,
      "Doji": 1
    },
    "pattern_thresholds": {
      "doji_body_ratio": "0.1",
      "hammer_shadow_ratio": "0.6",
      "strong_body_ratio": "0.7"
    },
    "processing_time_ms": 23
  },
  "flow": {
    "stage": "pattern_complete",
    "previous_stage": "pattern_analysis",
    "next_stage": "sr_analysis",
    "flow_id": "flow_enh_20250803174705"
  },
  "tags": ["pattern_identification", "candlestick_analysis"],
  "trace_id": "trd_002_2025080317470545"
}
```

### Support/Resistance with Raw Data - _analyze_sr_tests()
```json
{
  "timestamp": "2025-08-03T17:47:05.678Z",
  "level": "TRACE",
  "service": "MarketDataService",
  "operation": "_analyze_sr_tests", 
  "message": "Raw price data for support/resistance analysis",
  "context": {
    "symbol": "BTCUSDT",
    "price_levels_input": {
      "support_candidate": "110500.00",
      "resistance_candidate": "115800.00", 
      "test_candles": [
        {
          "timestamp": "2025-08-01T08:00:00Z",
          "low": "110450.25",
          "high": "112300.75",
          "support_distance": "49.75",
          "resistance_distance": "3499.25"
        },
        {
          "timestamp": "2025-08-01T12:00:00Z", 
          "low": "110520.10",
          "high": "113450.60",
          "support_distance": "20.10",
          "resistance_distance": "2349.40"
        },
        {
          "timestamp": "2025-08-02T16:00:00Z",
          "low": "115750.80", 
          "high": "115850.25",
          "support_distance": "5250.80",
          "resistance_distance": "49.20"
        }
      ]
    },
    "test_analysis": {
      "support_test_threshold": "100.00",
      "resistance_test_threshold": "100.00",
      "support_tests_found": 2,
      "resistance_tests_found": 1,
      "test_details": [
        {
          "level_type": "support",
          "test_price": "110450.25",
          "test_distance": "49.75",
          "test_result": "valid_test"
        },
        {
          "level_type": "support", 
          "test_price": "110520.10",
          "test_distance": "20.10",
          "test_result": "valid_test"
        },
        {
          "level_type": "resistance",
          "test_price": "115850.25", 
          "test_distance": "49.20",
          "test_result": "valid_test"
        }
      ]
    }
  },
  "flow": {
    "stage": "sr_analysis",
    "previous_stage": "pattern_complete",
    "next_stage": "enhanced_complete",
    "flow_id": "flow_enh_20250803174705"
  },
  "tags": ["sr_raw_data", "level_testing", "price_analysis"],
  "trace_id": "trd_002_2025080317470567"
}
```

## 5. Error Handling реальных сценариев

### Network Error - requests.exceptions.RequestException
```json
{
  "timestamp": "2025-08-03T17:50:00.000Z",
  "level": "ERROR",
  "service": "MarketDataService",
  "operation": "_get_klines",
  "message": "Binance API request failed",
  "context": {
    "symbol": "ADAUSDT",
    "interval": "1h",
    "limit": 48,
    "error_type": "requests.exceptions.Timeout",
    "error_message": "HTTPSConnectionPool(host='api.binance.com', port=443): Read timed out.",
    "retry_attempt": 1,
    "fallback_action": "raise_exception"
  },
  "flow": {
    "stage": "data_collection_failed",
    "previous_stage": "symbol_validation",
    "flow_termination": true,
    "flow_id": "flow_ada_20250803175000"
  },
  "tags": ["network_error", "api_failure", "timeout"],
  "trace_id": "trd_003_2025080317500000"
}
```

### Validation Error - MarketDataSet.__post_init__()
```json
{
  "timestamp": "2025-08-03T17:50:15.234Z",
  "level": "ERROR",
  "service": "MarketDataService",
  "operation": "get_market_data",
  "message": "MarketDataSet validation failed",
  "context": {
    "symbol": "DOGEUSDT",
    "validation_error": "RSI must be between 0 and 100, got: 105.67",
    "failed_field": "rsi_14",
    "calculated_value": "105.67",
    "validation_stage": "__post_init__"
  },
  "flow": {
    "stage": "validation_failed",
    "previous_stage": "market_context_creation",
    "flow_termination": true,
    "flow_id": "flow_doge_20250803175015"
  },
  "tags": ["validation_error", "data_integrity", "market_data_set"],
  "trace_id": "trd_004_2025080317501523"
}
```

### Calculation Error - Division by zero в корреляции
```json
{
  "timestamp": "2025-08-03T17:50:30.567Z",
  "level": "WARNING",
  "service": "MarketDataService",
  "operation": "_calculate_btc_correlation",
  "message": "BTC correlation calculation failed, returning None",
  "context": {
    "symbol": "LINKUSDT",
    "error_type": "BTC data fetch failed",
    "error_message": "Failed to calculate BTC correlation for LINKUSDT: HTTP 404",
    "fallback_value": null,
    "impact": "btc_correlation field will be None"
  },
  "flow": {
    "stage": "correlation_failed",
    "previous_stage": "moving_averages",
    "next_stage": "volume_analysis",

## 8. MarketDataSet Validation Input Data & Errors

### Validation Input Data - TRACE level
```json
{
  "timestamp": "2025-08-03T17:47:04.200Z",
  "level": "TRACE",
  "service": "MarketDataService",
  "operation": "MarketDataSet.__post_init__",
  "message": "Validation input data captured",
  "context": {
    "symbol": "BTCUSDT",
    "timestamp": "2025-08-03T17:47:04.123Z",
    "dataframe_sizes": {
      "daily_candles": 180,
      "h4_candles": 84,
      "h1_candles": 48
    },
    "dataframe_columns": {
      "daily_candles": ["timestamp", "open", "high", "low", "close", "volume"],
      "h4_candles": ["timestamp", "open", "high", "low", "close", "volume"],
      "h1_candles": ["timestamp", "open", "high", "low", "close", "volume"]
    },
    "technical_indicators": {
      "rsi_14": "35.17",
      "macd_signal": "bearish",
      "ma_20": "113450.25",
      "ma_50": "115200.75",
      "ma_trend": "downtrend"
    },
    "optional_fields": {
      "btc_correlation": "0.892",
      "fear_greed_index": null,
      "volume_profile": "normal",
      "support_level": "110500.00",
      "resistance_level": "115800.00"
    },
    "dataframe_sample_data": {
      "h1_last_row": {
        "timestamp": "2025-08-03T16:00:00Z",
        "open": "112450.25",
        "high": "112950.75",
        "low": "112100.10",
        "close": "112650.50",
        "volume": "234.56789012"
      }
    }
  },
  "flow": {
    "stage": "validation_input",
    "previous_stage": "market_context_creation",
    "next_stage": "validation_execution",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["validation_input", "market_data_set", "pre_validation"],
  "trace_id": "trd_001_2025080317470420"
}
```

### Validation Error - ERROR level
```json
{
  "timestamp": "2025-08-03T17:50:15.234Z",
  "level": "ERROR",
  "service": "MarketDataService",
  "operation": "MarketDataSet.__post_init__",
  "message": "MarketDataSet validation failed",
  "context": {
    "symbol": "DOGEUSDT",
    "validation_stage": "_validate_technical_indicators",
    "validation_error": "RSI must be between 0 and 100, got: 105.67",
    "failed_field": "rsi_14",
    "failed_value": "105.67",
    "input_data": {
      "rsi_14": "105.67",
      "macd_signal": "bullish",
      "ma_20": "0.12345",
      "ma_50": "0.13456",
      "ma_trend": "uptrend"
    },
    "validation_context": {
      "expected_range": "0-100",
      "actual_value": "105.67",
      "value_type": "Decimal"
    }
  },
  "flow": {
    "stage": "validation_failed",
    "previous_stage": "validation_execution",
    "flow_termination": true,
    "flow_id": "flow_doge_20250803175015"
  },
  "tags": ["validation_error", "rsi_bounds", "technical_indicators"],
  "trace_id": "trd_004_2025080317501523"
}
```

### DataFrame Validation Error - ERROR level
```json
{
  "timestamp": "2025-08-03T17:51:30.456Z",
  "level": "ERROR",
  "service": "MarketDataService",
  "operation": "MarketDataSet.__post_init__",
  "message": "DataFrame validation failed",
  "context": {
    "symbol": "ADAUSDT",
    "validation_stage": "_validate_dataframes",
    "validation_error": "h1_candles has invalid OHLC data: high < max(open, close)",
    "failed_dataframe": "h1_candles",
    "problematic_rows": [
      {
        "index": 23,
        "timestamp": "2025-08-02T15:00:00Z",
        "open": "0.45123",
        "high": "0.44890",  // High < Open (invalid)
        "low": "0.44500",
        "close": "0.45000",
        "volume": "123456.789"
      },
      {
        "index": 31,
        "timestamp": "2025-08-02T23:00:00Z",
        "open": "0.44800",
        "high": "0.44950",
        "low": "0.44700",
        "close": "0.45200",  // Close > High (invalid)
        "volume": "987654.321"
      }
    ],
    "dataframe_stats": {
      "total_rows": 48,
      "invalid_rows": 2,
      "validation_checks_passed": {
        "non_empty": true,
        "required_columns": true,
        "numeric_types": true,
        "no_nan_values": true,
        "ohlc_logic": false
      }
    }
  },
  "flow": {
    "stage": "validation_failed",
    "previous_stage": "validation_execution",
    "flow_termination": true,
    "flow_id": "flow_ada_20250803175130"
  },
  "tags": ["validation_error", "ohlc_logic", "dataframe_integrity"],
  "trace_id": "trd_005_2025080317513045"
}
```

## 9. Enhanced Context 7-Algorithm Breakdown

### Algorithm Execution Summary - DEBUG level
```json
{
  "timestamp": "2025-08-03T17:47:05.800Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "_select_key_candles",
  "message": "7-algorithm key candle selection completed",
  "context": {
    "symbol": "BTCUSDT",
    "input_candles": 180,
    "algorithm_results": {
      "algorithm_1_recent": {
        "name": "Recent 5 candles",
        "candles_selected": 5,
        "timestamps": ["2025-08-01T00:00:00Z", "2025-08-02T00:00:00Z", "2025-08-03T00:00:00Z"]
      },
      "algorithm_2_extremes": {
        "name": "Extreme candles (30-day)",
        "candles_selected": 2,
        "highest_high": {"timestamp": "2025-07-15T00:00:00Z", "high": "118500.75"},
        "lowest_low": {"timestamp": "2025-07-22T00:00:00Z", "low": "108200.25"}
      },
      "algorithm_3_volume": {
        "name": "High volume (top 10%)",
        "candles_selected": 3,
        "volume_threshold": "890123.456",
        "top_volumes": [
          {"timestamp": "2025-07-28T00:00:00Z", "volume": "1234567.89"},
          {"timestamp": "2025-07-30T00:00:00Z", "volume": "1098765.43"},
          {"timestamp": "2025-08-01T00:00:00Z", "volume": "987654.32"}
        ]
      },
      "algorithm_4_big_moves": {
        "name": "Big moves (>3% change)",
        "candles_selected": 3,
        "change_threshold": "3.0%",
        "big_moves": [
          {"timestamp": "2025-07-25T00:00:00Z", "change_pct": "4.7%", "direction": "up"},
          {"timestamp": "2025-07-29T00:00:00Z", "change_pct": "-5.2%", "direction": "down"},
          {"timestamp": "2025-08-02T00:00:00Z", "change_pct": "3.8%", "direction": "up"}
        ]
      },
      "algorithm_5_patterns": {
        "name": "Pattern candles",
        "candles_selected": 4,
        "patterns_found": {
          "Hammer": 2,
          "Shooting Star": 1,
          "Doji": 1
        }
      },
      "algorithm_6_sr_tests": {
        "name": "Support/Resistance tests",
        "candles_selected": 0,
        "reason": "No S/R levels provided"
      },
      "algorithm_7_deduplication": {
        "name": "Timestamp deduplication",
        "input_candles": 17,
        "duplicate_timestamps": 2,
        "final_candles": 15
      }
    },
    "final_result": {
      "total_key_candles": 15,
      "selection_efficiency": "8.3%",
      "processing_time_ms": 67
    }
  },
  "flow": {
    "stage": "key_candle_selection",
    "previous_stage": "enhanced_context_init",
    "next_stage": "pattern_analysis",
    "flow_id": "flow_enh_20250803174705"
  },
  "tags": ["algorithm_breakdown", "key_candle_selection", "7_algorithms"],
  "trace_id": "trd_002_2025080317470580"
}
```

### Algorithm 6 Details - S/R Test Candles - TRACE level
```json
{
  "timestamp": "2025-08-03T17:47:05.890Z",
  "level": "TRACE",
  "service": "MarketDataService",
  "operation": "_find_sr_test_candles",
  "message": "Support/Resistance test candle analysis",
  "context": {
    "symbol": "BTCUSDT",
    "input_data": {
      "candles_count": 20,
      "support_level": "110500.00",
      "resistance_level": "115800.00",
      "test_threshold": "1.0%"
    },
    "test_analysis": {
      "support_tests": [
        {
          "timestamp": "2025-07-28T00:00:00Z",
          "low": "110445.25",
          "distance_from_support": "54.75",
          "distance_pct": "0.05%",
          "test_result": "valid_support_test"
        },
        {
          "timestamp": "2025-08-01T00:00:00Z",
          "low": "110520.10",
          "distance_from_support": "20.10",
          "distance_pct": "0.02%",
          "test_result": "valid_support_test"
        }
      ],
      "resistance_tests": [
        {
          "timestamp": "2025-07-30T00:00:00Z",
          "high": "115845.60",
          "distance_from_resistance": "45.60",
          "distance_pct": "0.04%",
          "test_result": "valid_resistance_test"
        }
      ]
    },
    "selection_result": {
      "support_test_candles": 2,
      "resistance_test_candles": 1,
      "total_sr_candles": 3
    }
  },
  "flow": {
    "stage": "sr_test_analysis",
    "previous_stage": "key_candle_selection",
    "next_stage": "deduplication",
    "flow_id": "flow_enh_20250803174705"
  },
  "tags": ["sr_test_candles", "algorithm_6", "support_resistance"],
  "trace_id": "trd_002_2025080317470589"
}
```

## 10. Error Recovery Chain в Enhanced Context

### Component Failure Recovery - WARNING level
```json
{
  "timestamp": "2025-08-03T17:47:06.123Z",
  "level": "WARNING",
  "service": "MarketDataService",
  "operation": "get_enhanced_context",
  "message": "Enhanced context component failed, continuing with fallback",
  "context": {
    "symbol": "LINKUSDT",
    "failed_component": "pattern_identification",
    "error_details": {
      "error_type": "IndexError",
      "error_message": "list index out of range",
      "error_location": "_identify_patterns line 802"
    },
    "recovery_action": "continue_with_remaining_components",
    "remaining_components": ["recent_trend", "sr_tests", "volume_analysis"],
    "completed_components": ["key_candle_selection"],
    "fallback_data": {
      "patterns": "Pattern analysis failed (IndexError)",
      "pattern_count": 0
    }
  },
  "flow": {
    "stage": "component_recovery",
    "previous_stage": "pattern_analysis",
    "next_stage": "sr_analysis",
    "flow_id": "flow_enh_20250803174706"
  },
  "tags": ["error_recovery", "component_failure", "graceful_degradation"],
  "trace_id": "trd_003_2025080317470612"
}
```

### Complete Analysis Failure - ERROR level
```json
{
  "timestamp": "2025-08-03T17:47:06.456Z",
  "level": "ERROR",
  "service": "MarketDataService",
  "operation": "get_enhanced_context",
  "message": "Enhanced analysis completely failed, returning basic context",
  "context": {
    "symbol": "SHIBUSDT",
    "failure_cascade": {
      "initial_failure": "key_candle_selection",
      "subsequent_failures": ["pattern_analysis", "sr_tests", "volume_analysis"],
      "root_cause": "Empty daily_candles DataFrame"
    },
    "error_chain": [
      {
        "component": "key_candle_selection",
        "error": "ValueError: daily_candles is empty",
        "timestamp": "2025-08-03T17:47:06.200Z"
      },
      {
        "component": "pattern_analysis",
        "error": "AttributeError: 'NoneType' object has no attribute '__len__'",
        "timestamp": "2025-08-03T17:47:06.345Z"
      }
    ],
    "recovery_strategy": "fallback_to_basic_context",
    "basic_context_status": "available",
    "user_impact": "enhanced_features_unavailable"
  },
  "flow": {
    "stage": "complete_failure_recovery",
    "previous_stage": "component_recovery",
    "next_stage": "basic_context_fallback",
    "flow_id": "flow_enh_20250803174706"
  },
  "tags": ["complete_failure", "error_cascade", "basic_fallback"],
  "trace_id": "trd_003_2025080317470645"
}
```

## 11. Edge Case Scenarios

### Empty DataFrame Handling - WARNING level
```json
{
  "timestamp": "2025-08-03T17:47:07.000Z",
  "level": "WARNING",
  "service": "MarketDataService",
  "operation": "to_llm_context_basic",
  "message": "Empty DataFrame detected, returning minimal context",
  "context": {
    "symbol": "NEWUSDT",
    "empty_dataframes": {
      "h1_candles": {"length": 0, "columns": ["timestamp", "open", "high", "low", "close", "volume"]},
      "h4_candles": {"length": 12, "status": "available"},
      "daily_candles": {"length": 5, "status": "insufficient"}
    },
    "fallback_indicators": {
      "rsi_14": "50.0",
      "macd_signal": "neutral",
      "ma_20": "N/A",
      "ma_50": "N/A",
      "ma_trend": "sideways"
    },
    "context_limitations": {
      "no_24h_change": "insufficient h1 data",
      "no_volume_24h": "insufficient h1 data",
      "no_current_price": "empty h1_candles"
    }
  },
  "flow": {
    "stage": "empty_data_handling",
    "previous_stage": "context_generation",
    "next_stage": "minimal_context_return",
    "flow_id": "flow_new_20250803174707"
  },
  "tags": ["empty_dataframe", "edge_case", "minimal_context"],
  "trace_id": "trd_004_2025080317470700"
}
```

### Insufficient Data Periods - WARNING level
```json
{
  "timestamp": "2025-08-03T17:47:07.234Z",
  "level": "WARNING",
  "service": "MarketDataService",
  "operation": "_calculate_rsi",
  "message": "Insufficient data for RSI calculation, using fallback",
  "context": {
    "symbol": "TESTUSDT",
    "required_periods": 14,
    "available_periods": 8,
    "data_points": {
      "h1_candles_length": 8,
      "close_prices": ["100.00", "101.50", "99.75", "102.25", "100.80", "103.10", "101.90", "102.45"]
    },
    "fallback_strategy": {
      "action": "return_neutral_rsi",
      "fallback_value": "50.0",
      "reason": "insufficient_data_for_reliable_calculation"
    },
    "calculation_requirements": {
      "minimum_periods": 15,
      "recommended_periods": 50
    }
  },
  "flow": {
    "stage": "insufficient_data_handling",
    "previous_stage": "technical_indicators",
    "next_stage": "fallback_calculation",
    "flow_id": "flow_test_20250803174707"
  },
  "tags": ["insufficient_data", "rsi_fallback", "edge_case"],
  "trace_id": "trd_005_2025080317470723"
}
```

## 12. Performance & Data Quality Metrics

### Processing Performance - INFO level
```json
{
  "timestamp": "2025-08-03T17:47:08.000Z",
  "level": "INFO",
  "service": "MarketDataService",
  "operation": "get_market_data",
  "message": "Processing performance metrics",
  "context": {
    "symbol": "BTCUSDT",
    "performance_metrics": {
      "total_processing_time_ms": 4123,
      "component_breakdown_ms": {
        "api_calls": 319,
        "data_validation": 45,
        "technical_indicators": 234,
        "correlation_calculation": 156,
        "volume_analysis": 67,
        "context_generation": 89
      },
      "memory_usage": {
        "dataframe_sizes_mb": {
          "daily_candles": 0.12,
          "h4_candles": 0.05,
          "h1_candles": 0.03
        },
        "peak_memory_mb": 2.8,
        "memory_efficiency": "98.2%"
      },
      "api_efficiency": {
        "requests_made": 3,
        "total_response_time_ms": 319,
        "average_response_time_ms": 106,
        "success_rate": "100%"
      }
    },
    "bottlenecks_identified": [
      {
        "component": "technical_indicators",
        "time_ms": 234,
        "percentage": "56.7%",
        "optimization_potential": "medium"
      }
    ]
  },
  "flow": {
    "stage": "performance_analysis",
    "previous_stage": "completion",
    "flow_completion": true,
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["performance_metrics", "bottleneck_analysis", "memory_usage"],
  "trace_id": "trd_001_2025080317470800"
}
```

### Data Quality Issues - WARNING level
```json
{
  "timestamp": "2025-08-03T17:47:08.345Z",
  "level": "WARNING",
  "service": "MarketDataService",
  "operation": "_get_klines",
  "message": "Data quality anomalies detected",
  "context": {
    "symbol": "VOLATILEUSDT",
    "data_quality_issues": {
      "price_anomalies": {
        "extreme_gaps": [
          {
            "timestamp": "2025-08-02T14:00:00Z",
            "prev_close": "1.2345",
            "current_open": "2.4567",
            "gap_percentage": "99.1%",
            "anomaly_type": "extreme_gap_up"
          }
        ],
        "zero_volume_periods": [
          {
            "timestamp": "2025-08-01T03:00:00Z",
            "volume": "0.00000000",
            "duration_hours": 2
          }
        ]
      },
      "ohlc_inconsistencies": {
        "count": 3,
        "issues": [
          {
            "timestamp": "2025-07-30T09:00:00Z",
            "issue": "high_equals_low",
            "values": {"high": "1.2345", "low": "1.2345", "open": "1.2345", "close": "1.2345"}
          }
        ]
      },
      "data_integrity": {
        "missing_timestamps": 0,
        "duplicate_timestamps": 1,
        "out_of_sequence": 0
      }
    },
    "impact_assessment": {
      "technical_indicators": "may_be_affected",
      "pattern_analysis": "reliability_reduced",
      "recommended_action": "use_with_caution"
    }
  },
  "flow": {
    "stage": "data_quality_check",
    "previous_stage": "data_validation",
    "next_stage": "technical_indicators_with_warnings",
    "flow_id": "flow_volatile_20250803174708"
  },
  "tags": ["data_quality", "price_anomalies", "reliability_warning"],
  "trace_id": "trd_006_2025080317470834"
}
```

Эта финальная logging архитектура теперь обеспечивает **полную диагностическую карту** для ИИ, включая все критически важные элементы:

- **Validation input data и errors** - для диагностики проблем валидации
- **7-algorithm breakdown** - детальный trace каждого алгоритма 
- **Error recovery chain** - пошаговое восстановление после ошибок
- **Edge case scenarios** - обработка пустых данных и недостаточных периодов
- **Performance metrics** - узкие места и оптимизация возможности
- **Data quality issues** - аномалии данных и их влияние

Архитектура готова к немедленному внедрению в MarketDataService код.
    "flow_id": "flow_link_20250803175030"
  },
  "tags": ["correlation_error", "fallback_used", "graceful_degradation"],
  "trace_id": "trd_005_2025080317503056"
}
```

## 6. Performance Monitoring

### Method Performance Tracking
```json
{
  "timestamp": "2025-08-03T17:52:00.000Z",
  "level": "INFO",
  "service": "MarketDataService",
  "operation": "performance_summary",
  "message": "Service performance metrics",
  "context": {
    "time_window": "last_1_hour",
    "method_metrics": {
      "get_market_data_calls": 45,
      "get_enhanced_context_calls": 12,
      "avg_processing_time_ms": 234,
      "api_success_rate": "98.9%"
    },
    "resource_usage": {
      "cache_dir_size_mb": 12.5,
      "memory_usage_mb": 67.8
    }
  },
  "tags": ["performance_monitoring", "service_health"],
  "trace_id": "trd_006_2025080317520000"
}
```

## 7. Structured Context Tags для поиска

### Основные категории тегов:

**Методы MarketDataService:**
- `get_market_data`, `get_enhanced_context`, `_get_klines`
- `_calculate_rsi`, `_calculate_macd_signal`, `_calculate_ma`
- `_calculate_btc_correlation`, `_analyze_volume_profile`

**Операционные теги:**
- `symbol_validation`, `data_collection`, `technical_analysis`
- `pattern_identification`, `candlestick_analysis`, `volume_analysis`

**Состояние системы:**
- `success`, `error`, `warning`, `validation_error`
- `fallback_used`, `graceful_degradation`

**Финансовые операции:**
- `financial_precision`, `decimal_arithmetic`, `market_data_set`
- `rsi_calculation`, `macd_calculation`, `correlation_analysis`

**Performance:**
- `processing_time`, `api_success_rate`, "service_health`

**Flow Navigation:**
- `flow_start`, `flow_complete`, `flow_termination`
- Stage progression: `initiation` → `symbol_validation` → `data_collection` → `raw_data_processing` → `data_validation` → `technical_indicators` → `completion`

Эта logging архитектура обеспечивает полную трассировку цепочки выполнения с целостными trace_id, временными последовательностями и flow_id для навигации по сложным процессам.