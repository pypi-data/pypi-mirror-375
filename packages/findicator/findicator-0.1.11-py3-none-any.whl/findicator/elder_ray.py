import pandas as pd

def elder_ray(high: pd.Series, low: pd.Series, close: pd.Series, ema_period: int = 13):
    ema = close.ewm(span=ema_period, adjust=False).mean()
    bull_power = high - ema
    bear_power = low - ema
    return bull_power, bear_power
