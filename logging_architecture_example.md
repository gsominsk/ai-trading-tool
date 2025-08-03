# Structured Logging Architecture Example for MarketDataService

Этот документ демонстрирует комплексную архитектуру структурированного логирования для MarketDataService в AI Trading System, включая различные уровни логирования, трейсинг data flow, детализацию расчетной логики и performance метрики.

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
    "last_successful_call": "2025-08-03T16:30:00.000Z",
    "trading_halt_triggered": true
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
  "operation": "calculate_rsi",
  "message": "RSI calculation failed due to insufficient data",
  "context": {
    "symbol": "ETHUSDT",
    "required_periods": 14,
    "available_periods": 8,
    "data_gap_detected": true,
    "fallback_strategy": "use_cached_value"
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
  "operation": "validate_market_data",
  "message": "Price anomaly detected in market data",
  "context": {
    "symbol": "MATICUSDT",
    "current_price": "1.2500",
    "price_change_1h": "15.67%",
    "anomaly_threshold": "10.0%",
    "data_source": "binance_api",
    "validation_action": "flagged_for_review"
  },
  "tags": ["price_anomaly", "data_validation", "requires_review"],
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
    "candlesticks_analyzed": 180,
    "key_patterns_found": 4,
    "patterns": ["Shooting Star", "Hammer", "Strong Bear", "Doji"],
    "sr_tests": {"resistance": 1, "support": 1},
    "token_count": 387
  },
  "tags": ["enhanced_context", "pattern_analysis", "performance"],
  "trace_id": "trd_001_2025080317454523"
}
```

### DEBUG - Детальная отладочная информация
```json
{
  "timestamp": "2025-08-03T17:46:00.567Z",
  "level": "DEBUG",
  "service": "MarketDataService", 
  "operation": "select_key_candles",
  "message": "Smart candlestick selection algorithm executed",
  "context": {
    "symbol": "BTCUSDT",
    "algorithm_steps": {
      "recent_5": 5,
      "extremes": 4,
      "high_volume": 8,
      "big_moves": 3,
      "patterns": 6,
      "sr_tests": 2,
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
  "operation": "identify_patterns",
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
      "range_size": "1100.00",
      "body_ratio": 0.136,
      "upper_shadow": "550.00",
      "lower_shadow": "400.00",
      "upper_shadow_ratio": 0.500,
      "lower_shadow_ratio": 0.364
    },
    "pattern_result": "No significant pattern"
  },
  "tags": ["pattern_trace", "calculation_details", "candle_analysis"],
  "trace_id": "trd_001_2025080317461589"
}
```

## 2. Data Flow Tracing между компонентами

### Начало цепочки обработки данных
```json
{
  "timestamp": "2025-08-03T17:47:00.000Z",
  "level": "INFO",
  "service": "MarketDataService",
  "operation": "get_market_data",
  "message": "Market data request initiated",
  "context": {
    "symbol": "BTCUSDT",
    "request_type": "full_analysis",
    "requested_by": "ClaudeProvider",
    "request_id": "req_12345"
  },
  "flow": {
    "stage": "initiation",
    "next_stage": "data_collection",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["flow_start", "llm_request"],
  "trace_id": "trd_001_2025080317470000"
}
```

### Этап сбора данных с Binance API
```json
{
  "timestamp": "2025-08-03T17:47:01.234Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "fetch_binance_data",
  "message": "Binance API data retrieved",
  "context": {
    "symbol": "BTCUSDT",
    "api_calls": {
      "daily_candles_6m": "SUCCESS",
      "4h_candles_2w": "SUCCESS", 
      "1h_candles_48h": "SUCCESS"
    },
    "response_times_ms": {
      "daily": 145,
      "4h": 98,
      "1h": 76
    },
    "total_candles_received": 360
  },
  "flow": {
    "stage": "data_collection",
    "previous_stage": "initiation",
    "next_stage": "technical_analysis",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["api_success", "data_collection"],
  "trace_id": "trd_001_2025080317470123"
}
```

### Этап технического анализа
```json
{
  "timestamp": "2025-08-03T17:47:02.567Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "calculate_technical_indicators",
  "message": "Technical indicators calculated",
  "context": {
    "symbol": "BTCUSDT",
    "indicators": {
      "rsi_14": "35.77",
      "macd_signal": "bearish",
      "ma_20": "113450.25",
      "ma_50": "115200.75"
    },
    "calculation_time_ms": 23
  },
  "flow": {
    "stage": "technical_analysis",
    "previous_stage": "data_collection",
    "next_stage": "enhanced_analysis",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["technical_indicators", "calculation_complete"],
  "trace_id": "trd_001_2025080317470256"
}
```

### Этап enhanced анализа
```json
{
  "timestamp": "2025-08-03T17:47:03.890Z",
  "level": "INFO",
  "service": "MarketDataService",
  "operation": "generate_enhanced_context",
  "message": "Enhanced context generation completed",
  "context": {
    "symbol": "BTCUSDT",
    "analysis_results": {
      "recent_trend": "Downward bias",
      "key_patterns": ["Shooting Star", "Hammer", "Strong Bear", "Doji"],
      "sr_interactions": {"resistance_tests": 1, "support_tests": 1},
      "volume_signal": "Weak bearish"
    },
    "processing_time_ms": 189
  },
  "flow": {
    "stage": "enhanced_analysis",
    "previous_stage": "technical_analysis", 
    "next_stage": "response_formatting",
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["enhanced_analysis", "pattern_recognition"],
  "trace_id": "trd_001_2025080317470389"
}
```

### Завершение цепочки - отправка данных LLM
```json
{
  "timestamp": "2025-08-03T17:47:05.123Z",
  "level": "INFO",
  "service": "MarketDataService",
  "operation": "deliver_market_data",
  "message": "Market data delivered to LLM provider",
  "context": {
    "symbol": "BTCUSDT",
    "delivery_target": "ClaudeProvider",
    "data_format": "enhanced_context",
    "total_tokens": 387,
    "total_processing_time_ms": 5123
  },
  "flow": {
    "stage": "response_formatting",
    "previous_stage": "enhanced_analysis",
    "flow_completion": true,
    "flow_id": "flow_btc_20250803174700"
  },
  "tags": ["flow_complete", "llm_delivery"],
  "trace_id": "trd_001_2025080317470512"
}
```

## 3. Детализация расчетной логики

### RSI Calculation с полной детализацией
```json
{
  "timestamp": "2025-08-03T17:48:00.000Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "calculate_rsi",
  "message": "RSI calculation performed",
  "context": {
    "symbol": "BTCUSDT",
    "rsi_period": 14,
    "calculation_data": {
      "gains_avg": "234.567890",
      "losses_avg": "432.109876",
      "relative_strength": "0.542857",
      "rsi_value": "35.17"
    },
    "data_quality": {
      "periods_available": 14,
      "periods_required": 14,
      "data_completeness": "100%"
    },
    "precision": "decimal_8_places",
    "calculation_time_ms": 8
  },
  "tags": ["rsi_calculation", "technical_analysis", "financial_precision"],
  "trace_id": "trd_001_2025080317480000"
}
```

### MACD Calculation с компонентами
```json
{
  "timestamp": "2025-08-03T17:48:15.234Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "calculate_macd",
  "message": "MACD components calculated",
  "context": {
    "symbol": "BTCUSDT",
    "macd_components": {
      "ema_12": "112756.45000000",
      "ema_26": "113123.78000000",
      "macd_line": "-367.33000000",
      "signal_line": "-234.56000000",
      "histogram": "-132.77000000"
    },
    "signal_interpretation": {
      "trend": "bearish",
      "strength": "moderate",
      "divergence": "none"
    },
    "calculation_time_ms": 12
  },
  "tags": ["macd_calculation", "trend_analysis", "signal_generation"],
  "trace_id": "trd_001_2025080317481523"
}
```

### Correlation Analysis с BTC
```json
{
  "timestamp": "2025-08-03T17:48:30.567Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "calculate_btc_correlation",
  "message": "BTC correlation analysis completed",
  "context": {
    "symbol": "ETHUSDT",
    "correlation_data": {
      "btc_correlation_7d": "0.89234567",
      "btc_correlation_30d": "0.76543210",
      "correlation_strength": "strong_positive",
      "price_movement_sync": "85.3%"
    },
    "calculation_method": "pearson_correlation",
    "sample_size": {
      "7d_points": 168,
      "30d_points": 720
    },
    "calculation_time_ms": 18
  },
  "tags": ["correlation_analysis", "btc_relationship", "market_structure"],
  "trace_id": "trd_001_2025080317483056"
}
```

## 4. Performance Metrics Logging

### API Performance Monitoring
```json
{
  "timestamp": "2025-08-03T17:49:00.000Z",
  "level": "INFO",
  "service": "MarketDataService",
  "operation": "performance_metrics",
  "message": "API performance summary",
  "context": {
    "time_window": "last_1_hour",
    "binance_api_metrics": {
      "total_requests": 247,
      "successful_requests": 245,
      "failed_requests": 2,
      "success_rate": "99.19%",
      "average_response_time_ms": 156,
      "p95_response_time_ms": 284,
      "p99_response_time_ms": 456
    },
    "rate_limiting": {
      "current_weight": 850,
      "weight_limit": 1200,
      "utilization": "70.83%"
    }
  },
  "tags": ["performance_monitoring", "api_health", "sla_tracking"],
  "trace_id": "trd_001_2025080317490000"
}
```

### Memory и Processing Performance
```json
{
  "timestamp": "2025-08-03T17:49:15.234Z",
  "level": "DEBUG",
  "service": "MarketDataService",
  "operation": "system_performance",
  "message": "System resource utilization",
  "context": {
    "memory_usage": {
      "current_mb": 245.67,
      "peak_mb": 289.34,
      "available_mb": 1024.00
    },
    "processing_metrics": {
      "concurrent_operations": 3,
      "average_processing_time_ms": 234,
      "operations_per_minute": 87,
      "cpu_utilization": "23.4%"
    },
    "cache_performance": {
      "hit_rate": "89.5%",
      "cache_size_mb": 45.2,
      "evictions_per_hour": 12
    }
  },
  "tags": ["system_performance", "resource_monitoring", "optimization"],
  "trace_id": "trd_001_2025080317491523"
}
```

### Business Logic Performance
```json
{
  "timestamp": "2025-08-03T17:49:30.567Z",
  "level": "INFO",
  "service": "MarketDataService",
  "operation": "business_metrics",
  "message": "Business logic performance summary",
  "context": {
    "symbol_processing": {
      "symbols_processed": 15,
      "enhanced_context_generations": 8,
      "basic_context_generations": 7,
      "pattern_recognitions": 45,
      "sr_level_calculations": 30
    },
    "accuracy_metrics": {
      "data_validation_pass_rate": "98.7%",
      "pattern_confidence_avg": "0.847",
      "calculation_precision": "decimal_8_places"
    },
    "efficiency_metrics": {
      "token_optimization": "91.7%",
      "processing_speed_improvement": "34.2%"
    }
  },
  "tags": ["business_performance", "accuracy_tracking", "efficiency"],
  "trace_id": "trd_001_2025080317493056"
}
```

## 5. Error Handling Scenarios

### Network Timeout Handling
```json
{
  "timestamp": "2025-08-03T17:50:00.000Z",
  "level": "WARNING",
  "service": "MarketDataService",
  "operation": "handle_network_timeout",
  "message": "Network timeout detected, applying fallback strategy",
  "context": {
    "symbol": "ADAUSDT",
    "error_details": {
      "timeout_duration_ms": 5000,
      "retry_attempt": 2,
      "max_retries": 3
    },
    "fallback_strategy": {
      "action": "use_cached_data",
      "cache_age_minutes": 3,
      "data_freshness": "acceptable"
    },
    "impact_assessment": {
      "trading_decision_delayed": false,
      "data_quality_degraded": "minimal"
    }
  },
  "tags": ["network_timeout", "fallback_strategy", "resilience"],
  "trace_id": "trd_001_2025080317500000"
}
```

### Data Validation Error
```json
{
  "timestamp": "2025-08-03T17:50:15.234Z",
  "level": "ERROR",
  "service": "MarketDataService",
  "operation": "validate_market_data",
  "message": "Critical data validation failure",
  "context": {
    "symbol": "DOGEUSDT",
    "validation_errors": [
      {
        "field": "ohlc_relationship",
        "error": "High price lower than Open price",
        "values": {"open": "0.12345", "high": "0.12300", "low": "0.12100", "close": "0.12234"}
      },
      {
        "field": "volume",
        "error": "Negative volume detected",
        "value": "-123.456"
      }
    ],
    "data_source": "binance_api",
    "error_handling": {
      "action": "reject_data",
      "fallback": "request_fresh_data",
      "alert_sent": true
    }
  },
  "tags": ["data_validation", "critical_error", "data_integrity"],
  "trace_id": "trd_001_2025080317501523"
}
```

### Rate Limiting Encountered
```json
{
  "timestamp": "2025-08-03T17:50:30.567Z",
  "level": "WARNING",
  "service": "MarketDataService",
  "operation": "handle_rate_limiting",
  "message": "Binance API rate limit approached",
  "context": {
    "current_weight": 1150,
    "weight_limit": 1200,
    "utilization": "95.83%",
    "rate_limiting_strategy": {
      "action": "delay_non_critical_requests",
      "delay_duration_ms": 2000,
      "priority_queue_activated": true
    },
    "request_queue": {
      "high_priority": 2,
      "normal_priority": 5,
      "delayed": 3
    }
  },
  "tags": ["rate_limiting", "request_management", "priority_queue"],
  "trace_id": "trd_001_2025080317503056"
}
```

### Calculation Precision Error
```json
{
  "timestamp": "2025-08-03T17:50:45.890Z",
  "level": "ERROR",
  "service": "MarketDataService",
  "operation": "decimal_precision_check",
  "message": "Decimal precision requirement violation detected",
  "context": {
    "symbol": "LINKUSDT",
    "precision_error": {
      "expected_type": "Decimal",
      "actual_type": "float",
      "field": "ma_20_calculation",
      "value": 23.456789012345
    },
    "financial_safety": {
      "trading_blocked": true,
      "precision_critical": true,
      "auto_correction_attempted": false
    },
    "remediation": {
      "action": "convert_to_decimal",
      "validation_required": true,
      "trading_resume_condition": "manual_approval"
    }
  },
  "tags": ["precision_error", "financial_safety", "trading_halt"],
  "trace_id": "trd_001_2025080317504589"
}
```

## 6. Structured Context Tags для поиска и анализа

### Основные категории тегов:

**Операционные теги:**
- `api_call`, `data_processing`, `calculation`, `validation`, `caching`
- `pattern_recognition`, `technical_analysis`, `enhanced_context`

**Состояние системы:**
- `success`, `warning`, `error`, `critical`, `performance`
- `fallback_used`, `cache_hit`, `cache_miss`

**Финансовые операции:**
- `financial_precision`, `decimal_arithmetic`, `price_calculation`
- `trading_decision`, `risk_assessment`

**Производительность:**
- `performance_tracking`, `optimization`, `resource_monitoring`
- `sla_compliance`, `efficiency_metrics`

**Troubleshooting:**
- `debug_trace`, `error_analysis`, `network_issue`
- `data_quality`, `system_health`

## 7. Integration с Monitoring Systems

### Prometheus Metrics Format
```json
{
  "timestamp": "2025-08-03T17:51:00.000Z",
  "level": "INFO",
  "service": "MarketDataService",
  "operation": "export_metrics",
  "message": "Metrics exported to monitoring system",
  "context": {
    "prometheus_metrics": {
      "market_data_requests_total": 247,
      "market_data_request_duration_seconds": 0.156,
      "binance_api_errors_total": 2,
      "rsi_calculations_total": 45,
      "enhanced_context_generations_total": 8
    },
    "grafana_dashboard": "ai_trading_system",
    "alert_rules_active": 12
  },
  "tags": ["metrics_export", "monitoring_integration", "observability"],
  "trace_id": "trd_001_2025080317510000"
}
```

Эта архитектура логирования обеспечивает:
- **Полную трассируемость** операций от запроса до ответа
- **Финансовую безопасность** через детальное логирование всех расчетов
- **Оперативную диагностику** проблем через структурированные теги
- **Мониторинг производительности** для оптимизации системы
- **Соответствие требованиям** регулирования финансовых систем