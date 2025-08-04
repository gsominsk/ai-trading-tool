"""
AI-Optimized Logging System for MarketDataService

This module provides structured, AI-searchable logging with:
- JSON-formatted logs with semantic tags
- Flow context tracking with trace IDs
- Graceful degradation logging patterns
- Performance metrics collection
- Error context preservation

Usage:
    from src.logging_system import configure_ai_logging, get_ai_logger, flow_operation
    
    # Configure logging
    configure_ai_logging(log_level="DEBUG", log_file="logs/trading.log")
    
    # Get logger
    logger = get_ai_logger(__name__)
    
    # Use flow context
    with flow_operation("BTCUSDT", "get_market_data"):
        logger.info("Processing market data", operation="get_market_data")
"""

from .logger_config import (
    configure_ai_logging,
    get_ai_logger,
    MarketDataLogger
)

from .flow_context import (
    flow_operation,
    advance_to_stage,
    set_flow_context,
    get_flow_context,
    get_flow_summary,
    complete_current_flow,
    terminate_current_flow
)

from .trace_generator import (
    get_trace_id,
    get_flow_id,
    reset_trace_counter
)

from .json_formatter import (
    StructuredLogger,
    get_logger
)

__all__ = [
    # Main configuration
    "configure_ai_logging",
    "get_ai_logger",
    "MarketDataLogger",
    
    # Flow context management
    "flow_operation",
    "advance_to_stage", 
    "set_flow_context",
    "get_flow_context",
    "get_flow_summary",
    "complete_current_flow",
    "terminate_current_flow",
    
    # ID generation
    "get_trace_id",
    "get_flow_id",
    "reset_trace_counter",
    
    # Low-level interfaces
    "StructuredLogger",
    "get_logger"
]

# Version info
__version__ = "1.0.0"
__author__ = "AI Trading System"
__description__ = "AI-Optimized Logging System with Flow Context Tracking"