import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
from .stategies import cross_sectional_mean_reversion
def main():
    portfolios = ["xlb", "xlc", "xle",  "xlf", "xlg", "xli", "xlk", "xlp", "xlre", "xlu", "xlv", "xly", "spy", "dia", "qqq", "iwm"] 
    result = cross_sectional_mean_reversion(tickers=portfolios, window=90)
    
    print(result)


if __name__  == "__main__":
    main()
