"""
TASK 1.3: Fix Mock Data Consistency Between Symbols
===================================================

PRIORITY: CRITICAL
PHASE: 1 - Demo Script Fixes

PROBLEM CONTEXT:
---------------
Demo logs show data leakage between symbols:
- logs/ai_trading_20250806.log line 48: BTC request returns ETH data
- BTC price shown as 3800.00 USD (this is ETH price, not BTC)
- Content-length=139 bytes (ETH response size) for BTC request
- Same candle data returned for different symbols

ROOT CAUSE:
----------
Shared mock state in create_realistic_binance_response():
- Mock objects reuse same timestamp/data between symbols
- Symbol-specific data not properly isolated
- Candle data generation uses shared variables

CURRENT PROBLEMATIC PATTERN:
----------------------------
File: examples/phase6_final_demo.py, lines ~147-162
```python
candle_data = [
    [
        int(time.time() * 1000) - 3600000,  # Shared timestamp!
        f"{open_price:.2f}",                 
        f"{high_price:.2f}",                 
        f"{low_price:.2f}",                  
        f"{close_price:.2f}",                
        f"{volume_base:.2f}",                
        int(time.time() * 1000) - 1,        # Shared timestamp!
        # ... rest uses shared state
    ]
]
```

SOLUTION:
---------
Add symbol-specific data isolation:

```python
def create_realistic_binance_response(self, symbol: str, response_time: float = 0.15, scenario: str = "normal"):
    # Add symbol-specific seed for deterministic but unique data
    symbol_seed = hash(symbol) % 1000
    base_timestamp = int(time.time() * 1000) + symbol_seed
    
    # Symbol-specific pricing with realistic spreads
    base_prices = {
        'BTCUSDT': 67500.00,
        'ETHUSDT': 3800.00, 
        'ADAUSDT': 0.485,
        'BNBUSDT': 635.00,
        'SOLUSDT': 155.00
    }
    
    base_price = base_prices.get(symbol, 50000)
    # Add symbol-specific price variation
    price_variation = (symbol_seed % 100) * 0.001  # 0-0.1% variation
    actual_price = base_price * (1 + price_variation)
    
    candle_data = [
        [
            base_timestamp - 3600000,           # Symbol-specific timestamp
            f"{actual_price:.8f}",              # Symbol-specific price
            f"{actual_price * 1.002:.8f}",      # Symbol-specific high
            f"{actual_price * 0.998:.8f}",      # Symbol-specific low  
            f"{actual_price * 1.001:.8f}",      # Symbol-specific close
            f"{volume_base:.2f}",               # Symbol-specific volume
            base_timestamp - 1,                 # Symbol-specific close time
            # ... rest with symbol-specific calculations
        ]
    ]
```

IMPLEMENTATION STEPS:
--------------------
1. Open examples/phase6_final_demo.py
2. Modify create_realistic_binance_response() method
3. Add symbol-specific timestamp generation
4. Add symbol-specific price calculation with realistic variation
5. Add symbol-specific volume patterns
6. Ensure content-length reflects actual symbol data size
7. Test data isolation between symbols

FILES TO MODIFY:
----------------
- examples/phase6_final_demo.py (create_realistic_binance_response method, lines ~104-167)

DETAILED IMPLEMENTATION:
-----------------------
1. Add symbol seed generation:
```python
symbol_seed = hash(symbol) % 1000  # Deterministic but unique per symbol
```

2. Update timestamp generation:
```python
base_timestamp = int(time.time() * 1000) + symbol_seed
```

3. Add realistic price variation per symbol:
```python
price_variation = (symbol_seed % 100) * 0.001  # 0-0.1% 
actual_price = base_price * (1 + price_variation)
```

4. Update volume calculation with symbol-specific patterns:
```python
volume_patterns = {
    'BTCUSDT': 1250.5,
    'ETHUSDT': 8500.2, 
    'ADAUSDT': 125000.0,
    'BNBUSDT': 850.0,
    'SOLUSDT': 2100.0
}
volume_base = volume_patterns.get(symbol, 5000.0)
volume_variation = (symbol_seed % 50) * 0.01  # 0-0.5% variation
actual_volume = volume_base * (1 + volume_variation)
```

5. Update content-length to reflect actual data:
```python
mock_response.content = json.dumps(candle_data).encode()
actual_content_length = len(mock_response.content)
mock_response.headers['content-length'] = str(actual_content_length)
```

VALIDATION:
-----------
After fix, verify in demo logs:
- Each symbol returns symbol-specific price data
- No cross-symbol data contamination
- Content-length matches actual response size
- Timestamps are unique per symbol
- Volume patterns reflect symbol characteristics

RELATED ISSUES:
---------------
- UUID uniqueness (Task 1.2)
- Performance metrics timing (Task 1.1)
- Mock framework standardization (Task 2.1)

SUCCESS CRITERIA:
-----------------
✅ Each symbol returns unique, realistic data
✅ No cross-symbol data leakage
✅ Content-length matches actual response size
✅ Price/volume patterns reflect real market characteristics
✅ Timestamps are unique and deterministic per symbol
"""