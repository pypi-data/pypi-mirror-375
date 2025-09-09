# MeridianAlgo

[![PyPI version](https://img.shields.io/pypi/v/meridianalgo.svg)](https://pypi.org/project/meridianalgo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/pypi/pyversions/meridianalgo.svg)](https://pypi.org/project/meridianalgo/)

Advanced Algorithmic Trading and Statistical Analysis Library

## Overview

MeridianAlgo is a comprehensive Python library designed for quantitative finance, algorithmic trading, and statistical analysis. It provides powerful tools for portfolio optimization, time series analysis, statistical arbitrage, and machine learning for financial markets.

## Features

- **Portfolio Optimization**: Modern portfolio theory implementation with efficient frontier calculation
- **Statistical Analysis**: Advanced statistical methods including cointegration, volatility modeling, and risk metrics
- **Machine Learning**: Feature engineering and model evaluation for financial time series prediction
- **Data Processing**: Efficient tools for handling and preprocessing financial data
- **Risk Management**: Value at Risk (VaR), Expected Shortfall (CVaR), and other risk metrics

## Installation

```bash
pip install meridianalgo
```

## Quick Start

```python
import meridianalgo as ma
import yfinance as yf

# Fetch market data
data = yf.download(['AAPL', 'MSFT', 'GOOGL'], start='2020-01-01')['Adj Close']

# Calculate returns
returns = data.pct_change().dropna()

# Portfolio optimization
optimizer = ma.PortfolioOptimizer(returns)
efficient_frontier = optimizer.calculate_efficient_frontier()

# Statistical analysis
analyzer = ma.StatisticalArbitrage(data)
correlation = analyzer.calculate_rolling_correlation(window=21)

# Calculate risk metrics
var = ma.calculate_value_at_risk(returns['AAPL'])
es = ma.calculate_expected_shortfall(returns['AAPL'])
```

## Documentation

### Core Modules

#### PortfolioOptimizer
Optimize portfolio allocation using modern portfolio theory.

```python
optimizer = ma.PortfolioOptimizer(returns)
frontier = optimizer.calculate_efficient_frontier()
```

#### StatisticalArbitrage
Statistical arbitrage and cointegration analysis.

```python
arbitrage = ma.StatisticalArbitrage(data)
cointegration_test = arbitrage.test_cointegration(data['AAPL'], data['MSFT'])
```

#### TimeSeriesAnalyzer
Time series analysis and technical indicators.

```python
analyzer = ma.TimeSeriesAnalyzer(data['AAPL'])
volatility = analyzer.calculate_volatility(window=21)
```

### Risk Metrics

- `calculate_value_at_risk(returns, confidence_level=0.95)`
- `calculate_expected_shortfall(returns, confidence_level=0.95)`
- `calculate_max_drawdown(returns)`
- `hurst_exponent(time_series, max_lag=20)`

### Machine Learning

#### Feature Engineering

```python
engineer = ma.FeatureEngineer()
features = engineer.create_features(data['AAPL'])
```

#### Model Evaluation

```python
metrics = ma.ModelEvaluator.calculate_metrics(y_true, y_pred)
cv_results = ma.ModelEvaluator.time_series_cv(model, X, y)
```

## Examples

See the `examples/` directory for complete usage examples:

1. [Portfolio Optimization](examples/portfolio_optimization.py)
2. [Statistical Arbitrage](examples/statistical_arbitrage.py)
3. [Time Series Prediction](examples/time_series_prediction.py)

## Requirements

- Python 3.7+
- numpy
- pandas
- scipy
- scikit-learn
- yfinance
- torch (for deep learning features)

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests, report issues, or suggest features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on GitHub or contact support@meridianalgo.com

---

*MeridianAlgo is developed and maintained by the Meridian Algorithmic Research Team.*
