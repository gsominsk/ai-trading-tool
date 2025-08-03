"""
MarketDataService - Multi-timeframe cryptocurrency market data aggregation.

Provides structured market data for LLM trading decisions with three data levels:
- Level 1: 6 months daily candles (global trend analysis)
- Level 2: 2 weeks 4H candles (medium-term patterns)
- Level 3: 48 hours 1H candles (short-term signals)

Includes technical indicators and market context for comprehensive analysis.
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, NamedTuple
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import time
import json
import os


@dataclass
class MarketDataSet:
    """Standardized market data structure for LLM analysis."""
    symbol: str
    timestamp: datetime
    
    # Multi-level price data
    daily_candles: pd.DataFrame      # 6 months daily (Level 1)
    h4_candles: pd.DataFrame         # 2 weeks 4H (Level 2)
    h1_candles: pd.DataFrame         # 48 hours 1H (Level 3)
    
    # Technical indicators (using Decimal for financial precision)
    rsi_14: Decimal
    macd_signal: str  # "bullish", "bearish", "neutral"
    ma_20: Decimal
    ma_50: Decimal
    ma_trend: str     # "uptrend", "downtrend", "sideways"
    
    # Market context
    btc_correlation: Optional[Decimal] = None
    fear_greed_index: Optional[int] = None
    volume_profile: str = "normal"  # "high", "low", "normal"
    
    # Enhanced analysis data (no state pollution)
    support_level: Optional[Decimal] = None
    resistance_level: Optional[Decimal] = None
    
    def __post_init__(self):
        """Validate data after initialization."""
        self._validate_symbol()
        self._validate_technical_indicators()
    
    def _validate_symbol(self):
        """Validate symbol format."""
        if not self.symbol or not isinstance(self.symbol, str):
            raise ValueError("Symbol must be a non-empty string")
        if not self.symbol.endswith("USDT") or len(self.symbol) < 6:
            raise ValueError(f"Invalid symbol format: {self.symbol}. Expected XXXUSDT")
    
    def _validate_technical_indicators(self):
        """Validate technical indicator values."""
        if not (Decimal('0') <= self.rsi_14 <= Decimal('100')):
            raise ValueError(f"RSI must be between 0 and 100, got: {self.rsi_14}")
        if self.macd_signal not in ["bullish", "bearish", "neutral"]:
            raise ValueError(f"Invalid MACD signal: {self.macd_signal}")
        if self.ma_trend not in ["uptrend", "downtrend", "sideways"]:
            raise ValueError(f"Invalid MA trend: {self.ma_trend}")
    
    def to_llm_context(self, include_candlesticks: bool = False) -> str:
        """Convert to structured text format for LLM consumption.
        
        Args:
            include_candlesticks: If True, includes key candlestick analysis
        """
        if include_candlesticks:
            return self.to_llm_context_enhanced()
        else:
            return self.to_llm_context_basic()
    
    def to_llm_context_basic(self) -> str:
        """Convert to structured text format for LLM consumption."""
        # Check for empty DataFrames first
        if len(self.h1_candles) == 0:
            return f"""
MARKET DATA ANALYSIS FOR {self.symbol}
Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

⚠️ NO MARKET DATA AVAILABLE
Status: Insufficient data for analysis
Reason: Empty price data (h1_candles)

=== TECHNICAL INDICATORS ===
RSI(14): {self.rsi_14:.2f} - {'Oversold' if self.rsi_14 < Decimal('30') else 'Overbought' if self.rsi_14 > Decimal('70') else 'Neutral'}
MACD: {self.macd_signal.upper()}
MA(20): ${'N/A' if self.ma_20 is None else f'{self.ma_20:.2f}'}
MA(50): ${'N/A' if self.ma_50 is None else f'{self.ma_50:.2f}'}
Moving Average Trend: {self.ma_trend.upper()}
"""
        
        try:
            current_price = Decimal(str(self.h1_candles.iloc[-1]['close']))
            change_24h = self._calculate_24h_change()
            volume_24h = Decimal(str(self.h1_candles['volume'].tail(24).sum()))
            
            # Safe format values with Decimal precision
            ma_20_str = f"${self.ma_20:.2f}" if self.ma_20 is not None else "N/A"
            ma_50_str = f"${self.ma_50:.2f}" if self.ma_50 is not None else "N/A"
            btc_corr_str = f"{self.btc_correlation:.3f}" if self.btc_correlation is not None else "N/A"
            
            return f"""
