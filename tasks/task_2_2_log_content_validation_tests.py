"""
TASK 2.2: Log Content Validation Tests
======================================

PRIORITY: HIGH
PHASE: 2 - Testing Architecture Enhancement

PROBLEM CONTEXT:
---------------
Current tests validate code execution but not log content quality:
- Tests check if logging methods are called
- Tests don't parse actual log output
- Tests miss data quality issues (negative performance, UUID collisions)
- No validation of JSON log structure or field values

Example from test_trace_id_integration.py:
```python
# Current weak assertion - only checks if method was called
self.mock_logger.info.assert_called()

# Missing: What was actually logged? Is the data correct?
```

ROOT CAUSE:
----------
Tests focus on method invocation rather than output validation:
- No log content parsing in test assertions
- Missing JSON structure validation
- No field-level data quality checks
- No log correlation validation between operations

SOLUTION:
---------
Implement comprehensive log content validation framework:

1. **Log Content Parser** - Parse actual log output
2. **JSON Structure Validator** - Validate log JSON schema
3. **Field-Level Assertions** - Check specific field values
4. **Log Correlation Validator** - Validate trace_id relationships

IMPLEMENTATION PLAN:
-------------------

### Step 1: Create Log Content Validation Framework
File: tests/utils/log_validator.py

```python
"""
Log Content Validation Framework
Provides comprehensive validation of actual log output content.
"""
import json
import re
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import uuid


class LogContentValidator:
    """Validates actual log content for data quality and consistency."""
    
    def __init__(self):
        self.required_fields = {
            'INFO': ['timestamp', 'level', 'message', 'trace_id'],
            'DEBUG': ['timestamp', 'level', 'message', 'trace_id', 'raw_data'],
            'ERROR': ['timestamp', 'level', 'message', 'trace_id', 'error_details']
        }
        
    def parse_log_line(self, log_line: str) -> Optional[Dict[str, Any]]:
        """Parse a single log line into structured data."""
        try:
            # Handle different log formats
            if log_line.startswith('['):
                # JSON-like format: [2025-01-06 12:34:56] INFO - {...}
                parts = log_line.split(' - ', 1)
                if len(parts) != 2:
                    return None
                    
                header = parts[0]
                content = parts[1]
                
                # Extract timestamp and level
                timestamp_match = re.search(r'\[([^\]]+)\]', header)
                level_match = re.search(r'(INFO|DEBUG|ERROR|WARNING)', header)
                
                if not timestamp_match or not level_match:
                    return None
                    
                timestamp_str = timestamp_match.group(1)
                level = level_match.group(1)
                
                # Parse JSON content
                try:
                    json_content = json.loads(content)
                except json.JSONDecodeError:
                    # Handle non-JSON messages
                    json_content = {'message': content}
                    
                return {
                    'timestamp': timestamp_str,
                    'level': level,
                    'raw_content': content,
                    **json_content
                }
            else:
                # Direct JSON format
                return json.loads(log_line)
                
        except Exception as e:
            return {'parse_error': str(e), 'raw_line': log_line}
            
    def validate_log_structure(self, parsed_log: Dict[str, Any]) -> Dict[str, Any]:
        """Validate log entry structure and required fields."""
        issues = []
        
        if 'parse_error' in parsed_log:
            return {
                'valid': False,
                'issues': [f"Parse error: {parsed_log['parse_error']}"],
                'parsed_log': parsed_log
            }
            
        level = parsed_log.get('level', 'UNKNOWN')
        required = self.required_fields.get(level, self.required_fields['INFO'])
        
        # Check required fields
        for field in required:
            if field not in parsed_log:
                issues.append(f"Missing required field: {field}")
            elif parsed_log[field] is None:
                issues.append(f"Required field is None: {field}")
                
        # Validate timestamp format
        if 'timestamp' in parsed_log:
            try:
                # Try multiple timestamp formats
                timestamp_str = parsed_log['timestamp']
                if not self._validate_timestamp_format(timestamp_str):
                    issues.append(f"Invalid timestamp format: {timestamp_str}")
            except Exception as e:
                issues.append(f"Timestamp validation error: {e}")
                
        # Validate trace_id format
        if 'trace_id' in parsed_log:
            trace_id = parsed_log['trace_id']
            if not self._validate_trace_id_format(trace_id):
                issues.append(f"Invalid trace_id format: {trace_id}")
                
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'level': level,
            'parsed_log': parsed_log
        }
        
    def validate_performance_metrics(self, parsed_log: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance metrics in log entry."""
        issues = []
        
        # Check for performance-related fields
        perf_fields = ['response_time', 'api_latency', 'processing_time', 'duration']
        
        for field in perf_fields:
            if field in parsed_log:
                value = parsed_log[field]
                try:
                    numeric_value = float(value)
                    if numeric_value < 0:
                        issues.append(f"Negative performance metric {field}: {numeric_value}")
                    elif numeric_value > 10.0:  # More than 10 seconds
                        issues.append(f"Unrealistic performance metric {field}: {numeric_value}")
                except (ValueError, TypeError):
                    issues.append(f"Non-numeric performance metric {field}: {value}")
                    
        # Check message content for performance data
        message = parsed_log.get('message', '')
        if 'response_time' in message:
            # Extract performance values from message
            time_matches = re.findall(r'(\d+\.?\d*)ms', message)
            for match in time_matches:
                try:
                    ms_value = float(match)
                    if ms_value < 0:
                        issues.append(f"Negative millisecond value in message: {ms_value}ms")
                except ValueError:
                    pass
                    
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'metrics_found': len([f for f in perf_fields if f in parsed_log])
        }
        
    def validate_uuid_uniqueness(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate UUID uniqueness across log entries."""
        trace_ids = []
        symbol_trace_mapping = {}
        issues = []
        
        for entry in log_entries:
            if 'trace_id' in entry:
                trace_id = entry['trace_id']
                trace_ids.append(trace_id)
                
                # Extract symbol if present
                symbol = None
                if 'symbol' in entry:
                    symbol = entry['symbol']
                elif 'message' in entry:
                    symbol_match = re.search(r'symbol["\']?\s*:\s*["\']?([A-Z]+)["\']?', entry['message'])
                    if symbol_match:
                        symbol = symbol_match.group(1)
                        
                if symbol:
                    if symbol not in symbol_trace_mapping:
                        symbol_trace_mapping[symbol] = []
                    symbol_trace_mapping[symbol].append(trace_id)
                    
        # Check for duplicate trace_ids
        seen_traces = set()
        duplicates = []
        for trace_id in trace_ids:
            if trace_id in seen_traces:
                duplicates.append(trace_id)
            seen_traces.add(trace_id)
            
        if duplicates:
            issues.append(f"Duplicate trace_ids found: {duplicates}")
            
        # Check for cross-symbol trace_id collisions
        for symbol, traces in symbol_trace_mapping.items():
            unique_traces = set(traces)
            if len(traces) != len(unique_traces):
                issues.append(f"Symbol {symbol} has duplicate trace_ids: {traces}")
                
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'total_traces': len(trace_ids),
            'unique_traces': len(seen_traces),
            'symbols_analyzed': len(symbol_trace_mapping),
            'symbol_trace_mapping': symbol_trace_mapping
        }
        
    def validate_data_consistency(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate data consistency across log entries."""
        issues = []
        symbol_data = {}
        
        for entry in log_entries:
            # Extract symbol and price data
            symbol = self._extract_symbol(entry)
            price_data = self._extract_price_data(entry)
            
            if symbol and price_data:
                if symbol not in symbol_data:
                    symbol_data[symbol] = []
                symbol_data[symbol].append(price_data)
                
        # Validate symbol-specific data consistency
        for symbol, prices in symbol_data.items():
            if len(prices) > 1:
                # Check for cross-contamination
                unique_prices = set(prices)
                if len(unique_prices) == 1 and len(prices) > 1:
                    # All prices are identical - potential cross-contamination
                    issues.append(f"Symbol {symbol} has identical prices across multiple entries: {prices[0]}")
                    
                # Check price realism
                expected_ranges = {
                    'BTCUSDT': (60000, 75000),
                    'ETHUSDT': (3000, 4500),
                    'ADAUSDT': (0.3, 0.7),
                    'BNBUSDT': (500, 800),
                    'SOLUSDT': (100, 200)
                }
                
                if symbol in expected_ranges:
                    min_price, max_price = expected_ranges[symbol]
                    for price in prices:
                        if not (min_price <= price <= max_price):
                            issues.append(f"Symbol {symbol} price {price} outside expected range {expected_ranges[symbol]}")
                            
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'symbols_analyzed': len(symbol_data),
            'total_price_entries': sum(len(prices) for prices in symbol_data.values())
        }
        
    def _validate_timestamp_format(self, timestamp_str: str) -> bool:
        """Validate timestamp format."""
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ'
        ]
        
        for fmt in formats:
            try:
                datetime.strptime(timestamp_str, fmt)
                return True
            except ValueError:
                continue
        return False
        
    def _validate_trace_id_format(self, trace_id: str) -> bool:
        """Validate trace_id format."""
        # Check if it's a valid UUID format
        try:
            uuid.UUID(trace_id)
            return True
        except ValueError:
            pass
            
        # Check if it's a custom format (e.g., SYMBOL-operation-counter)
        if re.match(r'^[A-Z]+-\w+-\d+$', trace_id):
            return True
            
        return False
        
    def _extract_symbol(self, entry: Dict[str, Any]) -> Optional[str]:
        """Extract symbol from log entry."""
        if 'symbol' in entry:
            return entry['symbol']
            
        message = entry.get('message', '')
        symbol_match = re.search(r'symbol["\']?\s*:\s*["\']?([A-Z]+)["\']?', message)
        if symbol_match:
            return symbol_match.group(1)
            
        return None
        
    def _extract_price_data(self, entry: Dict[str, Any]) -> Optional[float]:
        """Extract price data from log entry."""
        # Check direct price fields
        if 'price' in entry:
            try:
                return float(entry['price'])
            except (ValueError, TypeError):
                pass
                
        # Check message content
        message = entry.get('message', '')
        price_match = re.search(r'price["\']?\s*:\s*["\']?([0-9]+\.?[0-9]*)', message)
        if price_match:
            try:
                return float(price_match.group(1))
            except ValueError:
                pass
                
        return None


