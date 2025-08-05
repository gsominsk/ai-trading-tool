"""
MarketDataService Logging Integration Module

Provides AI-optimized logging integration for MarketDataService operations.
Implements zero-defect integration following the "Истины" protocol.

Integration Components:
- Operation flow tracking with context
- Performance metrics collection  
- Error context preservation
- Raw API data logging
- Graceful degradation logging
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime

# AI-Optimized Logging System Integration
from src.logging_system import (
    configure_ai_logging,
    get_ai_logger,
    MarketDataLogger,
    flow_operation,
    advance_to_stage,
    set_flow_context,
    get_flow_context,
    get_flow_summary,
    complete_current_flow,
    terminate_current_flow,
    get_trace_id
)


class MarketDataServiceLogging:
    """
    Centralized logging integration for MarketDataService.
    
    Provides structured, AI-searchable logging with semantic tags,
    flow context tracking, and performance metrics collection.
    """
    
    def __init__(self, service_name: str = "MarketDataService", log_level: str = "INFO"):
        """Initialize logging integration with AI-optimized configuration."""
        # Configure AI-optimized logging system for trading operations
        import os
        os.makedirs("logs", exist_ok=True)
        
        # Store log level for filtering
        self.log_level = log_level.upper()
        
        configure_ai_logging(
            log_level=log_level,  # Use configurable log level
            log_file="logs/trading_operations.log",  # Main trading operations log
            console_output=True,  # Enable console output so JSON formatter applies to file handler
            max_bytes=50*1024*1024,  # 50MB per log file (trading operations can be verbose)
            backup_count=10  # Keep 10 backup files (500MB total history)
        )
        
        # Initialize specialized logger
        self.logger = MarketDataLogger("market_data_service")
        self.service_name = service_name
        
        # Performance tracking
        self._operation_start_times: Dict[str, float] = {}
        
    def _should_log(self, level: str) -> bool:
        """Check if message should be logged based on current log level."""
        log_levels = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
        current_level = log_levels.get(self.log_level, 20)  # Default to INFO
        message_level = log_levels.get(level.upper(), 20)
        return message_level >= current_level
    
    def _handle_logging_error(self, method_name: str, error: Exception,
                             operation: str = "", symbol: str = "", trace_id: str = None):
        """
        Handle logging errors gracefully to protect trading operations.
        
        This method ensures that logging failures never crash trading operations.
        It provides fallback error recording and silent degradation.
        """
        try:
            # Attempt to create a minimal error record in case the main logging system is broken
            error_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "logging_method": method_name,
                "error_type": type(error).__name__,
                "error_message": str(error)[:200],  # Limit message length
                "operation": operation,
                "symbol": symbol,
                "trace_id": trace_id or "unknown",
                "fallback_logging": True
            }
            
            # Try to write to a fallback error log file
            import os
            os.makedirs("logs", exist_ok=True)
            with open("logs/logging_errors.log", "a", encoding="utf-8") as f:
                import json
                f.write(json.dumps(error_record) + "\n")
                
        except Exception:
            # If even fallback logging fails, we silently continue
            # Trading operations must never be interrupted by logging issues
            pass
    
    def log_operation_start(self, operation: str, symbol: str = "",
                           context: Optional[Dict[str, Any]] = None,
                           trace_id: Optional[str] = None, level: str = "INFO", **kwargs):
        """Log start of major operation with flow context and timing."""
        try:
            # Check if we should log this level
            if not self._should_log(level):
                return  # Skip logging if level is below threshold
                
            # Record start time for performance metrics
            operation_key = f"{operation}_{trace_id or 'unknown'}"
            self._operation_start_times[operation_key] = time.time()
            
            # Initialize flow operation with context
            flow_operation_context = {
                "operation": operation,
                "symbol": symbol,
                "trace_id": trace_id or get_trace_id(),
                "start_time": datetime.utcnow().isoformat(),
                **(context or {}),
                **kwargs  # Include additional keyword arguments
            }
            
            # Set flow context for operation tracking (using correct API)
            set_flow_context("operation", operation)
            set_flow_context("symbol", symbol)
            set_flow_context("trace_id", trace_id or get_trace_id())
            set_flow_context("start_time", datetime.utcnow().isoformat())
            
            # Add any additional context
            if context:
                for key, value in context.items():
                    set_flow_context(key, value)
            
            # Add kwargs to flow context as well
            for key, value in kwargs.items():
                set_flow_context(key, value)
            
            # Log operation start with AI-optimized semantic tags
            self.logger.log_operation_start(
                operation=operation,
                symbol=symbol,
                context=flow_operation_context,
                trace_id=trace_id
            )
        except Exception as e:
            # Critical: Never let logging failures affect trading operations
            # Silently handle logging errors to protect business logic
            self._handle_logging_error("log_operation_start", e, operation, symbol, trace_id)
    
    def log_operation_success(self, operation: str, symbol: str = "",
                             context: Optional[Dict[str, Any]] = None,
                             trace_id: Optional[str] = None,
                             data_points: Optional[int] = None, level: str = "INFO", **kwargs):
        """Log successful operation completion with performance metrics."""
        try:
            # Check if we should log this level
            if not self._should_log(level):
                return  # Skip logging if level is below threshold
                
            operation_key = f"{operation}_{trace_id or 'unknown'}"
            
            # Calculate performance metrics
            start_time = self._operation_start_times.pop(operation_key, time.time())
            duration_ms = (time.time() - start_time) * 1000
            
            # Create success context
            success_context = {
                "operation": operation,
                "symbol": symbol,
                "trace_id": trace_id or get_trace_id(),
                "duration_ms": round(duration_ms, 2),
                "status": "success",
                "end_time": datetime.utcnow().isoformat(),
                **(context or {}),
                **kwargs  # Include additional keyword arguments
            }
            
            if data_points is not None:
                success_context["data_points"] = data_points
            
            # Advance flow to completion stage
            advance_to_stage("completion")
            
            # Log success with performance metrics
            self.logger.log_operation_complete(
                operation=operation,
                processing_time_ms=int(duration_ms),
                context=success_context,
                trace_id=trace_id
            )
            
            # Complete current flow
            complete_current_flow()
        except Exception as e:
            # Critical: Never let logging failures affect trading operations
            self._handle_logging_error("log_operation_success", e, operation, symbol, trace_id)
    
    def log_operation_error(self, operation: str, error: Exception,
                           symbol: str = "", context: Optional[Dict[str, Any]] = None,
                           trace_id: Optional[str] = None,
                           error_type: str = "unknown", level: str = "ERROR", **kwargs):
        """Log operation error with rich context preservation."""
        try:
            # Check if we should log this level
            if not self._should_log(level):
                return  # Skip logging if level is below threshold
                
            operation_key = f"{operation}_{trace_id or 'unknown'}"
            
            # Calculate duration to error
            start_time = self._operation_start_times.pop(operation_key, time.time())
            duration_ms = (time.time() - start_time) * 1000
            
            # Create comprehensive error context
            error_context = {
                "operation": operation,
                "symbol": symbol,
                "trace_id": trace_id or get_trace_id(),
                "error_type": error_type,
                "error_class": type(error).__name__,
                "error_message": str(error),
                "duration_ms": round(duration_ms, 2),
                "status": "error",
                "error_time": datetime.utcnow().isoformat(),
                **(context or {}),
                **kwargs  # Include additional keyword arguments
            }
            
            # Add error-specific context if available
            if hasattr(error, 'context'):
                error_context["error_context"] = getattr(error, 'context', {})
            
            if hasattr(error, 'operation'):
                error_context["failed_operation"] = getattr(error, 'operation', operation)
            
            # Advance flow to error stage
            advance_to_stage("error")
            
            # Log error with full context
            self.logger.log_validation_error(
                field=operation,
                value=str(error),
                expected="successful_operation",
                error_msg=f"{error_type}: {str(error)}",
                trace_id=trace_id
            )
            
            # Terminate current flow due to error
            terminate_current_flow(reason=f"Error: {error_type}")
        except Exception as logging_error:
            # Critical: Never let logging failures affect trading operations
            # This is especially important for error logging - if we can't log an error,
            # we absolutely cannot break the application flow
            self._handle_logging_error("log_operation_error", logging_error, operation, symbol, trace_id)
    
    def log_graceful_degradation(self, operation: str, failed_component: str = None,
                                fallback_used: str = None, trace_id: str = None,
                                context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log graceful degradation events for non-critical operation failures."""
        try:
            # Create degradation context
            degradation_context = {
                "operation": operation,
                "failed_component": failed_component,
                "fallback_used": fallback_used,
                "trace_id": trace_id or get_trace_id(),
                "degradation_time": datetime.utcnow().isoformat(),
                "severity": "warning",
                **(context or {}),
                **kwargs
            }
            
            # Advance flow to degradation stage
            advance_to_stage("degradation")
            
            # Log degradation event
            self.logger.log_fallback_usage(
                operation=operation,
                reason=f"Component '{failed_component}' failed",
                fallback_value=fallback_used or "default_fallback",
                trace_id=trace_id
            )
        except Exception as e:
            # Critical: Never let logging failures affect trading operations
            self._handle_logging_error("log_graceful_degradation", e, operation, "", trace_id)
    
    def log_performance_metrics(self, operation: str, metrics: Dict[str, Any],
                               symbol: str = "", trace_id: Optional[str] = None):
        """Log performance metrics for operation analysis."""
        try:
            # Create metrics context
            metrics_context = {
                "operation": operation,
                "symbol": symbol,
                "trace_id": trace_id or get_trace_id(),
                "metrics_time": datetime.utcnow().isoformat(),
                "metrics": metrics
            }
            
            # Log performance data using raw data logging
            self.logger.log_raw_data(
                data_type="performance_metrics",
                data_sample=metrics,
                data_stats={"operation": operation, "symbol": symbol},
                trace_id=trace_id
            )
        except Exception as e:
            # Critical: Never let logging failures affect trading operations
            self._handle_logging_error("log_performance_metrics", e, operation, symbol, trace_id)
    
    def log_api_response(self, operation: str, url: str, status_code: int,
                        response_size: int = None, symbol: str = "",
                        trace_id: Optional[str] = None,
                        raw_data: Optional[str] = None):
        """Log raw API response data for debugging and analysis."""
        try:
            # Create API response context
            api_context = {
                "operation": operation,
                "symbol": symbol,
                "trace_id": trace_id or get_trace_id(),
                "api_url": url,
                "status_code": status_code,
                "response_time": datetime.utcnow().isoformat()
            }
            
            if response_size is not None:
                api_context["response_size_bytes"] = response_size
            
            if raw_data is not None:
                # Truncate raw data if too large (keep first 1000 chars for debugging)
                api_context["raw_data_sample"] = raw_data[:1000] if len(raw_data) > 1000 else raw_data
                api_context["raw_data_full_length"] = len(raw_data)
            
            # Log API response using API call logging
            self.logger.log_api_call(
                symbol=symbol,
                interval=operation,
                limit=status_code,  # Reuse for status code
                response_time_ms=response_size,
                status_code=status_code,
                trace_id=trace_id
            )
            
            # Also log raw response data if provided
            if raw_data:
                self.logger.log_raw_data(
                    data_type="api_response",
                    data_sample=api_context,
                    data_stats={"url": url, "status_code": status_code},
                    trace_id=trace_id
                )
        except Exception as e:
            # Critical: Never let logging failures affect trading operations
            self._handle_logging_error("log_api_response", e, operation, symbol, trace_id)
    
    def get_operation_metrics(self) -> Dict[str, Any]:
        """Get collected operation metrics for analysis."""
        try:
            current_time = datetime.utcnow().isoformat()
            
            # Get flow summary if available
            flow_summary = get_flow_summary()
            
            return {
                "service_name": self.service_name,
                "active_operations": len(self._operation_start_times),
                "active_operation_keys": list(self._operation_start_times.keys()),
                "flow_summary": flow_summary,
                "metrics_timestamp": current_time,
                "logger_status": "active"
            }
        except Exception as e:
            # Return safe fallback metrics if metrics collection fails
            self._handle_logging_error("get_operation_metrics", e)
            return {
                "service_name": self.service_name,
                "active_operations": 0,
                "active_operation_keys": [],
                "flow_summary": "metrics_unavailable",
                "metrics_timestamp": datetime.utcnow().isoformat(),
                "logger_status": "degraded"
            }
    
    def reset_metrics(self):
        """Reset performance tracking metrics (for testing or periodic cleanup)."""
        try:
            self._operation_start_times.clear()
            
            # Log metrics reset using raw data logging
            self.logger.log_raw_data(
                data_type="metrics_reset",
                data_sample={"reset_time": datetime.utcnow().isoformat(), "service": self.service_name},
                data_stats={"operation": "metrics_reset"},
                trace_id=get_trace_id()
            )
        except Exception as e:
            # Even if logging fails, we should still clear the metrics
            try:
                self._operation_start_times.clear()
            except:
                pass  # If even clearing fails, continue silently
            self._handle_logging_error("reset_metrics", e)
    
    def log_trading_operation(self, operation_type: str, symbol: str,
                             trade_data: Dict[str, Any], result: str = "success",
                             trace_id: Optional[str] = None):
        """Log complete trading operation for AI analysis and audit trail."""
        try:
            trading_context = {
                "operation_type": operation_type,  # "market_analysis", "order_placement", "position_management"
                "symbol": symbol,
                "trade_data": trade_data,
                "result": result,
                "trading_timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id or get_trace_id()
            }
            
            # Log trading operation with specialized tags
            self.logger.log_raw_data(
                data_type="trading_operation",
                data_sample=trading_context,
                data_stats={
                    "operation_type": operation_type,
                    "symbol": symbol,
                    "result": result
                },
                trace_id=trace_id
            )
        except Exception as e:
            # Critical: Trading operation logging failures must not affect actual trading
            self._handle_logging_error("log_trading_operation", e, operation_type, symbol, trace_id)
    
    def log_market_analysis(self, symbol: str, analysis_data: Dict[str, Any],
                           decision: str = "hold", confidence: float = 0.0,
                           trace_id: Optional[str] = None):
        """Log market analysis results for AI strategy optimization."""
        try:
            analysis_context = {
                "symbol": symbol,
                "analysis_data": analysis_data,
                "decision": decision,  # "buy", "sell", "hold"
                "confidence": confidence,  # 0.0 to 1.0
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id or get_trace_id()
            }
            
            # Log market analysis with AI-searchable tags
            self.logger.log_raw_data(
                data_type="market_analysis",
                data_sample=analysis_context,
                data_stats={
                    "symbol": symbol,
                    "decision": decision,
                    "confidence_level": "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
                },
                trace_id=trace_id
            )
        except Exception as e:
            # Critical: Market analysis logging failures must not affect trading decisions
            self._handle_logging_error("log_market_analysis", e, "market_analysis", symbol, trace_id)
    
    def log_order_execution(self, order_id: str, symbol: str, order_type: str,
                           amount: str, price: str, status: str = "executed",
                           execution_time_ms: Optional[int] = None,
                           trace_id: Optional[str] = None):
        """Log order execution details for compliance and performance tracking."""
        try:
            order_context = {
                "order_id": order_id,
                "symbol": symbol,
                "order_type": order_type,  # "BUY", "SELL", "LIMIT", "MARKET"
                "amount": amount,
                "price": price,
                "status": status,  # "executed", "pending", "cancelled", "failed"
                "execution_time_ms": execution_time_ms,
                "execution_timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id or get_trace_id()
            }
            
            # Log order execution with regulatory compliance tags
            self.logger.log_raw_data(
                data_type="order_execution",
                data_sample=order_context,
                data_stats={
                    "symbol": symbol,
                    "order_type": order_type,
                    "status": status,
                    "amount": amount
                },
                trace_id=trace_id
            )
        except Exception as e:
            # Critical: Order execution logging failures must not affect actual order processing
            self._handle_logging_error("log_order_execution", e, "order_execution", symbol, trace_id)


