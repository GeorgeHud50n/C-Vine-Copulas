import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint
import pyvinecopulib as pv
import yfinance as yf
import matplotlib.pyplot as plt

def fetch_data(currency_pairs):
    """
    Fetch closing prices for the currency pairs.
    """
    data = {pair: yf.download(pair, start="2000-01-01", end="2023-01-01")['Close'] for pair in currency_pairs}
    return pd.concat(data, axis=1)

def check_cointegration(combined_data_returns, currency_pairs):
    """
    Check cointegration between pairs of currency returns.
    """
    for i in range(4):
        for j in range(i+1, 4):
            _, pvalue, _ = coint(combined_data_returns[currency_pairs[i]], combined_data_returns[currency_pairs[j]])
            print(f"{currency_pairs[i]} and {currency_pairs[j]} {'ARE' if pvalue < 0.05 else 'are NOT'} cointegrated with p-value: {pvalue:.4f}")

def determine_best_copula_structure(orders, ranks):
    """
    Determine the best C-vine copula structure.
    """
    best_likelihood = float('-inf')
    best_order = None
    best_copula = None

    for order in orders:
        cop = pv.Vinecop(pv.CVineStructure(order))
        cop.select(ranks)
        likelihood = cop.loglik(ranks)
        if likelihood > best_likelihood:
            best_likelihood = likelihood
            best_order = order
            best_copula = cop

    return best_order, best_copula

def main():
    # Constants
    currency_pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X']

    # Fetch and prepare data
    combined_data = fetch_data(currency_pairs)
    combined_data_returns = combined_data.pct_change().dropna()

    # Check cointegration on returns
    check_cointegration(combined_data_returns, currency_pairs)

    # Specify C-Vine copula orderings
    orders = [[1, 2, 3, 4], [1, 2, 4, 3], [1, 3, 2, 4], [1, 3, 4, 2], [1, 4, 2, 3], [1, 4, 3, 2]]
    ranks = combined_data_returns.rank(pct=True).values

    # Find the best copula structure
    best_order, best_copula = determine_best_copula_structure(orders, ranks)
    pivotal_pair = currency_pairs[best_order[-1]-1]

    print(f"Best order: {best_order}")
    print(f"Pivotal pair: {pivotal_pair}")

    # Trading Strategy Constants
    N_SAMPLES = 10000
    OVERVALUED_THRESHOLD = 0.75  # placeholder, you need to define this value
    UNDERVALUED_THRESHOLD = 0.25  # placeholder, you need to define this value

    # Simulate data and calculate trading signals
    simulated_samples = best_copula.simulate(N_SAMPLES)
    trading_signals = []

    for current_ranks in ranks:
        relevant_samples = simulated_samples[np.all(simulated_samples[:, [0, 1, 3]] <= current_ranks[[0, 1, 3]], axis=1)]
        cond_cdf_value = np.mean(relevant_samples[:, 2] <= current_ranks[2])

        # Determine trading signals
        if cond_cdf_value > OVERVALUED_THRESHOLD:
            trading_signals.append(-1)
        elif cond_cdf_value < UNDERVALUED_THRESHOLD:
            trading_signals.append(1)
        else:
            trading_signals.append(0)

    # Calculate returns and performance metrics
    trading_signals = pd.Series(trading_signals, index=combined_data_returns.index)
    strategy_returns = trading_signals.shift() * combined_data_returns[pivotal_pair]
    cumulative_strategy_returns = (1 + strategy_returns.fillna(0)).cumprod()

    # Calculate Buy-and-Hold returns for USDJPY=X
    buy_and_hold_returns = combined_data_returns['USDJPY=X']
    cumulative_buy_and_hold_returns = (1 + buy_and_hold_returns).cumprod()

    # Plot Cumulative Returns (Strategy vs. Buy-and-Hold)
    plt.figure(figsize=(15, 7))
    cumulative_strategy_returns.plot(label="Strategy Returns for Pivotal Pair")
    cumulative_buy_and_hold_returns.plot(label="Buy-and-Hold Returns for USDJPY=X")
    plt.title("Cumulative Returns Comparison")
    plt.legend()
    plt.show()

    # Performance Metrics for Strategy
    strategy_returns_mean = strategy_returns.mean()
    strategy_returns_std = strategy_returns.std()
    annualized_return = (cumulative_strategy_returns.iloc[-1]) ** (252.0/len(cumulative_strategy_returns)) - 1
    sharpe_ratio = strategy_returns_mean / strategy_returns_std * np.sqrt(252)
    rolling_max = cumulative_strategy_returns.cummax()
    drawdown = (cumulative_strategy_returns - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    print(f"Annualized Return for Strategy on {pivotal_pair}: {annualized_return*100:.2f}%")
    print(f"Sharpe Ratio for Strategy on {pivotal_pair}: {sharpe_ratio:.2f}")
    print(f"Max Drawdown for Strategy on {pivotal_pair}: {max_drawdown*100:.2f}%")

    # Performance Metrics for Buy-and-Hold
    annualized_return_bh = (cumulative_buy_and_hold_returns.iloc[-1]) ** (252.0/len(cumulative_buy_and_hold_returns)) - 1
    sharpe_ratio_bh = buy_and_hold_returns.mean() / buy_and_hold_returns.std() * np.sqrt(252)
    rolling_max_bh = cumulative_buy_and_hold_returns.cummax()
    drawdown_bh = (cumulative_buy_and_hold_returns - rolling_max_bh) / rolling_max_bh
    max_drawdown_bh = drawdown_bh.min()

    print(f"Annualized Return for Buy-and-Hold on USDJPY=X: {annualized_return_bh*100:.2f}%")
    print(f"Sharpe Ratio for Buy-and-Hold on USDJPY=X: {sharpe_ratio_bh:.2f}")
    print(f"Max Drawdown for Buy-and-Hold on USDJPY=X: {max_drawdown_bh*100:.2f}%")

    # Position Counts
    long_positions = trading_signals[trading_signals == 1].count()
    short_positions = trading_signals[trading_signals == -1].count()
    neutral_positions = trading_signals[trading_signals == 0].count()

    print(f"Number of Long Positions: {long_positions}")
    print(f"Number of Short Positions: {short_positions}")
    print(f"Number of Neutral Positions: {neutral_positions}")

if __name__ == "__main__":
    main()
