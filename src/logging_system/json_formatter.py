"""
AI-Optimized JSON Log Formatter
Creates structured JSON logs with semantic tags for AI searchability
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from .trace_generator import get_trace_id


class AIOptimizedJSONFormatter(logging.Formatter):
    """
    Custom JSON formatter optimized for AI log analysis.
    
    Creates structured logs with:
    - Consistent JSON schema
    - Semantic tags for pattern recognition
    - Contextual data preservation
    - Flow and trace ID integration
    """
    
    def __init__(self, service_name: str = "MarketDataService"):
        super().__init__()
        self.service_name = service_name
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as AI-searchable JSON.
        
        Expected extra fields in record:
        - operation: Method name being executed
        - context: Dict with operation-specific data
        - tags: List of semantic tags
        - flow: Dict with flow information
        - trace_id: Trace identifier (auto-generated if missing)
        """
        
        # Base log structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": self.service_name,
            "operation": getattr(record, 'operation', 'unknown'),
            "message": record.getMessage()
        }
        
        # Add context data if provided
        if hasattr(record, 'context') and record.context:
            log_entry["context"] = record.context
        
        # Add flow information if provided
        if hasattr(record, 'flow') and record.flow:
            log_entry["flow"] = record.flow
        
        # Add semantic tags if provided
        if hasattr(record, 'tags') and record.tags:
            log_entry["tags"] = record.tags
        
        # Add trace ID (generate if not provided)
        log_entry["trace_id"] = getattr(record, 'trace_id', get_trace_id())
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        return json.dumps(log_entry, ensure_ascii=False, separators=(',', ':'))


class StructuredLogger:
    """
    High-level interface for structured logging with AI optimization.
    
    Provides convenience methods for different log levels with
    automatic trace ID generation and context preservation.
    """
    
    def __init__(self, name: str, service_name: str = "MarketDataService"):
        self.logger = logging.getLogger(name)
        self.service_name = service_name
        
        # Configure logger if not already configured
        if not self.logger.handlers:
            self._configure_logger()
    
    def _configure_logger(self):
        """Configure logger with AI-optimized JSON formatter."""
        handler = logging.StreamHandler()
        formatter = AIOptimizedJSONFormatter(self.service_name)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
    
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
            'trace_id': trace_id
        }
        
        self.logger.log(level, message, extra=extra)
    
    def trace(self, message: str, operation: str = "", 
              context: Optional[Dict[str, Any]] = None,
              tags: Optional[List[str]] = None,
              flow: Optional[Dict[str, Any]] = None,
              trace_id: Optional[str] = None):
        """Log TRACE level - raw data and detailed debugging."""
        self._log(logging.DEBUG - 5, message, operation, context, tags, flow, trace_id)
    
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
            self.logger.error(message, extra={
                'operation': operation,
                'context': context or {},
                'tags': tags or [],
                'flow': flow or {},
                'trace_id': trace_id
            }, exc_info=True)
        else:
            self._log(logging.ERROR, message, operation, context, tags, flow, trace_id)
    
    def critical(self, message: str, operation: str = "", 
                 context: Optional[Dict[str, Any]] = None,
                 tags: Optional[List[str]] = None,
                 flow: Optional[Dict[str, Any]] = None,
                 trace_id: Optional[str] = None):
        """Log CRITICAL level - system failures requiring immediate attention."""
        self._log(logging.CRITICAL, message, operation, context, tags, flow, trace_id)


def get_logger(name: str, service_name: str = "MarketDataService") -> StructuredLogger:
    """
    Get a structured logger instance for AI-optimized logging.
    
    Args:
        name: Logger name (typically module name)
        service_name: Service name for log identification
        
    Returns:
        StructuredLogger instance configured for AI analysis
    """
    return StructuredLogger(name, service_name)