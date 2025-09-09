"""Tests for debug mode and performance tracking."""

import pytest
import time
from csscade.debug import Debugger, DebugInfo, PerformanceTracker, debug_trace


class TestDebugInfo:
    """Test cases for DebugInfo."""
    
    def test_add_operation(self):
        """Test adding operations."""
        info = DebugInfo()
        
        info.add_operation('merge', {'source': 'a', 'override': 'b'}, 0.5)
        
        assert len(info.operations) == 1
        assert info.operations[0]['operation'] == 'merge'
        assert info.operations[0]['duration'] == 0.5
    
    def test_add_decision(self):
        """Test adding decisions."""
        info = DebugInfo()
        
        info.add_decision('use_component', 'Conflict detected', {'property': 'color'})
        
        assert len(info.decisions) == 1
        assert info.decisions[0]['decision'] == 'use_component'
        assert info.decisions[0]['reason'] == 'Conflict detected'
    
    def test_add_warnings_and_errors(self):
        """Test adding warnings and errors."""
        info = DebugInfo()
        
        info.add_warning('Invalid property')
        info.add_error('Parse error')
        
        assert len(info.warnings) == 1
        assert len(info.errors) == 1
        assert info.warnings[0] == 'Invalid property'
        assert info.errors[0] == 'Parse error'
    
    def test_performance_metrics(self):
        """Test adding performance metrics."""
        info = DebugInfo()
        
        info.add_performance_metric('parse_time', 0.123)
        info.add_performance_metric('merge_time', 0.456)
        
        assert info.performance['parse_time'] == 0.123
        assert info.performance['merge_time'] == 0.456
    
    def test_update_stats(self):
        """Test updating statistics."""
        info = DebugInfo()
        
        info.update_stats({'total_merges': 10, 'cache_hits': 5})
        
        assert info.stats['total_merges'] == 10
        assert info.stats['cache_hits'] == 5
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        info = DebugInfo()
        
        info.add_operation('test', {}, 1.0)
        info.add_warning('warning')
        
        result = info.to_dict()
        
        assert 'operations' in result
        assert 'warnings' in result
        assert len(result['operations']) == 1
        assert len(result['warnings']) == 1
    
    def test_get_summary(self):
        """Test getting summary."""
        info = DebugInfo()
        
        info.add_operation('op1', {}, 1.0)
        info.add_decision('dec1', 'reason', {})
        info.add_warning('warn1')
        info.add_error('err1')
        info.add_performance_metric('metric1', 0.5)
        
        summary = info.get_summary()
        
        assert 'Operations: 1' in summary
        assert 'Decisions: 1' in summary
        assert 'Warnings: 1' in summary
        assert 'Errors: 1' in summary
        assert 'metric1: 0.5000s' in summary


