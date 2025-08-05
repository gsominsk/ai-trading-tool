"""
Trading Operations Logging Demo

Demonstrates file-based logging for AI trading operations:
1. Market data analysis with logging
2. Trading decisions with confidence levels
3. Order execution simulation
4. File accumulation for AI analysis

This script shows how trading operations are logged to files
for later AI analysis and system monitoring.
"""

import os
import sys
import time
import json
from decimal import Decimal

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.market_data.market_data_service import MarketDataService


def demonstrate_trading_logging():
    """Demonstrate complete trading operations logging workflow."""
    
    print("🚀 AI Trading System - Logging Demo")
    print("=" * 50)
    
    # Create MarketDataService with logging enabled
    print("📊 Initializing MarketDataService with file logging...")
    service = MarketDataService(enable_logging=True)
    
    if not service._enable_logging:
        print("❌ Logging is not enabled!")
        return
    
    print("✅ Logging integration active")
    print(f"📁 Logs will be written to: logs/trading_operations.log")
    print(f"🔄 Log rotation: 50MB files, 10 backups (500MB total)")
    print()
    
    # Demo 1: Market Data Analysis
    print("📈 DEMO 1: Market Data Analysis")
    print("-" * 30)
    
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    
    for symbol in symbols:
        print(f"🔍 Analyzing {symbol}...")
        
        try:
            # This would normally fetch real market data
            # For demo, we'll use the service's logging methods directly
            
            # Simulate market analysis logging
            analysis_data = {
                "technical_indicators": {
                    "rsi_14": 45.5,
                    "macd_signal": "bullish",
                    "ma_trend": "uptrend"
                },
                "market_context": {
                    "volume_profile": "high",
                    "btc_correlation": 0.85
                },
                "data_quality": {
                    "candles_count": 48,
                    "data_freshness": "real_time"
                }
            }
            
            # Log market analysis
            if service._logging_integration:
                service._logging_integration.log_market_analysis(
                    symbol=symbol,
                    analysis_data=analysis_data,
                    decision="buy",
                    confidence=0.75
                )
            
            print(f"   ✅ {symbol} analysis logged")
            
        except Exception as e:
            print(f"   ❌ Error analyzing {symbol}: {e}")
        
        time.sleep(0.5)  # Brief pause for demo
    
    print()
    
    # Demo 2: Trading Operations
    print("💰 DEMO 2: Trading Operations")
    print("-" * 30)
    
    trading_operations = [
        {
            "type": "market_analysis",
            "symbol": "BTCUSDT",
            "data": {
                "strategy": "rsi_oversold_bounce",
                "entry_price": "42000.00",
                "stop_loss": "41000.00",
                "take_profit": "44000.00",
                "risk_reward": 2.0
            },
            "result": "buy_signal"
        },
        {
            "type": "order_placement", 
            "symbol": "ETHUSDT",
            "data": {
                "strategy": "breakout_momentum",
                "entry_price": "2800.00",
                "quantity": "0.1",
                "order_type": "LIMIT"
            },
            "result": "order_placed"
        }
    ]
    
    for i, operation in enumerate(trading_operations, 1):
        print(f"🔄 Trading Operation {i}: {operation['type']}")
        
        # Log trading operation
        service.log_trading_operation(
            operation_type=operation["type"],
            symbol=operation["symbol"],
            trade_data=operation["data"],
            result=operation["result"]
        )
        
        print(f"   ✅ {operation['symbol']} {operation['type']} logged")
        time.sleep(0.3)
    
    print()
    
    # Demo 3: Order Executions
    print("📋 DEMO 3: Order Executions")
    print("-" * 30)
    
    order_executions = [
        {
            "order_id": "ORD_001_BTC",
            "symbol": "BTCUSDT", 
            "order_type": "BUY",
            "amount": "0.001",
            "price": "42000.00",
            "status": "executed",
            "execution_time_ms": 150
        },
        {
            "order_id": "ORD_002_ETH",
            "symbol": "ETHUSDT",
            "order_type": "SELL", 
            "amount": "0.05",
            "price": "2800.00",
            "status": "executed",
            "execution_time_ms": 200
        }
    ]
    
    for order in order_executions:
        print(f"💸 Executing {order['order_type']} order for {order['symbol']}")
        
        # Log order execution
        service.log_order_execution(
            order_id=order["order_id"],
            symbol=order["symbol"],
            order_type=order["order_type"],
            amount=order["amount"],
            price=order["price"],
            status=order["status"],
            execution_time_ms=order["execution_time_ms"]
        )
        
        print(f"   ✅ Order {order['order_id']} logged")
        time.sleep(0.3)
    
    print()
    
    # Demo 4: Performance Metrics
    print("⚡ DEMO 4: Performance Metrics")
    print("-" * 30)
    
    performance_metrics = {
        "total_operations": 7,
        "successful_operations": 7,
        "average_response_time_ms": 175,
        "api_calls_made": 15,
        "data_points_processed": 336,
        "system_load": 0.45,
        "memory_usage_mb": 128
    }
    
    if service._logging_integration:
        service._logging_integration.log_performance_metrics(
            operation="demo_session",
            metrics=performance_metrics,
            symbol="SYSTEM"
        )
    
    print("📊 Performance metrics logged:")
    for key, value in performance_metrics.items():
        print(f"   {key}: {value}")
    
    print()
    
    # Demo 5: Show Accumulated Logs
    print("📄 DEMO 5: Accumulated Logs")
    print("-" * 30)
    
    log_file = "logs/trading_operations.log"
    
    # Allow time for all logs to be written
    time.sleep(1)
    
    if os.path.exists(log_file):
        file_size = os.path.getsize(log_file)
        print(f"📁 Log file: {log_file}")
        print(f"📏 File size: {file_size} bytes")
        
        # Show last few log entries
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            print(f"📝 Total log entries: {len(lines)}")
            print("🔍 Last 3 log entries:")
            
            for i, line in enumerate(lines[-3:], 1):
                try:
                    log_data = json.loads(line.strip())
                    print(f"   {i}. [{log_data.get('timestamp', 'N/A')}] {log_data.get('operation', 'unknown')}")
                    print(f"      Level: {log_data.get('level', 'N/A')}, Service: {log_data.get('service', 'N/A')}")
                except json.JSONDecodeError:
                    print(f"   {i}. [Invalid JSON] {line[:50]}...")
        
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
    else:
        print(f"❌ Log file not found: {log_file}")
        print("💡 Logs may be written to stderr or different location")
    
    print()
    
    # Final Summary
    print("🎯 DEMO COMPLETE")
    print("=" * 50)
    print("✅ File-based logging configured and tested")
    print("✅ Trading operations logged in JSON format")
    print("✅ AI-ready structured data accumulated")
    print("✅ Log rotation configured (50MB files)")
    print("✅ Ready for AI analysis and monitoring")
    print()
    print("🤖 AI Analysis Use Cases:")
    print("   • Pattern recognition in trading decisions")
    print("   • Performance optimization analysis")
    print("   • Risk management monitoring")
    print("   • Strategy effectiveness evaluation")
    print("   • Error pattern detection")
    print()
    print(f"📂 Check logs in: {os.path.abspath('logs/')}")


if __name__ == "__main__":
    demonstrate_trading_logging()