"""
AI-Optimized Logger Configuration
Central configuration for MarketDataService logging system
"""

import logging
import sys
import threading
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
                         console_output: bool = True):
        """
        Configure global logging for AI optimization.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for log output
            console_output: Whether to output to console
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
        
        # Add file handler if requested
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(numeric_level)
            root_logger.addHandler(file_handler)
        
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
                        console_output: bool = True):
    """
    Configure AI-optimized logging system.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output  
        console_output: Whether to output to console
    """
    _logger_config.configure_logging(log_level, log_file, console_output)


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
                           trace_id: Optional[str] = None):
        """Log start of major operation with flow context."""
        self.logger.info(
            f"{operation} initiated",
            operation=operation,
            context=context or {"symbol": symbol},
            tags=["flow_start", operation.lower().replace("_", "")],
            flow=get_flow_summary(),
            trace_id=trace_id
        )
    
    def log_operation_complete(self, operation: str, 
                              processing_time_ms: Optional[int] = None,
                              context: Optional[Dict[str, Any]] = None,
                              trace_id: Optional[str] = None):
        """Log successful completion of operation."""
        ctx = context or {}
        if processing_time_ms:
            ctx["processing_time_ms"] = processing_time_ms
            
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