import yfinance as yf
import pandas as pd


def trend_signals(ticker: yf.Ticker):
    price_history = ticker.history(period='5y')
    closing_prices = price_history["Close"]
    

    sma_20 = closing_prices.roling(20).mean()
    sma_50 = closing_prices.rolling(50).mean()
    sma_200 = closing_prices.rolling(200).mean()

    short_term_trend = sma_20 > sma_50
    long_term_trend = sma_50 > sma_200


def get_adx(df: pd.DataFrame, length: int = 14):
        high = df["High"]
        low = df["Low"]
        close = df["Close"]

        
        df["high_low"] = abs(high - low)
        df["high_close"] = abs(high - close.shift(1))
        df["low_close"] = abs(low - close.shift(1))
        df["true_range"] = df[["high_low", "high_close", "low_close"]].max(axis=1)

        df["plus_move"] = high - high.shift(1)
        df["minus_move"] = low.shift(1) - low 






def mean_reversion(ticker: yf.Ticker):
    price_history = ticker.history(period='1y')
    closing_prices = price_history["Close"]

    window = closing_prices.tail(50)
    sma = window.sum() / len(window)
    

    std = window.std()
    deviation = window.iloc[-1] - sma

    z_score = deviation / std

    return {
        "price": str(window.iloc[-1]),
        "z_score": str(z_score),
        "upper_band": str(sma + std * 2),
        "lower_band": str(sma - std * 2),
        "standard_deviation": str(std),
        "deviation": str(deviation)
    }
    


    
