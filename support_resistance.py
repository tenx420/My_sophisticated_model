def calculate_pivot_points(high, low, close):
    """
    Calculate the pivot point and support/resistance levels based on the previous day's high, low, and close.
    
    :param high: Previous day's high price
    :param low: Previous day's low price
    :param close: Previous day's close price
    :return: A dictionary containing pivot point, support levels, and resistance levels
    """
    # Pivot Point
    pivot_point = (high + low + close) / 3

    # Resistance Levels
    resistance_1 = (2 * pivot_point) - low
    resistance_2 = pivot_point + (high - low)
    resistance_3 = high + 2 * (pivot_point - low)

    # Support Levels
    support_1 = (2 * pivot_point) - high
    support_2 = pivot_point - (high - low)
    support_3 = low - 2 * (high - pivot_point)

    return {
        "Pivot Point": round(pivot_point, 2),
        "Resistance 1": round(resistance_1, 2),
        "Resistance 2": round(resistance_2, 2),
        "Resistance 3": round(resistance_3, 2),
        "Support 1": round(support_1, 2),
        "Support 2": round(support_2, 2),
        "Support 3": round(support_3, 2),
    }
