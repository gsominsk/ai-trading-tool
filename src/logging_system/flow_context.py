"""
Flow Context Management for AI-Optimized Logging
Tracks flow stages and maintains context throughout operation chains
"""

import threading
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from .trace_generator import get_trace_id


class FlowContext:
    """
    Thread-local context for tracking operation flow stages.
    
    Maintains flow state throughout operation chains to enable
    AI to understand operation progression and relationships.
    """
    
    def __init__(self):
        self._local = threading.local()
    
    @property
    def current_flow(self) -> Optional[Dict[str, Any]]:
        """Get current flow context."""
        return getattr(self._local, 'flow', None)
    
    @property
    def current_stage(self) -> Optional[str]:
        """Get current operation stage."""
        flow = self.current_flow
        return flow.get('stage') if flow else None
    
    @property
    def trace_id(self) -> Optional[str]:
        """Get current trace ID."""
        flow = self.current_flow
        return flow.get('trace_id') if flow else None
    
    def start_flow(self, symbol: str = "", operation: str = "",
                   initial_stage: str = "initiation", parent_trace_id: Optional[str] = None) -> str:
        """
        Start a new operation flow.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            operation: Operation type (e.g., "enhanced_context")
            initial_stage: Starting stage name
            parent_trace_id: The trace_id of the parent operation, if any.
            
        Returns:
            Generated trace ID
        """
        trace_id = get_trace_id(parent_trace_id=parent_trace_id)
        
        self._local.flow = {
            "trace_id": trace_id,
            "parent_trace_id": parent_trace_id,
            "stage": initial_stage,
            "previous_stage": None,
            "symbol": symbol,
            "operation": operation,
            "stages_completed": [],
            "context_data": {}
        }
        
        return trace_id
    
    def advance_stage(self, next_stage: str, context_data: Optional[Dict[str, Any]] = None):
        """
        Advance to next operation stage.
        
        Args:
            next_stage: Name of the next stage
            context_data: Additional context data for this stage
        """
        if not self.current_flow:
            return
        
        current_stage = self.current_flow["stage"]
        self.current_flow["stages_completed"].append(current_stage)
        self.current_flow["previous_stage"] = current_stage
        self.current_flow["stage"] = next_stage
        
        if context_data:
            self.current_flow["context_data"].update(context_data)
    
    def set_stage_context(self, key: str, value: Any):
        """Add context data to current stage."""
        if self.current_flow:
            self.current_flow["context_data"][key] = value
    
    def get_stage_context(self, key: str, default: Any = None) -> Any:
        """Get context data from current flow."""
        if self.current_flow:
            return self.current_flow["context_data"].get(key, default)
        return default
    
    def complete_flow(self, final_stage: str = "completion"):
        """Mark flow as completed."""
        if self.current_flow:
            self.current_flow["stages_completed"].append(self.current_flow["stage"])
            self.current_flow["stage"] = final_stage
            self.current_flow["flow_completion"] = True
    
    def terminate_flow(self, termination_reason: str = "error"):
        """Mark flow as terminated due to error."""
        if self.current_flow:
            self.current_flow["flow_termination"] = True
            self.current_flow["termination_reason"] = termination_reason
    
    def clear_flow(self):
        """Clear current flow context."""
        if hasattr(self._local, 'flow'):
            delattr(self._local, 'flow')
    
    def get_flow_summary(self) -> Dict[str, Any]:
        """Get complete flow summary for logging."""
        if not self.current_flow:
            return {}
        
        return {
            "trace_id": self.current_flow["trace_id"],
            "parent_trace_id": self.current_flow.get("parent_trace_id"),
            "stage": self.current_flow["stage"],
            "previous_stage": self.current_flow.get("previous_stage"),
            "stages_completed": self.current_flow.get("stages_completed", []),
            "flow_completion": self.current_flow.get("flow_completion", False),
            "flow_termination": self.current_flow.get("flow_termination", False),
            "termination_reason": self.current_flow.get("termination_reason")
        }


# Global flow context instance
_flow_context = FlowContext()


@contextmanager
def flow_operation(symbol: str = "", operation: str = "",
                   initial_stage: str = "initiation"):
    """
    Context manager for operation flow tracking with nested operation support.
    
    Usage:
        with flow_operation("BTCUSDT", "get_market_data"):
            # operation code here
            advance_to_stage("data_collection")
            # more operation code
    """
    # Store previous flow for nested operations
    previous_flow = _flow_context.current_flow
    
    flow_id = _flow_context.start_flow(symbol, operation, initial_stage)
    try:
        yield flow_id
    except Exception as e:
        _flow_context.terminate_flow(f"exception: {type(e).__name__}")
        raise
    finally:
        # Restore previous flow instead of clearing (for nested operations)
        if previous_flow:
            _flow_context._local.flow = previous_flow
        else:
            _flow_context.clear_flow()


def get_current_flow() -> Optional[Dict[str, Any]]:
    """Get current flow context."""
    return _flow_context.current_flow


def get_flow_summary() -> Dict[str, Any]:
    """Get current flow summary for logging."""
    return _flow_context.get_flow_summary()


def advance_to_stage(next_stage: str, **context_data):
    """Advance to next stage with optional context data."""
    _flow_context.advance_stage(next_stage, context_data)


def set_flow_context(key: str, value: Any):
    """Set context data in current flow."""
    _flow_context.set_stage_context(key, value)


def get_flow_context(key: str, default: Any = None) -> Any:
    """Get context data from current flow."""
    return _flow_context.get_stage_context(key, default)


def complete_current_flow():
    """Mark current flow as completed."""
    _flow_context.complete_flow()


def terminate_current_flow(reason: str = "error"):
    """Mark current flow as terminated."""
    _flow_context.terminate_flow(reason)