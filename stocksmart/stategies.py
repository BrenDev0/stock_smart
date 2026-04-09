import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint



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
    

def pair_trade(ticker_a: str, ticker_b: str, window: int):
    price_history_a = yf.Ticker(ticker_a).history(period="5y", auto_adjust=True)
    price_history_b = yf.Ticker(ticker_b).history(period="5y", auto_adjust=True)

    df = pd.DataFrame({
        ticker_a: price_history_a["Close"],
        ticker_b: price_history_b["Close"]
    }).dropna()

    if len(df) < window + 1:
        return f"Not enough overlapping data for {ticker_a}, {ticker_b} with window={window}"
    
    returns = df.pct_change().dropna()
    
    correlation = returns[ticker_a].corr(returns[ticker_b])
    if pd.isna(correlation) or correlation < 0.7:
        return f"Insufficient correlation for {ticker_a}, {ticker_b}: {correlation}"
        

    score, pvalue, _ = coint(df[ticker_a], df[ticker_b])
    if pd.isna(pvalue) or pvalue > 0.05:
        return f"Cointegration failed for {ticker_a}, {ticker_b}: p-value={pvalue}"

    y = df[ticker_a]
    x = df[ticker_b]

    X = sm.add_constant(x)

    model = sm.OLS(y, X).fit()
    beta = model.params[ticker_b]
    alpha = model.params["const"]

    spread = y - (alpha + beta * x)

    rolling_mean = spread.rolling(window).mean()

    rolling_std_dev = spread.rolling(window).std(ddof=1)
    
    z_score = (spread - rolling_mean) / rolling_std_dev
    z_score = z_score.dropna()
    if z_score.empty:
        return f"Could not compute z-score for {ticker_a}, {ticker_b}"
    

    latest_score = z_score.iloc[-1]
    latest_spread = spread.iloc[-1]
    latest_mean = rolling_mean.iloc[-1]
    latest_std = rolling_std_dev.iloc[-1]

    signal = "neutral"

    if latest_score > 2:
        signal = "short spread"
    elif latest_score < -2:
        signal = "long spread"

   
    return {
        "ticker_a": ticker_a,
        "ticker_b": ticker_b,
        "correlation": round(correlation, 2),
        "cointegration_pvalue": round(pvalue, 4),
        "hedge_ratio": round(beta, 4),
        "intercept": round(alpha, 4),
        "latest_spread": round(latest_spread, 4),
        "rolling_mean": round(latest_mean, 4),
        "rolling_std_dev": round(latest_std, 4),
        "latest_z_score": round(latest_score, 4),
        "signal": signal
    }
    
    
    



    
