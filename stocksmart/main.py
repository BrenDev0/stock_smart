import asyncio
import pandas as pd
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
from .stategies import pair_trade

async def main():
    portfolios = ["xlb", "xlc", "xle",  "xlf", "xlg", "xli", "xlk", "xlp", "xlre", "xlu", "xlv", "xly", "spy", "dia", "qqq", "iwm", "gld", "slv"] 
    tasks = []

    for i in portfolios:
        ticker = i
        for k in portfolios:
            if k == ticker:
                continue

            tasks.append(asyncio.to_thread(pair_trade, ticker, k, 90)) 

    results = await asyncio.gather(*tasks)
    trades = [
        i for i in results if isinstance(i, dict)
    ]
    
    df = pd.DataFrame(trades)
    print(df)


if __name__  == "__main__":
    asyncio.run(main())
