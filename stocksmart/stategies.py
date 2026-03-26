import yfinance as yf
import pandas as pd
import numpy as np


def trend_signals(ticker: yf.Ticker):
    pass


def adx(df: pd.DataFrame, length: int = 14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    df["high_low"] = abs(high - low)
    df["high_close"] = abs(high - close.shift(1))
    df["low_close"] = abs(low - close.shift(1))
    df["true_range"] = df[["high_low", "high_close", "low_close"]].max(axis=1)

    df["up_move"] = high - high.shift(1)
    df["down_move"] = low.shift(1) - low

    df["+dm"] = np.where((df["up_move"] > df["down_move"]) & (df["up_move"] > 0), df["up_move"], 0)
    df["-dm"] = np.where((df["down_move"] > df["up_move"]) & (df["down_move"] > 0), df["down_move"], 0)

    df["+di"] = 100 * (df["+dm"].ewm(span=length).mean() / df["true_range"].ewm(span=length).mean())
    df["-di"] = 100 * (df["-dm"].ewm(span=length).mean() / df["true_range"].ewm(span=length).mean())
    df["dx"] = 100 * abs(df["+di"] - df["-di"]) / (df["+di"] + df["-di"])
    df["adx"] = df["dx"].ewm(span=length).mean()

    return df[["adx", "+di", "-di"]]

        


def mean_reversion(df: pd.DataFrame, sma_length: int = 50):
    df = df.rename(columns={"Close": "close"})
    df["sma"] = df["close"].rolling(window=sma_length).mean()
    
    df["deviation"] = df["close"] - df["sma"]
    df["std_deviation"] = df["deviation"].rolling(window=sma_length).std()
    

    df["z_score"] = df["deviation"] / df["std_deviation"]

    return df[["sma", "std_deviation", "deviation", "z_score", "close"]]
    


    
