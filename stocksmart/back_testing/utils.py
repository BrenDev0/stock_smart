from typing import List
from stocksmart.models import Trade


def calculate_days_held(entry_date, exit_date) -> int:
    return (exit_date - entry_date).days

def calculate_short_position_pl(entry: float, exit: float) -> float:
    return (entry - exit) / entry

def calculate_long_position_pl(entry: float, exit: float) -> float:
    return (exit - entry) / entry

def gather_wins(trades: List[Trade])-> List[float | None]:
    return [
        trade.pl_pct for trade in trades if trade.pl_pct > 0
    ]

def gather_losses(trades: List[Trade]) -> List[float | None]:
    return [
        trade.pl_pct for trade in trades if trade.pl_pct < 0 
    ]

def get_average_pl_pct(trades: List[float]) -> float:
    return sum(trades) / len(trades)

def get_average_days_held(trades: list[Trade]) -> float:
    return sum([trade.days_held for trade in trades]) /len(trades)

