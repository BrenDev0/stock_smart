from stocksmart.back_testing.mean_reversion import optimize_mean_reversion_params, back_test_mean_reversion
import yfinance as yf
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

def main():
    ticker = yf.Ticker("ibm")
    price_history = ticker.history(period="5y")

    study = optimize_mean_reversion_params(df=price_history, n_trials=100)
    best_params = study.best_params

    result = back_test_mean_reversion(
        price_history=price_history, 
        z_score_entry=best_params["z_score_entry"],
        z_score_exit=best_params["z_score_exit"],
        sma_length=best_params["sma_length"]
    )

    print(result)

if __name__  == "__main__":
    main()
