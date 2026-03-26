import pandas as pd
import optuna
from stocksmart.stategies import mean_reversion
from stocksmart.models import Trade
from .utils import (
    calculate_days_held, 
    calculate_long_position_pl, 
    calculate_short_position_pl,
    gather_losses,
    gather_wins,
    get_average_pl_pct,
    get_average_days_held
)


def back_test_mean_reversion(price_history: pd.DataFrame, z_score_entry: int, z_score_exit: int, sma_length: int):
    df: pd.DataFrame = mean_reversion(df=price_history, sma_length=sma_length)
    
    long_entry = df["z_score"] <= -abs(z_score_entry)
    short_entry = df["z_score"] >= abs(z_score_entry)

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

        if abs(row["z_score"]) <= abs(z_score_exit) and position != 0:
            trade = Trade(days_held=calculate_days_held(entry_date, date))
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
        "sma_length": sma_length,
        "z_score_thresholds": f"entry: +/-{z_score_entry}, exit: +/-{z_score_exit}",
        "win_stats": f"{len(wins)}, total: {sum(wins)}, average_win: {get_average_pl_pct(wins)}",
        "loss_stats": f"{len(losses)}, total: {sum(losses)}, average_loss: {get_average_pl_pct(losses)}",
        "pl": sum([trade.pl_pct for trade in trades]),
        "average_days_held": get_average_days_held(trades)
    }
    


def optimize_mean_reversion_params(df: pd.DataFrame, n_trials: int):
    def objective(trial: optuna.Trial):
        z_score_entry = trial.suggest_float("z_score_entry", 0.5, 2.0)
        z_score_exit = trial.suggest_float("z_score_exit", 0.0, z_score_entry - 0.2)
        sma_length = trial.suggest_categorical("sma_length", [20, 50, 200])

        result = back_test_mean_reversion(price_history=df, z_score_entry=z_score_entry, z_score_exit=z_score_exit, sma_length=sma_length)

        pl = result["pl"]
        return pl
    
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)

    return study