class TestDebugger:
    """Test cases for Debugger."""
    
    def test_disabled_debugger(self):
        """Test that disabled debugger doesn't track."""
        debugger = Debugger(enabled=False)
        
        with debugger.operation('test'):
            pass
        
        assert len(debugger.info.operations) == 0
    
    def test_enabled_debugger(self):
        """Test that enabled debugger tracks operations."""
        debugger = Debugger(enabled=True)
        
        with debugger.operation('test', key='value'):
            time.sleep(0.01)
        
        assert len(debugger.info.operations) == 1
        assert debugger.info.operations[0]['operation'] == 'test'
        assert debugger.info.operations[0]['duration'] > 0
    
    def test_operation_error_handling(self):
        """Test operation error handling."""
        debugger = Debugger(enabled=True)
        
        with pytest.raises(ValueError):
            with debugger.operation('failing_op'):
                raise ValueError('Test error')
        
        assert len(debugger.info.errors) == 1
        assert 'Test error' in debugger.info.errors[0]
    
    def test_timers(self):
        """Test timer functionality."""
        debugger = Debugger(enabled=True)
        
        debugger.start_timer('test_timer')
        time.sleep(0.01)
        duration = debugger.stop_timer('test_timer')
        
        assert duration is not None
        assert duration > 0
        assert 'test_timer' in debugger.info.performance
    
    def test_log_decision(self):
        """Test logging decisions."""
        debugger = Debugger(enabled=True)
        
        debugger.log_decision('merge_strategy', 'Conflicts found', property='color')
        
        assert len(debugger.info.decisions) == 1
        assert debugger.info.decisions[0]['decision'] == 'merge_strategy'
        assert debugger.info.decisions[0]['context']['property'] == 'color'
    
    def test_log_warning_and_error(self):
        """Test logging warnings and errors."""
        debugger = Debugger(enabled=True)
        
        debugger.log_warning('This is a warning')
        debugger.log_error('This is an error')
        
        assert len(debugger.info.warnings) == 1
        assert len(debugger.info.errors) == 1
    
    def test_update_stats(self):
        """Test updating statistics."""
        debugger = Debugger(enabled=True)
        
        debugger.update_stats(merges=10, conflicts=3)
        
        assert debugger.info.stats['merges'] == 10
        assert debugger.info.stats['conflicts'] == 3
    
    def test_clear(self):
        """Test clearing debug info."""
        debugger = Debugger(enabled=True)
        
        debugger.log_warning('test')
        assert len(debugger.info.warnings) == 1
        
        debugger.clear()
        
        assert len(debugger.info.warnings) == 0
        assert len(debugger._timers) == 0
    
    def test_verbose_mode(self, capsys):
        """Test verbose mode output."""
        debugger = Debugger(enabled=True, verbose=True)
        
        with debugger.operation('test_op'):
            pass
        
        captured = capsys.readouterr()
        assert '[DEBUG] Starting: test_op' in captured.out
        assert '[DEBUG] Completed: test_op' in captured.out


class TestPerformanceTracker:
    """Test cases for PerformanceTracker."""
    
    def test_record_metrics(self):
        """Test recording metrics."""
        tracker = PerformanceTracker()
        
        tracker.record('parse_time', 0.1)
        tracker.record('parse_time', 0.2)
        tracker.record('merge_time', 0.3)
        
        assert len(tracker.metrics['parse_time']) == 2
        assert len(tracker.metrics['merge_time']) == 1
    
    def test_increment_counters(self):
        """Test incrementing counters."""
        tracker = PerformanceTracker()
        
        tracker.increment('merges')
        tracker.increment('merges', 5)
        tracker.increment('conflicts', 2)
        
        assert tracker.get_count('merges') == 6
        assert tracker.get_count('conflicts') == 2
    
    def test_get_average(self):
        """Test getting average metric value."""
        tracker = PerformanceTracker()
        
        tracker.record('time', 1.0)
        tracker.record('time', 2.0)
        tracker.record('time', 3.0)
        
        assert tracker.get_average('time') == 2.0
        assert tracker.get_average('nonexistent') is None
    
    def test_get_total(self):
        """Test getting total metric value."""
        tracker = PerformanceTracker()
        
        tracker.record('time', 1.0)
        tracker.record('time', 2.0)
        
        assert tracker.get_total('time') == 3.0
        assert tracker.get_total('nonexistent') is None
    
    def test_get_summary(self):
        """Test getting performance summary."""
        tracker = PerformanceTracker()
        
        tracker.record('time', 1.0)
        tracker.record('time', 3.0)
        tracker.increment('count', 5)
        
        summary = tracker.get_summary()
        
        assert summary['metrics']['time']['count'] == 2
        assert summary['metrics']['time']['average'] == 2.0
        assert summary['metrics']['time']['min'] == 1.0
        assert summary['metrics']['time']['max'] == 3.0
        assert summary['counters']['count'] == 5
    
    def test_clear(self):
        """Test clearing tracker."""
        tracker = PerformanceTracker()
        
        tracker.record('time', 1.0)
        tracker.increment('count')
        
        tracker.clear()
        
        assert len(tracker.metrics) == 0
        assert len(tracker.counters) == 0