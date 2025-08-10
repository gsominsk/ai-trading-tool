"""
AI-Optimized JSON Log Formatter
Creates structured JSON logs with semantic tags for AI searchability
"""

import json
import logging
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from .trace_generator import get_trace_id
from .flow_context import get_flow_summary

# Add custom TRACE level (below DEBUG level)
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, 'TRACE')


class AIOptimizedJSONFormatter(logging.Formatter):
    """
    Custom JSON formatter optimized for AI log analysis.
    
    Creates structured logs with:
    - Consistent JSON schema
    - Semantic tags for pattern recognition
    - Contextual data preservation
    - Flow and trace ID integration
    """
    
    def __init__(self):
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as AI-searchable JSON.
        
        Expected extra fields in record:
        - operation: Method name being executed
        - context: Dict with operation-specific data
        - tags: List of semantic tags
        - flow: Dict with flow information
        - trace_id: Trace identifier (auto-generated if missing)
        - service_name: Name of the service/component
        """
        
        # Base log structure
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": getattr(record, 'service_name', 'default_service'),
            "operation": getattr(record, 'operation', 'unknown'),
            "message": record.getMessage()
        }
        
        # Add context data if provided, and handle hierarchical tracing
        if hasattr(record, 'context') and record.context:
            context_data = record.context.copy()  # Work with a copy
            parent_trace_id = context_data.pop('parent_trace_id', None)
            if parent_trace_id:
                log_entry['parent_trace_id'] = parent_trace_id
            
            if context_data: # Add context only if it's not empty after popping
                log_entry["context"] = context_data
        
        # Add flow information - ensure consistent flow context
        flow_data = getattr(record, 'flow', None)
        if not flow_data:
            # Always try to get flow from global context
            flow_data = get_flow_summary()
        
        # Always include flow data (empty dict if no flow active)
        log_entry["flow"] = flow_data if flow_data else {}
        
        # Add semantic tags if provided
        if hasattr(record, 'tags') and record.tags:
            log_entry["tags"] = record.tags
        
        # Add trace ID - coordinate with flow context but maintain compatibility
        trace_id = getattr(record, 'trace_id', None)
        if trace_id is None:
            # Always generate proper trace_id format for consistency
            trace_id = get_trace_id()
            
            # For flow operations, store relationship in flow data
            flow_data = log_entry.get("flow", {})
            if flow_data and flow_data.get("flow_id"):
                # Add trace_id to flow context for coordination
                flow_data["trace_id"] = trace_id
                log_entry["flow"] = flow_data
        
        # Ensure trace_id is attached to the record for other handlers/tests
        record.trace_id = trace_id
        log_entry["trace_id"] = trace_id
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        try:
            return json.dumps(log_entry, ensure_ascii=False, separators=(',', ':'))
        except (TypeError, ValueError) as e:
            # Fallback: если JSON serialization не удалась, возвращаем простой текст
            service_name = getattr(record, 'service_name', 'default_service')
            return f'{{"timestamp":"{datetime.now(timezone.utc).isoformat()}","level":"{record.levelname}","service":"{service_name}","message":"FALLBACK_LOG: {record.getMessage()}","serialization_error":"{str(e)}"}}'


class StructuredLogger:
    """
    High-level interface for structured logging with AI optimization.
    
    Provides convenience methods for different log levels with
    automatic trace ID generation and context preservation.
    This class acts as a custom LoggerAdapter.
    """
    
    def __init__(self, name: str, service_name: str):
        self.logger = logging.getLogger(name)
        self.service_name = service_name
    
    def _log(self, level: int, message: str, operation: str = "",
             context: Optional[Dict[str, Any]] = None,
             tags: Optional[List[str]] = None,
             flow: Optional[Dict[str, Any]] = None,
             trace_id: Optional[str] = None):
        """Internal logging method with structured data."""
        
        extra = {
            'operation': operation,
            'context': context or {},
            'tags': tags or [],
            'flow': flow or {},
            'trace_id': trace_id,
            'service_name': self.service_name
        }
        
        try:
            self.logger.log(level, message, extra=extra)
        except Exception as e:
            # Логи сломались - останавливаем сервис
            print(f"CRITICAL: Logging system failed - shutting down service: {e}", file=sys.stderr)
            # Graceful exit вместо os._exit(1)
            raise SystemExit(1)
    
    def trace(self, message: str, operation: str = "",
              context: Optional[Dict[str, Any]] = None,
              tags: Optional[List[str]] = None,
              flow: Optional[Dict[str, Any]] = None,
              trace_id: Optional[str] = None):
        """Log TRACE level - raw data and detailed debugging."""
        # Use proper TRACE level (5) - below DEBUG
        self._log(TRACE_LEVEL, message, operation, context, tags, flow, trace_id)
    
    def debug(self, message: str, operation: str = "", 
              context: Optional[Dict[str, Any]] = None,
              tags: Optional[List[str]] = None,
              flow: Optional[Dict[str, Any]] = None,
              trace_id: Optional[str] = None):
        """Log DEBUG level - detailed debugging information."""
        self._log(logging.DEBUG, message, operation, context, tags, flow, trace_id)
    
    def info(self, message: str, operation: str = "", 
             context: Optional[Dict[str, Any]] = None,
             tags: Optional[List[str]] = None,
             flow: Optional[Dict[str, Any]] = None,
             trace_id: Optional[str] = None):
        """Log INFO level - general information."""
        self._log(logging.INFO, message, operation, context, tags, flow, trace_id)
    
    def warning(self, message: str, operation: str = "", 
                context: Optional[Dict[str, Any]] = None,
                tags: Optional[List[str]] = None,
                flow: Optional[Dict[str, Any]] = None,
                trace_id: Optional[str] = None):
        """Log WARNING level - potential issues."""
        self._log(logging.WARNING, message, operation, context, tags, flow, trace_id)
    
    def error(self, message: str, operation: str = "",
              context: Optional[Dict[str, Any]] = None,
              tags: Optional[List[str]] = None,
              flow: Optional[Dict[str, Any]] = None,
              trace_id: Optional[str] = None,
              exc_info: bool = False):
        """Log ERROR level - errors affecting functionality."""
        if exc_info:
            try:
                self.logger.error(message, extra={
                    'operation': operation,
                    'context': context or {},
                    'tags': tags or [],
                    'flow': flow or {},
                    'trace_id': trace_id
                }, exc_info=True)
            except Exception as e:
                # Логи сломались - останавливаем сервис
                print(f"CRITICAL: Logging system failed - shutting down service: {e}", file=sys.stderr)
                # Graceful exit вместо os._exit(1)
                raise SystemExit(1)
        else:
            self._log(logging.ERROR, message, operation, context, tags, flow, trace_id)
    
    def critical(self, message: str, operation: str = "", 
                 context: Optional[Dict[str, Any]] = None,
                 tags: Optional[List[str]] = None,
                 flow: Optional[Dict[str, Any]] = None,
                 trace_id: Optional[str] = None):
        """Log CRITICAL level - system failures requiring immediate attention."""
        self._log(logging.CRITICAL, message, operation, context, tags, flow, trace_id)


def get_logger(name: str, service_name: str) -> StructuredLogger:
    """
    Get a structured logger instance for AI-optimized logging.
    
    Args:
        name: Logger name (typically module name)
        service_name: Service name for log identification
        
    Returns:
        StructuredLogger instance configured for AI analysis
    """
    return StructuredLogger(name, service_name)