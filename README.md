# Currency Pair Analysis and Trading Strategy

This repository contains a Python script for analyzing cointegration among various currency pairs. It leverages the power of the C-Vine copula structure to model dependencies among the pairs, based on which a trading strategy is formulated.

## Dependencies

- `pandas`
- `numpy`
- `statsmodels`
- `pyvinecopulib`
- `yfinance`
- `matplotlib`

You can install the necessary libraries using pip:

\```bash
pip install pandas numpy statsmodels pyvinecopulib yfinance matplotlib
\```

## Features

1. **Data Fetching**: Fetches the closing prices of specific currency pairs.
2. **Cointegration Analysis**: Determines if pairs of currencies are cointegrated.
3. **C-Vine Copula Modeling**: Determines the best C-Vine copula structure for the given currency pairs.
4. **Trading Strategy**: Formulates a trading strategy based on the copula analysis.
5. **Performance Metrics**: Evaluates the performance of the formulated strategy against a simple buy-and-hold strategy.


## Results

The script provides a visualization comparing the cumulative returns of the formulated trading strategy and a simple buy-and-hold strategy. Additionally, it prints out performance metrics such as Annualized Return, Sharpe Ratio, and Max Drawdown for both strategies.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue if you have improvements or fixes.

