"""
AI-Optimized Logger Configuration
Central configuration for MarketDataService logging system
"""

import logging
import logging.handlers
import sys
import threading
import os
from typing import Dict, Any, Optional
from .json_formatter import get_logger, StructuredLogger
from .flow_context import flow_operation, get_flow_summary
from .trace_generator import get_trace_id, get_flow_id


class LoggerConfig:
    """
    Central configuration for AI-optimized logging system.
    
    Manages logger setup, level configuration, and output destinations.
    Designed for complete process visibility and AI searchability.
    """
    
    def __init__(self):
        self._configured = False
        self._loggers: Dict[str, StructuredLogger] = {}
        self._loggers_lock = threading.Lock()
        self._log_level = logging.DEBUG
    
    def configure_logging(self,
                         log_level: str = "DEBUG",
                         log_file: Optional[str] = None,
                         console_output: bool = True,
                         max_bytes: int = 10*1024*1024,  # 10MB
                         backup_count: int = 5):
        """
        Configure global logging for AI optimization with file rotation.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for log output with rotation
            console_output: Whether to output to console
            max_bytes: Maximum file size before rotation (default: 10MB)
            backup_count: Number of backup files to keep (default: 5)
        """
        if self._configured:
            return
        
        # Set logging level
        numeric_level = getattr(logging, log_level.upper(), logging.DEBUG)
        self._log_level = numeric_level
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Add console handler if requested (JSON logs go to stderr for AI searchability)
        if console_output:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(numeric_level)
            root_logger.addHandler(console_handler)
        
        # Add rotating file handler if requested
        if log_file:
            try:
                # Ensure log directory exists
                log_dir = os.path.dirname(log_file)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)
                
                # Use RotatingFileHandler for automatic log rotation
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                file_handler.setLevel(numeric_level)
                
                # Apply JSON formatter to file handler for structured logs
                from .json_formatter import AIOptimizedJSONFormatter
                json_formatter = AIOptimizedJSONFormatter("MarketDataService")
                file_handler.setFormatter(json_formatter)
                
                root_logger.addHandler(file_handler)
            except Exception as e:
                # Логи сломались - останавливаем сервис
                print(f"CRITICAL: Failed to configure file logging - shutting down service: {e}", file=sys.stderr)
                # Graceful exit вместо os._exit(1)
                raise SystemExit(1)
        
        self._configured = True
    
    def get_logger(self, name: str, service_name: str = "MarketDataService") -> StructuredLogger:
        """
        Get or create a structured logger for AI-optimized logging.
        
        Args:
            name: Logger name (typically module name)
            service_name: Service name for log identification
            
        Returns:
            StructuredLogger instance configured for AI analysis
        """
        with self._loggers_lock:
            # Use combination of name and service_name as cache key to support multiple services
            cache_key = f"{name}:{service_name}"
            if cache_key not in self._loggers:
                logger = get_logger(name, service_name)
                # Ensure logger respects the configured log level
                if self._configured:
                    logger.logger.setLevel(self._log_level)
                self._loggers[cache_key] = logger
            return self._loggers[cache_key]
    
    def is_configured(self) -> bool:
        """Check if logging system is configured."""
        return self._configured
    
    def reset(self):
        """Reset logger configuration for testing."""
        with self._loggers_lock:
            self._configured = False
            self._loggers.clear()
            
            # Clear all handlers from root logger
            root_logger = logging.getLogger()
            root_logger.handlers.clear()
            root_logger.setLevel(logging.WARNING)  # Reset to default


# Global logger configuration instance
_logger_config = LoggerConfig()


def configure_ai_logging(log_level: str = "DEBUG",
                        log_file: Optional[str] = None,
                        console_output: bool = True,
                        max_bytes: int = 10*1024*1024,
                        backup_count: int = 5,
                        filter_http_noise: bool = True):
    """
    Configure AI-optimized logging system with file rotation and HTTP noise filtering.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output with rotation
        console_output: Whether to output to console
        max_bytes: Maximum file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
        filter_http_noise: Filter out verbose HTTP logs from urllib3/requests (default: True)
    """
    _logger_config.configure_logging(log_level, log_file, console_output, max_bytes, backup_count)
    
    # Filter HTTP noise for cleaner AI logs
    if filter_http_noise:
        _configure_http_logging_filters()


def _configure_http_logging_filters():
    """
    Configure HTTP logging filters to reduce noise in AI logs.
    
    Filters out verbose HTTP connection logs from urllib3 and requests
    while preserving ERROR level messages for debugging network issues.
    """
    # Filter urllib3 connection pool logs (the main source of "unknown" operations)
    urllib3_logger = logging.getLogger('urllib3.connectionpool')
    urllib3_logger.setLevel(logging.WARNING)  # Only show warnings and errors
    
    # Filter requests logs
    requests_logger = logging.getLogger('requests')
    requests_logger.setLevel(logging.WARNING)  # Only show warnings and errors
    
    # Filter general urllib3 logs
    urllib3_base_logger = logging.getLogger('urllib3')
    urllib3_base_logger.setLevel(logging.WARNING)  # Only show warnings and errors
    
    # Optional: Add more specific filters if needed
    # These loggers are common sources of HTTP noise
    http_loggers = [
        'urllib3.util.retry',
        'urllib3.util.connection',
        'requests.packages.urllib3.connectionpool'
    ]
    
    for logger_name in http_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.ERROR)  # Only critical HTTP errors


def get_ai_logger(name: str, service_name: str = "MarketDataService") -> StructuredLogger:
    """
    Get AI-optimized structured logger.
    
    Args:
        name: Logger name (typically __name__)
        service_name: Service name for identification
        
    Returns:
        StructuredLogger configured for AI analysis
    """
    return _logger_config.get_logger(name, service_name)