# Global validator instance
log_validator = LogContentValidator()
```

### Step 2: Create Enhanced Test Assertions
File: tests/utils/enhanced_assertions.py

```python
"""
Enhanced Test Assertions for Log Content Validation
Provides rich assertions for log content testing.
"""
import unittest
from typing import List, Dict, Any, Optional
from .log_validator import log_validator


class LogAssertionMixin:
    """Mixin class providing enhanced log content assertions."""
    
    def assertLogStructureValid(self, log_entries: List[str], msg: Optional[str] = None):
        """Assert that all log entries have valid structure."""
        issues = []
        
        for i, log_line in enumerate(log_entries):
            parsed = log_validator.parse_log_line(log_line)
            validation = log_validator.validate_log_structure(parsed)
            
            if not validation['valid']:
                issues.extend([f"Entry {i}: {issue}" for issue in validation['issues']])
                
        if issues:
            error_msg = f"Log structure validation failed:\n" + "\n".join(issues)
            if msg:
                error_msg = f"{msg}\n{error_msg}"
            raise AssertionError(error_msg)
            
    def assertPerformanceMetricsValid(self, log_entries: List[str], msg: Optional[str] = None):
        """Assert that performance metrics in logs are valid."""
        issues = []
        
        for i, log_line in enumerate(log_entries):
            parsed = log_validator.parse_log_line(log_line)
            if parsed:
                validation = log_validator.validate_performance_metrics(parsed)
                
                if not validation['valid']:
                    issues.extend([f"Entry {i}: {issue}" for issue in validation['issues']])
                    
        if issues:
            error_msg = f"Performance metrics validation failed:\n" + "\n".join(issues)
            if msg:
                error_msg = f"{msg}\n{error_msg}"
            raise AssertionError(error_msg)
            
    def assertUuidUniqueness(self, log_entries: List[str], msg: Optional[str] = None):
        """Assert that UUIDs are unique across log entries."""
        parsed_entries = []
        for log_line in log_entries:
            parsed = log_validator.parse_log_line(log_line)
            if parsed:
                parsed_entries.append(parsed)
                
        validation = log_validator.validate_uuid_uniqueness(parsed_entries)
        
        if not validation['valid']:
            error_msg = f"UUID uniqueness validation failed:\n" + "\n".join(validation['issues'])
            if msg:
                error_msg = f"{msg}\n{error_msg}"
            raise AssertionError(error_msg)
            
    def assertDataConsistency(self, log_entries: List[str], msg: Optional[str] = None):
        """Assert that data is consistent across log entries."""
        parsed_entries = []
        for log_line in log_entries:
            parsed = log_validator.parse_log_line(log_line)
            if parsed:
                parsed_entries.append(parsed)
                
        validation = log_validator.validate_data_consistency(parsed_entries)
        
        if not validation['valid']:
            error_msg = f"Data consistency validation failed:\n" + "\n".join(validation['issues'])
            if msg:
                error_msg = f"{msg}\n{error_msg}"
            raise AssertionError(error_msg)
            
    def assertLogContainsFields(self, log_entry: str, required_fields: List[str], msg: Optional[str] = None):
        """Assert that log entry contains required fields."""
        parsed = log_validator.parse_log_line(log_entry)
        if not parsed:
            raise AssertionError(f"Could not parse log entry: {log_entry}")
            
        missing_fields = [field for field in required_fields if field not in parsed]
        
        if missing_fields:
            error_msg = f"Log entry missing required fields: {missing_fields}"
            if msg:
                error_msg = f"{msg}\n{error_msg}"
            raise AssertionError(error_msg)
            
    def assertLogFieldValue(self, log_entry: str, field: str, expected_value: Any, msg: Optional[str] = None):
        """Assert that log entry field has expected value."""
        parsed = log_validator.parse_log_line(log_entry)
        if not parsed:
            raise AssertionError(f"Could not parse log entry: {log_entry}")
            
        if field not in parsed:
            raise AssertionError(f"Field {field} not found in log entry")
            
        actual_value = parsed[field]
        if actual_value != expected_value:
            error_msg = f"Field {field}: expected {expected_value}, got {actual_value}"
            if msg:
                error_msg = f"{msg}\n{error_msg}"
            raise AssertionError(error_msg)


