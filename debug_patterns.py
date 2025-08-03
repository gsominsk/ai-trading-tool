from decimal import Decimal

def debug_pattern_logic():
    """Отладка логики распознавания паттернов."""
    print("=== ОТЛАДКА ПАТТЕРНОВ ===\n")
    
    # Hammer pattern test
    candle = [1640995200000, "100.00", "100.20", "98.00", "100.10"]
    open_price = Decimal(str(candle[1]))    # 100.00
    high_price = Decimal(str(candle[2]))    # 100.20
    low_price = Decimal(str(candle[3]))     # 98.00
    close_price = Decimal(str(candle[4]))   # 100.10
    
    body = abs(close_price - open_price)                           # |100.10 - 100.00| = 0.10
    upper_shadow = high_price - max(open_price, close_price)       # 100.20 - 100.10 = 0.10
    lower_shadow = min(open_price, close_price) - low_price        # 100.00 - 98.00 = 2.00
    total_range = high_price - low_price                           # 100.20 - 98.00 = 2.20
    
    print("HAMMER TEST:")
    print(f"Body: {body} ({body/total_range:.3f})")
    print(f"Upper shadow: {upper_shadow} ({upper_shadow/total_range:.3f})")
    print(f"Lower shadow: {lower_shadow} ({lower_shadow/total_range:.3f})")
    print(f"Total range: {total_range}")
    
    lower_ratio = lower_shadow / total_range
    body_ratio = body / total_range
    
    print(f"Lower shadow ratio: {lower_ratio:.3f} > 0.6? {lower_ratio > Decimal('0.6')}")
    print(f"Body ratio: {body_ratio:.3f} < 0.3? {body_ratio < Decimal('0.3')}")
    print(f"Is Hammer? {lower_ratio > Decimal('0.6') and body_ratio < Decimal('0.3')}")
    
    print("\n" + "="*50 + "\n")
    
    # Shooting Star test
    candle2 = [1640995200000, "100.00", "102.00", "99.80", "99.90"]
    open_price2 = Decimal(str(candle2[1]))    # 100.00
    high_price2 = Decimal(str(candle2[2]))    # 102.00
    low_price2 = Decimal(str(candle2[3]))     # 99.80
    close_price2 = Decimal(str(candle2[4]))   # 99.90
    
    body2 = abs(close_price2 - open_price2)                           # |99.90 - 100.00| = 0.10
    upper_shadow2 = high_price2 - max(open_price2, close_price2)      # 102.00 - 100.00 = 2.00
    lower_shadow2 = min(open_price2, close_price2) - low_price2       # 99.90 - 99.80 = 0.10
    total_range2 = high_price2 - low_price2                           # 102.00 - 99.80 = 2.20
    
    print("SHOOTING STAR TEST:")
    print(f"Body: {body2} ({body2/total_range2:.3f})")
    print(f"Upper shadow: {upper_shadow2} ({upper_shadow2/total_range2:.3f})")
    print(f"Lower shadow: {lower_shadow2} ({lower_shadow2/total_range2:.3f})")
    print(f"Total range: {total_range2}")
    
    upper_ratio2 = upper_shadow2 / total_range2
    body_ratio2 = body2 / total_range2
    
    print(f"Upper shadow ratio: {upper_ratio2:.3f} > 0.6? {upper_ratio2 > Decimal('0.6')}")
    print(f"Body ratio: {body_ratio2:.3f} < 0.3? {body_ratio2 < Decimal('0.3')}")
    print(f"Is Shooting Star? {upper_ratio2 > Decimal('0.6') and body_ratio2 < Decimal('0.3')}")

if __name__ == "__main__":
    debug_pattern_logic()