MARKET DATA ANALYSIS FOR {self.symbol}
Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

=== TECHNICAL INDICATORS ===
RSI(14): {self.rsi_14:.2f} - {'Oversold' if self.rsi_14 < Decimal('30') else 'Overbought' if self.rsi_14 > Decimal('70') else 'Neutral'}
MACD: {self.macd_signal.upper()}
MA(20): {ma_20_str}
MA(50): {ma_50_str}
Moving Average Trend: {self.ma_trend.upper()}

=== MARKET CONTEXT ===
BTC Correlation: {btc_corr_str}
Volume Profile: {self.volume_profile.upper()}

=== RECENT PRICE ACTION ===
Current Price: ${current_price:.2f}
24H Change: {change_24h:.2f}%
24H Volume: {volume_24h:.0f}
"""
        except Exception as e:
            return f"""
MARKET DATA ANALYSIS FOR {self.symbol}
Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

❌ DATA ACCESS ERROR
Error: {str(e)}
Status: Unable to access price data for context generation

=== AVAILABLE TECHNICAL INDICATORS ===
RSI(14): {self.rsi_14:.2f}
MACD: {self.macd_signal.upper()}
MA Trend: {self.ma_trend.upper()}
"""
    
    def to_llm_context_enhanced(self) -> str:
        """Convert to enhanced format with candlestick analysis (~300-400 tokens)."""
        basic_context = self.to_llm_context_basic()
        # Note: Enhanced analysis requires MarketDataService instance access
        # This would typically be called through the service's get_enhanced_context method
        return f"{basic_context}\n\nCANDLESTICK ANALYSIS: Enhanced analysis available via service method"
    
    def _analyze_trend(self, df: pd.DataFrame) -> str:
        """Analyze trend direction from price data."""
        if len(df) < 2:
            return "insufficient_data"
        
        start_price = df.iloc[0]['close']
        end_price = df.iloc[-1]['close']
        change_pct = ((end_price - start_price) / start_price) * 100
        
        if change_pct > 5:
            return f"BULLISH (+{change_pct:.1f}%)"
        elif change_pct < -5:
            return f"BEARISH ({change_pct:.1f}%)"
        else:
            return f"SIDEWAYS ({change_pct:.1f}%)"
    
    def _calculate_24h_change(self) -> Decimal:
        """Calculate 24-hour price change percentage."""
        if len(self.h1_candles) < 24:
            return Decimal('0.0')
        
        price_24h_ago = Decimal(str(self.h1_candles.iloc[-24]['close']))
        current_price = Decimal(str(self.h1_candles.iloc[-1]['close']))
        return ((current_price - price_24h_ago) / price_24h_ago) * Decimal('100')


class MarketDataService:
    """Service for aggregating multi-timeframe cryptocurrency market data."""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        self.base_url = "https://api.binance.com/api/v3"
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist."""
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_market_data(self, symbol: str) -> MarketDataSet:
        """
        Get complete multi-timeframe market data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            MarketDataSet with all timeframes and indicators
        """
        # Validate input parameters
        self._validate_symbol_input(symbol)
        
        try:
            # Fetch multi-timeframe data
            daily_data = self._get_klines(symbol, "1d", 180)  # 6 months
            h4_data = self._get_klines(symbol, "4h", 84)      # 2 weeks
            h1_data = self._get_klines(symbol, "1h", 48)      # 48 hours
            
            # Calculate support/resistance levels (no state pollution)
            support_level = Decimal(str(daily_data['low'].tail(30).min()))
            resistance_level = Decimal(str(daily_data['high'].tail(30).max()))
            
            # Calculate technical indicators
            rsi = self._calculate_rsi(h1_data, 14)
            macd_signal = self._calculate_macd_signal(h1_data)
            ma_20 = self._calculate_ma(h1_data, 20)
            ma_50 = self._calculate_ma(h1_data, 50)
            ma_trend = self._determine_ma_trend(ma_20, ma_50)
            
            # Get market context
            btc_correlation = self._calculate_btc_correlation(symbol, h1_data) if symbol != "BTCUSDT" else None
            volume_profile = self._analyze_volume_profile(h1_data)
            
            return MarketDataSet(
                symbol=symbol,
                timestamp=datetime.utcnow(),
                daily_candles=daily_data,
                h4_candles=h4_data,
                h1_candles=h1_data,
                rsi_14=rsi,
                macd_signal=macd_signal,
                ma_20=ma_20,
                ma_50=ma_50,
                ma_trend=ma_trend,
                btc_correlation=btc_correlation,
                volume_profile=volume_profile,
                support_level=support_level,
                resistance_level=resistance_level
            )
            
        except Exception as e:
            raise Exception(f"Failed to get market data for {symbol}: {str(e)}")
    
    def _validate_symbol_input(self, symbol: str):
        """Validate symbol input before processing."""
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol must be a non-empty string")
        if not symbol.endswith("USDT") or len(symbol) < 6:
            raise ValueError(f"Invalid symbol format: {symbol}. Expected XXXUSDT format")
        if len(symbol) > 12:  # Reasonable length limit
            raise ValueError(f"Symbol too long: {symbol}")
        
        # Extract base currency by removing only the trailing USDT
        if symbol.count("USDT") > 1:
            raise ValueError(f"Invalid symbol format: {symbol}. Multiple USDT occurrences not allowed")
        
        base_currency = symbol[:-4]  # Remove last 4 characters (USDT)
        if not base_currency or not base_currency.isalpha() or not base_currency.isupper():
            raise ValueError(f"Invalid base currency: '{base_currency}'. Must be uppercase letters only")
        
        # Validate base currency length (cryptocurrency standards)
        if len(base_currency) < 3:
            raise ValueError(f"Base currency too short: '{base_currency}'. Must be at least 3 characters")
        if len(base_currency) > 5:
            raise ValueError(f"Base currency too long: '{base_currency}'. Must be 5 characters or less")
    
    def get_enhanced_context(self, symbol: str) -> str:
        """Get enhanced market context with candlestick analysis."""
        market_data = self.get_market_data(symbol)
        
        # Generate candlestick analysis using market_data (no state pollution)
        key_candles = self._select_key_candles(market_data.daily_candles.values.tolist())
        patterns = self._identify_patterns(key_candles)
        
        basic_context = market_data.to_llm_context_basic()
        
        # Enhanced candlestick analysis
        analysis = "\n=== CANDLESTICK ANALYSIS ===\n"
        
        # Recent candles trend
        recent_trend = self._analyze_recent_trend(key_candles[:5])
        analysis += f"Recent Trend: {recent_trend}\n"
        
        # Key patterns
        if patterns:
            analysis += f"Patterns: {', '.join(patterns)}\n"
        
        # Critical levels interaction
        sr_tests = self._analyze_sr_tests(key_candles, market_data.support_level, market_data.resistance_level)
        if sr_tests:
            analysis += f"S/R Tests: {sr_tests}\n"
        
        # Volume-price relationship
        volume_analysis = self._analyze_volume_relationship(key_candles)
        analysis += f"Volume Analysis: {volume_analysis}\n"
        
        # Key candlestick summary
        analysis += f"Key Candles Analyzed: {len(key_candles)} of {len(market_data.daily_candles)} total"
        
        return f"{basic_context}{analysis}"
    
    def _get_klines(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        """Fetch candlestick data from Binance API."""
        url = f"{self.base_url}/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        # Convert to proper types
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> Decimal:
        """Calculate RSI indicator with Decimal precision and division by zero protection."""
        if len(df) < period + 1:
            return Decimal('50.0')  # Default neutral RSI
        
        closes = df['close']
        delta = closes.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Get the final values
        final_gain = gain.iloc[-1]
        final_loss = loss.iloc[-1]
        
        # Handle division by zero cases
        if final_loss == 0:
            if final_gain == 0:
                # No price movement at all
                rsi_value = 50.0
            else:
                # Only gains, no losses (maximum RSI)
                rsi_value = 100.0
        elif final_gain == 0:
            # Only losses, no gains (minimum RSI)
            rsi_value = 0.0
        else:
            # Normal RSI calculation
            rs = final_gain / final_loss
            rsi_value = 100 - (100 / (1 + rs))
        
        # Convert to Decimal with proper precision
        return Decimal(str(rsi_value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def _calculate_macd_signal(self, df: pd.DataFrame) -> str:
        """Calculate MACD signal (bullish/bearish/neutral)."""
        if len(df) < 26:
            return "neutral"
        
        closes = df['close']
        ema_12 = closes.ewm(span=12).mean()
        ema_26 = closes.ewm(span=26).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9).mean()
        
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        
        if current_macd > current_signal:
            return "bullish"
        elif current_macd < current_signal:
            return "bearish"
        else:
            return "neutral"
    
    def _calculate_ma(self, df: pd.DataFrame, period: int) -> Decimal:
        """Calculate moving average with Decimal precision."""
        if len(df) < period:
            avg_value = float(df['close'].mean())
            return Decimal(str(avg_value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        ma_value = df['close'].rolling(window=period).mean().iloc[-1]
        if pd.notna(ma_value):
            return Decimal(str(float(ma_value))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            avg_value = float(df['close'].mean())
            return Decimal(str(avg_value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def _determine_ma_trend(self, ma_20: Decimal, ma_50: Decimal) -> str:
        """Determine trend based on moving averages."""
        if ma_20 is None or ma_50 is None:
            return "sideways"
        
        threshold_up = ma_50 * Decimal('1.02')  # 2% threshold
        threshold_down = ma_50 * Decimal('0.98')
        
        if ma_20 > threshold_up:
            return "uptrend"
        elif ma_20 < threshold_down:
            return "downtrend"
        else:
            return "sideways"
    
    def _calculate_btc_correlation(self, symbol: str, df: pd.DataFrame) -> Optional[Decimal]:
        """Calculate correlation with BTC (placeholder - would need BTC data)."""
        # For MVP, return a mock correlation
        # In production, would fetch BTC data and calculate actual correlation
        return Decimal('0.75')  # Mock positive correlation
    
    def _analyze_volume_profile(self, df: pd.DataFrame) -> str:
        """Analyze volume profile (high/normal/low)."""
        if len(df) < 24:
            return "normal"
        
        recent_volume = df['volume'].tail(24).mean()
        historical_volume = df['volume'].mean()
        
        ratio = recent_volume / historical_volume
        
        if ratio > 1.5:
            return "high"
        elif ratio < 0.5:
            return "low"
        else:
            return "normal"
    
    def _select_key_candles(self, daily_candles: list) -> list:
        """Select key candlesticks using 7-algorithm approach."""
        if not daily_candles or len(daily_candles) < 10:
            return []
        
        candles = daily_candles.copy()
        key_candles = []
        
        # 1. Recent 5 candles (most important for current context)
        recent_candles = candles[-5:]
        key_candles.extend(recent_candles)
        
        # 2. Extreme candles (highest highs, lowest lows in last 30 days)
        if len(candles) >= 30:
            last_30 = candles[-30:]
            highest_high = max(last_30, key=lambda x: x[2])  # high price
            lowest_low = min(last_30, key=lambda x: x[3])    # low price
            key_candles.extend([highest_high, lowest_low])
        
        # 3. High volume candles (top 10% volume in last 20 days)
        if len(candles) >= 20:
            last_20 = candles[-20:]
            volumes = [float(c[5]) for c in last_20]  # volume
            volume_threshold = sorted(volumes, reverse=True)[int(len(volumes) * 0.1)]
            high_vol_candles = [c for c in last_20 if float(c[5]) >= volume_threshold]
            key_candles.extend(high_vol_candles[:3])  # Top 3 high volume
        
        # 4. Big moves (>3% daily change)
        big_move_candles = []
        for candle in candles[-20:]:  # Last 20 days
            open_price = Decimal(str(candle[1]))
            close_price = Decimal(str(candle[4]))
            change_pct = abs((close_price - open_price) / open_price * Decimal('100'))
            if change_pct > Decimal('3.0'):
                big_move_candles.append(candle)
        key_candles.extend(big_move_candles[-3:])  # Last 3 big moves
        
        # 5. Pattern candles (doji, hammer, shooting star)
        pattern_candles = self._find_pattern_candles(candles[-15:])
        key_candles.extend(pattern_candles)
        
        # 6. Support/Resistance test candles (skipped - requires support/resistance levels)
        # sr_test_candles = self._find_sr_test_candles(candles[-20:], support_level, resistance_level)
        # key_candles.extend(sr_test_candles)
        
        # 7. Remove duplicates and sort by timestamp
        unique_candles = []
        seen_timestamps = set()
        for candle in key_candles:
            timestamp = candle[0]
            if timestamp not in seen_timestamps:
                unique_candles.append(candle)
                seen_timestamps.add(timestamp)
        
        # Sort by timestamp and limit to reasonable number
        unique_candles.sort(key=lambda x: x[0])
        return unique_candles[-15:]  # Keep last 15 key candles
    
    def _find_pattern_candles(self, candles: list) -> list:
        """Identify candlestick patterns with Decimal precision."""
        pattern_candles = []
        
        for candle in candles:
            open_price = Decimal(str(candle[1]))
            high_price = Decimal(str(candle[2]))
            low_price = Decimal(str(candle[3]))
            close_price = Decimal(str(candle[4]))
            
            body = abs(close_price - open_price)
            upper_shadow = high_price - max(open_price, close_price)
            lower_shadow = min(open_price, close_price) - low_price
            total_range = high_price - low_price
            
            # Doji pattern (small body)
            if total_range > 0 and body / total_range < Decimal('0.1'):
                pattern_candles.append(candle)
            
            # Hammer/Shooting star (long shadow)
            elif total_range > 0:
                if lower_shadow / total_range > Decimal('0.6'):  # Hammer
                    pattern_candles.append(candle)
                elif upper_shadow / total_range > Decimal('0.6'):  # Shooting star
                    pattern_candles.append(candle)
        
        return pattern_candles
    
    def _find_sr_test_candles(self, candles: list, support_level: Decimal, resistance_level: Decimal) -> list:
        """Find candles that test support/resistance levels with Decimal precision."""
        sr_test_candles = []
        
        for candle in candles:
            high_price = Decimal(str(candle[2]))
            low_price = Decimal(str(candle[3]))
            
            # Test resistance level (within 1%)
            if abs(high_price - resistance_level) / resistance_level < Decimal('0.01'):
                sr_test_candles.append(candle)
            
            # Test support level (within 1%)
            elif abs(low_price - support_level) / support_level < Decimal('0.01'):
                sr_test_candles.append(candle)
        
        return sr_test_candles
    
    def _identify_patterns(self, candles: list) -> list:
        """Identify candlestick patterns in key candles with Decimal precision."""
        patterns = []
        
        for candle in candles:
            open_price = Decimal(str(candle[1]))
            high_price = Decimal(str(candle[2]))
            low_price = Decimal(str(candle[3]))
            close_price = Decimal(str(candle[4]))
            
            body = abs(close_price - open_price)
            upper_shadow = high_price - max(open_price, close_price)
            lower_shadow = min(open_price, close_price) - low_price
            total_range = high_price - low_price
            
            if total_range == 0:
                continue
                
            # Pattern identification with Decimal thresholds (specific patterns first)
            if lower_shadow / total_range > Decimal('0.6') and body / total_range < Decimal('0.3'):
                patterns.append("Hammer")
            elif upper_shadow / total_range > Decimal('0.6') and body / total_range < Decimal('0.3'):
                patterns.append("Shooting Star")
            elif body / total_range > Decimal('0.7'):
                if close_price > open_price:
                    patterns.append("Strong Bull")
                else:
                    patterns.append("Strong Bear")
            elif body / total_range < Decimal('0.1'):
                patterns.append("Doji")
        
        return list(set(patterns))  # Remove duplicates
    
    def _analyze_recent_trend(self, recent_candles: list) -> str:
        """Analyze trend from recent candles."""
        if len(recent_candles) < 3:
            return "Insufficient data"
        
        closes = [float(c[4]) for c in recent_candles]
        
        if closes[-1] > closes[-2] > closes[-3]:
            return "Strong Uptrend"
        elif closes[-1] < closes[-2] < closes[-3]:
            return "Strong Downtrend"
        elif closes[-1] > closes[-3]:
            return "Upward bias"
        elif closes[-1] < closes[-3]:
            return "Downward bias"
        else:
            return "Sideways"
    
    def _analyze_sr_tests(self, candles: list, support_level: Decimal, resistance_level: Decimal) -> str:
        """Analyze support/resistance tests."""
        resistance_tests = 0
        support_tests = 0
        
        for candle in candles:
            high_price = float(candle[2])
            low_price = float(candle[3])
            
            if abs(high_price - float(resistance_level)) / float(resistance_level) < 0.01:
                resistance_tests += 1
            if abs(low_price - float(support_level)) / float(support_level) < 0.01:
                support_tests += 1
        
        if resistance_tests > 0 and support_tests > 0:
            return f"R:{resistance_tests} tests, S:{support_tests} tests"
        elif resistance_tests > 0:
            return f"Resistance tested {resistance_tests} times"
        elif support_tests > 0:
            return f"Support tested {support_tests} times"
        else:
            return "No recent S/R tests"
    
    def _analyze_volume_relationship(self, candles: list) -> str:
        """Analyze volume-price relationship."""
        if len(candles) < 3:
            return "Insufficient data"
        
        recent_volumes = [float(c[5]) for c in candles[-3:]]
        recent_closes = [float(c[4]) for c in candles[-3:]]
        
        avg_volume = sum(recent_volumes) / len(recent_volumes)
        price_trend = "up" if recent_closes[-1] > recent_closes[0] else "down"
        volume_trend = "increasing" if recent_volumes[-1] > avg_volume else "decreasing"
        
        if price_trend == "up" and volume_trend == "increasing":
            return "Strong bullish confirmation"
        elif price_trend == "down" and volume_trend == "increasing":
            return "Strong bearish confirmation"
        elif price_trend == "up" and volume_trend == "decreasing":
            return "Weak bullish signal"
        elif price_trend == "down" and volume_trend == "decreasing":
            return "Weak bearish signal"
        else:
            return "Mixed signals"


# Factory function for easy instantiation
def create_market_data_service(cache_dir: str = "data/cache") -> MarketDataService:
    """Create a MarketDataService instance."""
    return MarketDataService(cache_dir=cache_dir)


if __name__ == "__main__":
    # Test the service
    service = create_market_data_service()
    
    try:
        # Test with BTC basic context
        btc_data = service.get_market_data("BTCUSDT")
        print("=== BTC Market Data Test (Basic) ===")
        print(btc_data.to_llm_context())
        
        print("\n" + "="*60 + "\n")
        
        # Test with enhanced candlestick analysis
        print("=== BTC Market Data Test (Enhanced) ===")
        print(service.get_enhanced_context("BTCUSDT"))
        
    except Exception as e:
        print(f"Test failed: {e}")