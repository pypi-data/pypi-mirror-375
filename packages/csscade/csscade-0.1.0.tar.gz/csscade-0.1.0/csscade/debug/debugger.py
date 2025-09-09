"""Debug mode and performance tracking for CSSCade."""

import time
import traceback
from typing import Any, Dict, List, Optional, Callable
from functools import wraps
from contextlib import contextmanager


class DebugInfo:
    """Container for debug information."""
    
    def __init__(self):
        """Initialize debug info."""
        self.operations: List[Dict[str, Any]] = []
        self.performance: Dict[str, float] = {}
        self.decisions: List[Dict[str, Any]] = []
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.call_stack: List[str] = []
        self.stats: Dict[str, Any] = {}
    
    def add_operation(
        self,
        operation: str,
        details: Dict[str, Any],
        duration: Optional[float] = None
    ) -> None:
        """
        Add operation to debug log.
        
        Args:
            operation: Operation name
            details: Operation details
            duration: Operation duration in seconds
        """
        entry = {
            'operation': operation,
            'details': details,
            'timestamp': time.time()
        }
        
        if duration is not None:
            entry['duration'] = duration
        
        self.operations.append(entry)
    
    def add_decision(
        self,
        decision: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add merge decision to debug log.
        
        Args:
            decision: Decision made
            reason: Reason for decision
            context: Additional context
        """
        self.decisions.append({
            'decision': decision,
            'reason': reason,
            'context': context or {},
            'timestamp': time.time()
        })
    
    def add_warning(self, warning: str) -> None:
        """Add warning message."""
        self.warnings.append(warning)
    
    def add_error(self, error: str) -> None:
        """Add error message."""
        self.errors.append(error)
    
    def add_performance_metric(self, metric: str, value: float) -> None:
        """Add performance metric."""
        self.performance[metric] = value
    
    def update_stats(self, stats: Dict[str, Any]) -> None:
        """Update statistics."""
        self.stats.update(stats)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'operations': self.operations,
            'performance': self.performance,
            'decisions': self.decisions,
            'warnings': self.warnings,
            'errors': self.errors,
            'stats': self.stats
        }
    
    def get_summary(self) -> str:
        """
        Get debug summary.
        
        Returns:
            Human-readable summary
        """
        lines = [
            "=== Debug Summary ===",
            f"Operations: {len(self.operations)}",
            f"Decisions: {len(self.decisions)}",
            f"Warnings: {len(self.warnings)}",
            f"Errors: {len(self.errors)}"
        ]
        
        if self.performance:
            lines.append("\nPerformance Metrics:")
            for metric, value in self.performance.items():
                lines.append(f"  {metric}: {value:.4f}s")
        
        if self.stats:
            lines.append("\nStatistics:")
            for stat, value in self.stats.items():
                lines.append(f"  {stat}: {value}")
        
        if self.warnings:
            lines.append("\nWarnings:")
            for warning in self.warnings[:5]:  # Show first 5
                lines.append(f"  - {warning}")
            if len(self.warnings) > 5:
                lines.append(f"  ... and {len(self.warnings) - 5} more")
        
        if self.errors:
            lines.append("\nErrors:")
            for error in self.errors[:5]:  # Show first 5
                lines.append(f"  - {error}")
            if len(self.errors) > 5:
                lines.append(f"  ... and {len(self.errors) - 5} more")
        
        return "\n".join(lines)


class Debugger:
    """Debug mode manager for CSSCade."""
    
    def __init__(self, enabled: bool = False, verbose: bool = False):
        """
        Initialize debugger.
        
        Args:
            enabled: Whether debug mode is enabled
            verbose: Whether to print verbose output
        """
        self.enabled = enabled
        self.verbose = verbose
        self.info = DebugInfo()
        self._timers: Dict[str, float] = {}
    
    @contextmanager
    def operation(self, name: str, **details):
        """
        Context manager for tracking operations.
        
        Args:
            name: Operation name
            **details: Operation details
        """
        if not self.enabled:
            yield
            return
        
        start_time = time.time()
        
        if self.verbose:
            print(f"[DEBUG] Starting: {name}")
            if details:
                for key, value in details.items():
                    print(f"  {key}: {value}")
        
        try:
            yield
        except Exception as e:
            self.info.add_error(f"{name}: {str(e)}")
            if self.verbose:
                print(f"[DEBUG] Error in {name}: {str(e)}")
            raise
        finally:
            duration = time.time() - start_time
            self.info.add_operation(name, details, duration)
            
            if self.verbose:
                print(f"[DEBUG] Completed: {name} ({duration:.4f}s)")
    
    def start_timer(self, name: str) -> None:
        """
        Start a named timer.
        
        Args:
            name: Timer name
        """
        if self.enabled:
            self._timers[name] = time.time()
    
    def stop_timer(self, name: str) -> Optional[float]:
        """
        Stop a named timer and record the duration.
        
        Args:
            name: Timer name
            
        Returns:
            Duration in seconds
        """
        if not self.enabled or name not in self._timers:
            return None
        
        duration = time.time() - self._timers[name]
        del self._timers[name]
        self.info.add_performance_metric(name, duration)
        
        if self.verbose:
            print(f"[DEBUG] Timer '{name}': {duration:.4f}s")
        
        return duration
    
    def log_decision(self, decision: str, reason: str, **context) -> None:
        """
        Log a merge decision.
        
        Args:
            decision: Decision made
            reason: Reason for decision
            **context: Additional context
        """
        if not self.enabled:
            return
        
        self.info.add_decision(decision, reason, context)
        
        if self.verbose:
            print(f"[DEBUG] Decision: {decision}")
            print(f"  Reason: {reason}")
            if context:
                for key, value in context.items():
                    print(f"  {key}: {value}")
    
    def log_warning(self, warning: str) -> None:
        """
        Log a warning.
        
        Args:
            warning: Warning message
        """
        if self.enabled:
            self.info.add_warning(warning)
            if self.verbose:
                print(f"[DEBUG] Warning: {warning}")
    
    def log_error(self, error: str) -> None:
        """
        Log an error.
        
        Args:
            error: Error message
        """
        if self.enabled:
            self.info.add_error(error)
            if self.verbose:
                print(f"[DEBUG] Error: {error}")
    
    def update_stats(self, **stats) -> None:
        """
        Update statistics.
        
        Args:
            **stats: Statistics to update
        """
        if self.enabled:
            self.info.update_stats(stats)
    
    def get_info(self) -> DebugInfo:
        """Get debug information."""
        return self.info
    
    def get_summary(self) -> str:
        """Get debug summary."""
        return self.info.get_summary()
    
    def clear(self) -> None:
        """Clear debug information."""
        self.info = DebugInfo()
        self._timers.clear()


def debug_trace(func: Callable) -> Callable:
    """
    Decorator to trace function calls in debug mode.
    
    Args:
        func: Function to trace
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if first argument has debugger attribute
        if args and hasattr(args[0], '_debugger'):
            debugger = args[0]._debugger
            if debugger and debugger.enabled:
                func_name = f"{args[0].__class__.__name__}.{func.__name__}"
                with debugger.operation(func_name, args=str(args[1:]), kwargs=str(kwargs)):
                    return func(*args, **kwargs)
        
        return func(*args, **kwargs)
    
    return wrapper


class PerformanceTracker:
    """Track performance metrics."""
    
    def __init__(self):
        """Initialize performance tracker."""
        self.metrics: Dict[str, List[float]] = {}
        self.counters: Dict[str, int] = {}
    
    def record(self, metric: str, value: float) -> None:
        """
        Record a metric value.
        
        Args:
            metric: Metric name
            value: Metric value
        """
        if metric not in self.metrics:
            self.metrics[metric] = []
        self.metrics[metric].append(value)
    
    def increment(self, counter: str, amount: int = 1) -> None:
        """
        Increment a counter.
        
        Args:
            counter: Counter name
            amount: Amount to increment
        """
        if counter not in self.counters:
            self.counters[counter] = 0
        self.counters[counter] += amount
    
    def get_average(self, metric: str) -> Optional[float]:
        """
        Get average value for a metric.
        
        Args:
            metric: Metric name
            
        Returns:
            Average value or None
        """
        if metric not in self.metrics or not self.metrics[metric]:
            return None
        return sum(self.metrics[metric]) / len(self.metrics[metric])
    
    def get_total(self, metric: str) -> Optional[float]:
        """
        Get total value for a metric.
        
        Args:
            metric: Metric name
            
        Returns:
            Total value or None
        """
        if metric not in self.metrics:
            return None
        return sum(self.metrics[metric])
    
    def get_count(self, counter: str) -> int:
        """
        Get counter value.
        
        Args:
            counter: Counter name
            
        Returns:
            Counter value
        """
        return self.counters.get(counter, 0)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get performance summary.
        
        Returns:
            Summary dictionary
        """
        summary = {
            'metrics': {},
            'counters': self.counters.copy()
        }
        
        for metric, values in self.metrics.items():
            if values:
                summary['metrics'][metric] = {
                    'count': len(values),
                    'total': sum(values),
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
        
        return summary
    
    def clear(self) -> None:
        """Clear all metrics and counters."""
        self.metrics.clear()
        self.counters.clear()