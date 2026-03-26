import pandas as pd
import optuna
from stocksmart.models import Trade
from ..stategies import adx
from .utils import (
    calculate_days_held, 
    calculate_long_position_pl, 
    calculate_short_position_pl,
    get_average_days_held,
    gather_losses, 
    gather_wins,
    get_average_pl_pct
)


def back_test_adx(price_history: pd.DataFrame, adx_entry: int, adx_exit: int):
    df = adx(price_history)
    df["close"] = price_history["Close"] 

    long_entry = (df["+di"] > df["-di"]) & (df["adx"] >= adx_entry)
    short_entry = (df["-di"] > df["+di"]) & (df["adx"] >= adx_entry)
    
    df["signal"] = 0
    
    df.loc[long_entry, "signal"] = 1
    df.loc[short_entry, "signal"] = -1

    trades = []
    position = 0
    entry_price = None
    entry_date = None

    for date, row in df.iterrows():
        if position == 0 and row["signal"] != 0:
            position = row["signal"]
            entry_price = row["close"]
            entry_date = date
            continue


        if row["signal"] == 1:
            if position == -1:
                trade = Trade(
                    pl_pct=calculate_short_position_pl(entry=entry_price, exit=row["close"]),
                    days_held=calculate_days_held(entry_date, date)
                ) 

                trades.append(trade)
                position = 1
                entry_price = row["close"]
                entry_date = date
    
        if row["signal"] == -1:    
            if position == 1:
                trade = Trade(
                    pl_pct=calculate_long_position_pl(entry=entry_price, exit=row["close"]),
                    days_held=calculate_days_held(entry_date, date)
                )

                trades.append(trade)
                position = -1
                entry_price = row["close"]
                entry_date = date

        if row["adx"] <= adx_exit and position != 0:
            trade = Trade(
                days_held=calculate_days_held(entry_date, date)
            )
            if position == 1:
                trade.pl_pct = calculate_long_position_pl(entry=entry_price, exit=row["close"])
            else:
                trade.pl_pct = calculate_short_position_pl(entry=entry_price, exit=row["close"])
            
            trades.append(trade)
            
            position = 0
            entry_date = None
            entry_price = None
                

    wins = gather_wins(trades)

    losses = gather_losses(trades)

    return {
        "adx_thresholds": f"entry: {adx_entry}, exit: {adx_exit}",
        "wins_stats": f"{len(wins)} wins, total: {sum(wins)*100:.2f}%, average win: {get_average_pl_pct(wins)}",
        "loss_stats": f"{len(losses)} losses, total: {sum(losses)*100:.2f}, average loss: {get_average_pl_pct(losses)}",
        "trades": len(trades),
        "pl": sum([trade.pl_pct for trade in trades]),
        "average_days_held": str(get_average_days_held(trades))
    }


def optimize_adx_params(df: pd.DataFrame, n_trials: int = 100):
    def objective(trial: optuna.Trial):
        adx_entry = trial.suggest_int("adx_entry", 20, 50)
        adx_exit = trial.suggest_int("adx_exit", 10, adx_entry -5)
        results = back_test_adx(df=df, adx_entry=adx_entry, adx_exit=adx_exit)

        pl = results["pl"]
        return pl
    

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)

    return study
