import pandas as pd


def force_index(close: pd.Series, volume: pd.Series, period: int = 13):
    fi = close.diff() * volume
    smoothed = fi.ewm(span=period, adjust=False).mean()
    return smoothed
