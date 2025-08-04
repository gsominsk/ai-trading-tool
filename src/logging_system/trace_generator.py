"""
AI-Optimized Trace ID Generation System
Generates sequential trace IDs and flow IDs for complete log traceability
"""

import time
import threading
from datetime import datetime, timezone
from typing import Optional


class TraceGenerator:
    """
    Thread-safe trace ID and flow ID generator for AI-searchable logging.
    
    Generates IDs in format:
    - trace_id: "trd_001_2025080421450001" (trd + session + timestamp + sequence)
    - flow_id: "flow_btc_20250804214500" (flow + symbol + timestamp)
    """
    
    def __init__(self, session_id: str = "001"):
        self.session_id = session_id
        self._trace_counter = 0
        self._lock = threading.Lock()
    
    def generate_trace_id(self) -> str:
        """
        Generate sequential trace ID for step-by-step tracking.
        
        Format: trd_{session}_{timestamp}{sequence}
        Example: "trd_001_2025080421450001"
        """
        with self._lock:
            self._trace_counter += 1
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            sequence = f"{self._trace_counter:04d}"
            return f"trd_{self.session_id}_{timestamp}{sequence}"
    
    def generate_flow_id(self, symbol: str, operation: str = "") -> str:
        """
        Generate flow ID for grouping all logs from single request.
        
        Format: flow_{symbol}_{timestamp} or flow_{operation}_{timestamp}
        Examples: 
        - "flow_btc_20250804214500"
        - "flow_enh_20250804214500"
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        identifier = symbol.lower().replace("usdt", "") if symbol else operation
        return f"flow_{identifier}_{timestamp}"
    
    def reset_counter(self):
        """Reset trace counter (for testing purposes)."""
        with self._lock:
            self._trace_counter = 0


# Global trace generator instance
_trace_generator = TraceGenerator()


def get_trace_id() -> str:
    """Get next sequential trace ID."""
    return _trace_generator.generate_trace_id()


def get_flow_id(symbol: str = "", operation: str = "") -> str:
    """Get flow ID for request grouping."""
    return _trace_generator.generate_flow_id(symbol, operation)


def reset_trace_counter():
    """Reset trace counter (for testing)."""
    _trace_generator.reset_counter()