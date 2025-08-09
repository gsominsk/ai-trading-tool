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
    Thread-safe, simplified trace ID generator for hierarchical logging.
    
    Generates a unique ID for an entire operation flow.
    The concept of a separate `flow_id` is deprecated and merged into this single `trace_id`.
    """
    
    def __init__(self, session_id: str = "001"):
        self.session_id = session_id
        self._counter = 0
        self._lock = threading.Lock()

    def generate_trace_id(self, parent_trace_id: Optional[str] = None) -> str:
        """
        Generates a unique trace ID for an operation.
        
        The `parent_trace_id` is accepted for semantic compatibility with hierarchical
        logging, but the core generation logic remains independent to ensure uniqueness.
        
        Format: trd_{session}_{timestamp}{sequence}
        Example: "trd_001_20250808233800001"
        """
        with self._lock:
            self._counter += 1
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            sequence = f"{self._counter:05d}"
            return f"trd_{self.session_id}_{timestamp}{sequence}"

    def reset_counter(self):
        """Resets the counter, primarily for testing purposes."""
        with self._lock:
            self._counter = 0


# Global singleton instance of the trace generator
_trace_generator = TraceGenerator()


def get_trace_id(parent_trace_id: Optional[str] = None) -> str:
    """
    Public function to get a new unique trace ID.
    
    Args:
        parent_trace_id: The trace_id of the parent operation, if any.
    """
    return _trace_generator.generate_trace_id(parent_trace_id)


def reset_trace_counter():
    """Public function to reset the global trace counter (for testing)."""
    _trace_generator.reset_counter()