class MarketDataLogger:
    """
    Specialized logger for MarketDataService operations.
    
    Provides domain-specific logging methods with semantic tags
    and context preservation for AI analysis.
    """
    
    def __init__(self, module_name: str):
        self.logger = get_ai_logger(module_name)
        self.module_name = module_name
    
    def log_operation_start(self, operation: str, symbol: str = "",
                           context: Optional[Dict[str, Any]] = None,
                           trace_id: Optional[str] = None,
                           parent_trace_id: Optional[str] = None):
        """Log start of major operation with flow context and hierarchical tracing."""
        ctx = context or {"symbol": symbol}
        
        # Auto-generate trace_id using get_flow_id if not provided and symbol is available
        if trace_id is None and symbol:
            from .trace_generator import get_flow_id
            trace_id = get_flow_id(symbol, operation)
        
        # Add parent_trace_id to context if provided for hierarchical tracing
        if parent_trace_id:
            ctx["parent_trace_id"] = parent_trace_id
            
        self.logger.info(
            f"{operation} initiated",
            operation=operation,
            context=ctx,
            tags=["flow_start", operation.lower().replace("_", "")],
            flow=get_flow_summary(),
            trace_id=trace_id
        )
    
    def log_operation_complete(self, operation: str,
                              processing_time_ms: Optional[int] = None,
                              context: Optional[Dict[str, Any]] = None,
                              trace_id: Optional[str] = None,
                              parent_trace_id: Optional[str] = None):
        """Log successful completion of operation with hierarchical tracing."""
        ctx = context or {}
        if processing_time_ms:
            ctx["processing_time_ms"] = processing_time_ms
        
        # Auto-generate trace_id using get_flow_id if not provided and symbol is available in context
        if trace_id is None and ctx.get("symbol"):
            from .trace_generator import get_flow_id
            trace_id = get_flow_id(ctx["symbol"], operation)
        
        # Add parent_trace_id to context if provided for hierarchical tracing
        if parent_trace_id:
            ctx["parent_trace_id"] = parent_trace_id
            
        self.logger.info(
            f"{operation} completed successfully",
            operation=operation,
            context=ctx,
            tags=["flow_complete", operation.lower().replace("_", ""), "success"],
            flow=get_flow_summary(),
            trace_id=trace_id
        )
    
    def log_api_call(self, symbol: str, interval: str, limit: int,
                     response_time_ms: Optional[int] = None,
                     status_code: Optional[int] = None,
                     trace_id: Optional[str] = None):
        """Log API call with performance metrics."""
        context = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        if response_time_ms:
            context["response_time_ms"] = response_time_ms
        if status_code:
            context["status_code"] = status_code
            
        self.logger.debug(
            "Binance API call executed",
            operation="_get_klines",
            context=context,
            tags=["api_call", "binance", "data_collection"],
            flow=get_flow_summary(),
            trace_id=trace_id
        )
    
    def log_calculation(self, indicator: str, symbol: str,
                       input_data: Optional[Dict[str, Any]] = None,
                       result: Optional[Any] = None,
                       calculation_time_ms: Optional[int] = None,
                       trace_id: Optional[str] = None):
        """Log technical indicator calculation."""
        context = {"symbol": symbol, "indicator": indicator}
        if input_data:
            context["input_data"] = input_data
        if result is not None:
            context["result"] = str(result)
        if calculation_time_ms:
            context["calculation_time_ms"] = calculation_time_ms
            
        self.logger.debug(
            f"{indicator} calculation completed",
            operation=f"_calculate_{indicator.lower()}",
            context=context,
            tags=["calculation", indicator.lower(), "technical_analysis"],
            flow=get_flow_summary(),
            trace_id=trace_id
        )
    
    def log_validation_error(self, field: str, value: Any, 
                            expected: str, error_msg: str,
                            trace_id: Optional[str] = None):
        """Log validation error with detailed context."""
        context = {
            "failed_field": field,
            "failed_value": str(value),
            "expected_format": expected,
            "validation_error": error_msg
        }
        
        self.logger.error(
            "Data validation failed",
            operation="validation",
            context=context,
            tags=["validation_error", "data_integrity", field.lower()],
            flow=get_flow_summary(),
            trace_id=trace_id
        )
    
    def log_fallback_usage(self, operation: str, reason: str,
                          fallback_value: Any, trace_id: Optional[str] = None):
        """Log fallback strategy usage."""
        context = {
            "operation": operation,
            "fallback_reason": reason,
            "fallback_value": str(fallback_value)
        }
        
        self.logger.warning(
            f"Fallback strategy used in {operation}",
            operation=operation,
            context=context,
            tags=["fallback_used", "graceful_degradation", operation.lower()],
            flow=get_flow_summary(),
            trace_id=trace_id
        )
    
    def log_raw_data(self, data_type: str, data_sample: Any,
                     data_stats: Optional[Dict[str, Any]] = None,
                     trace_id: Optional[str] = None):
        """Log raw data for AI analysis (TRACE level)."""
        context = {
            "data_type": data_type,
            "data_sample": data_sample
        }
        if data_stats:
            context.update(data_stats)
            
        # Note: Using debug instead of trace since Python logging doesn't have TRACE
        self.logger.debug(
            f"Raw {data_type} data captured",
            operation="data_capture",
            context=context,
            tags=["raw_data", data_type.lower(), "trace_level"],
            flow=get_flow_summary(),
            trace_id=trace_id
        )


def reset_logging_state():
    """Reset global logging state for testing."""
    _logger_config.reset()