# Factory function for MarketDataService integration
def create_market_data_logging(service_name: str = "MarketDataService", log_level: str = "INFO") -> MarketDataServiceLogging:
    """Create a MarketDataServiceLogging instance for easy integration."""
    return MarketDataServiceLogging(service_name=service_name, log_level=log_level)


# Direct integration functions for existing MarketDataService methods
def integrate_with_market_data_service(service_instance, log_level: str = "INFO"):
    """
    Integrate logging with existing MarketDataService instance.
    
    This function replaces the placeholder logging methods in MarketDataService
    with actual logging functionality.
    
    Args:
        service_instance: MarketDataService instance to integrate with
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logging integration with specified log level
    logging_integration = create_market_data_logging(log_level=log_level)
    
    # Replace placeholder methods with actual logging
    service_instance._log_operation_start = logging_integration.log_operation_start
    service_instance._log_operation_success = logging_integration.log_operation_success
    service_instance._log_operation_error = logging_integration.log_operation_error
    service_instance._log_graceful_degradation = logging_integration.log_graceful_degradation
    
    # Enable logging in the service
    service_instance._enable_logging = True
    
    # Store logging integration reference for access to additional methods
    service_instance._logging_integration = logging_integration
    
    # Log successful integration
    logging_integration.logger.log_operation_start(
        operation="logging_integration_completed",
        symbol="",
        context={
            "service": "MarketDataService",
            "integration_time": datetime.utcnow().isoformat(),
            "status": "active"
        },
        trace_id=get_trace_id()
    )
    
    return logging_integration


if __name__ == "__main__":
    # Example usage and testing
    logging_service = create_market_data_logging()
    
    # Test basic functionality
    print("Testing MarketDataService Logging Integration...")
    
    # Test operation lifecycle
    logging_service.log_operation_start("test_operation", symbol="BTCUSDT", trace_id="test_123")
    logging_service.log_performance_metrics("test_operation", {"duration": 150, "rows": 100})
    logging_service.log_operation_success("test_operation", symbol="BTCUSDT", trace_id="test_123", data_points=100)
    
    # Test metrics retrieval
    metrics = logging_service.get_operation_metrics()
    print(f"Operation metrics: {metrics}")
    
    print("MarketDataService Logging Integration test completed!")