class EnhancedLogTestCase(unittest.TestCase, LogAssertionMixin):
    """Test case class with enhanced log content assertions."""
    pass
```

### Step 3: Update Test Files with Log Content Validation

**Update Priority:**
1. tests/unit/logging/test_trace_id_integration.py
2. tests/unit/logging/test_raw_data_logging.py
3. tests/integration/logging/test_trace_architecture_integration.py

**Conversion Example:**
```python
# Before:
class TestTraceIdIntegration(unittest.TestCase):
    def test_trace_id_generation(self):
        # ... setup ...
        self.mock_logger.info.assert_called()

# After:
from tests.utils.enhanced_assertions import EnhancedLogTestCase

class TestTraceIdIntegration(EnhancedLogTestCase):
    def test_trace_id_generation(self):
        # ... setup with actual log capture ...
        log_entries = self.capture_log_output()
        
        # Validate log structure
        self.assertLogStructureValid(log_entries)
        
        # Validate UUID uniqueness
        self.assertUuidUniqueness(log_entries)
        
        # Validate performance metrics
        self.assertPerformanceMetricsValid(log_entries)
        
        # Validate specific field values
        self.assertLogContainsFields(log_entries[0], ['timestamp', 'trace_id', 'symbol'])
```

FILES TO CREATE/MODIFY:
----------------------
**New Files:**
- tests/utils/log_validator.py
- tests/utils/enhanced_assertions.py

**Files to Update:**
- tests/unit/logging/test_trace_id_integration.py
- tests/unit/logging/test_raw_data_logging.py
- tests/integration/logging/test_trace_architecture_integration.py
- tests/unit/test_market_data_service.py

VALIDATION CRITERIA:
-------------------
✅ Log content parsing framework implemented
✅ JSON structure validation working
✅ Performance metrics validation catches negative values
✅ UUID uniqueness validation catches collisions
✅ Data consistency validation catches cross-contamination
✅ Enhanced assertions integrate with existing test framework

DEPENDENCIES:
------------
- Should complete after Task 2.1 (Mock Framework Standardization)
- Enables Task 2.3 (Enhanced Assertion Architecture)
- Required for Task 4.1 (Integration Scenario Tests)

SUCCESS CRITERIA:
-----------------
✅ Tests validate actual log content, not just method calls
✅ Log content validation catches issues found in demo analysis
✅ Enhanced assertions provide clear failure messages
✅ All existing tests still pass with new validation
✅ New validation framework prevents regression of log quality issues
"""