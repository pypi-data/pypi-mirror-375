# Portfolio-lib 📈

**Ultra-Lightweight Python Backtesting Library for Algorithmic Trading**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Package Size](https://img.shields.io/badge/size-%3C500KB-green)](https://pypi.org/project/portfolio-lib/)

**Authors:** Rahul Ashok, Pritham Devaprasad, Siddarth S, and Anish R

Portfolio-lib is a comprehensive, ultra-lightweight backtesting framework designed for developing and testing quantitative trading strategies. With minimal dependencies and maximum performance, it provides everything you need for professional algorithmic trading research.

## 🚀 Key Features

### ⚡ **Ultra-Lightweight Architecture**
- **< 500KB total package size** - minimal memory footprint
- Only essential dependencies: pandas, numpy, yfinance, scipy, matplotlib
- Optimized for speed and efficiency

### 📊 **Comprehensive Technical Analysis**
- **129 Technical Indicators** built-in
- SMA, EMA, RSI, MACD, Bollinger Bands, Stochastic, ADX, and more
- Custom indicator support with easy extensibility

### 🔄 **Advanced Backtesting Engine**
- Event-driven backtesting architecture
- Multi-asset portfolio simulation
- Commission and slippage modeling
- Real-time strategy execution

### 📈 **Professional Analytics**
- Advanced performance metrics (Sharpe, Sortino, Calmar ratios)
- Risk management tools (VaR, CVaR, Maximum Drawdown)
- Comprehensive trade analysis and reporting
- Visual performance charts and equity curves

### 🌐 **Data Integration**
- **yfinance integration** for real market data
- Support for stocks, ETFs, forex, and cryptocurrencies
- Custom data source support
- Historical and real-time data handling

## 📦 Installation

```bash
pip install portfolio-lib
```

### Requirements
- Python 3.8+
- pandas >= 1.5.0
- numpy >= 1.21.0
- yfinance >= 0.2.0
- scipy >= 1.9.0
- matplotlib >= 3.5.0

## 🎯 Quick Start

### Basic SMA Crossover Strategy

```python
from portfolio_lib import BaseStrategy, Backtest, YFinanceDataFeed

class SMAStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.symbols = ['AAPL', 'MSFT']
        self.start_date = '2020-01-01'
        self.end_date = '2023-12-31'
        self.fast_period = 10
        self.slow_period = 30
        
    def init_indicators(self):
        print(f"SMA Strategy initialized for {self.symbols}")
    
    def next(self):
        for symbol in self.symbols:
            prices = self.data[symbol]['Close']
            
            if len(prices) < self.slow_period:
                continue
                
            fast_sma = prices.rolling(self.fast_period).mean().iloc[-1]
            slow_sma = prices.rolling(self.slow_period).mean().iloc[-1]
            
            position = self.position(symbol)
            
            # Buy signal: fast SMA crosses above slow SMA
            if fast_sma > slow_sma and position is None:
                self.buy(symbol, 0.5)  # 50% of portfolio
                
            # Sell signal: fast SMA crosses below slow SMA  
            elif fast_sma < slow_sma and position is not None:
                self.sell(symbol)

# Run backtest
strategy = SMAStrategy()
backtest = Backtest(strategy, initial_cash=100000)
data_feed = YFinanceDataFeed(strategy.symbols)
backtest.add_data_source(data_feed)

results = backtest.run(strategy.start_date, strategy.end_date)
print(results.summary())
```

### RSI Mean Reversion Strategy

```python
from portfolio_lib import BaseStrategy, TechnicalIndicators

class RSIStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.symbols = ['TSLA', 'NVDA']
        self.start_date = '2021-01-01'
        self.end_date = '2023-12-31'
        self.rsi_period = 14
        self.oversold = 30
        self.overbought = 70
        
    def next(self):
        for symbol in self.symbols:
            prices = self.data[symbol]['Close']
            
            if len(prices) < self.rsi_period + 1:
                continue
                
            rsi = TechnicalIndicators.rsi(prices, self.rsi_period)
            position = self.position(symbol)
            
            # Buy when oversold
            if rsi < self.oversold and position is None:
                self.buy(symbol, 0.3)
                
            # Sell when overbought
            elif rsi > self.overbought and position is not None:
                self.sell(symbol)
```

## 📚 Core Components

### 🔧 **BaseStrategy**
Base class for all trading strategies with built-in portfolio management:

```python
class MyStrategy(BaseStrategy):
    def init_indicators(self):
        # Initialize your indicators here
        pass
        
    def next(self):
        # Your strategy logic for each bar
        # Access data: self.data[symbol]['Close']
        # Place orders: self.buy(symbol, size) / self.sell(symbol)
        # Check positions: self.position(symbol)
        pass
```

### 💰 **Portfolio Management**
Automatic portfolio tracking with position management:

```python
# Portfolio automatically tracks:
# - Cash balance
# - Active positions  
# - Trade history
# - Equity curve
# - Performance metrics

portfolio = results.portfolio
print(f"Total Equity: ${portfolio.total_equity:,.2f}")
print(f"Cash: ${portfolio.cash:,.2f}")
print(f"Positions: {len(portfolio.positions)}")
```

### 📊 **Technical Indicators**
81+ built-in technical indicators:

```python
from portfolio_lib import TechnicalIndicators

# Moving averages
sma = TechnicalIndicators.sma(prices, period=20)
ema = TechnicalIndicators.ema(prices, period=20)
wma = TechnicalIndicators.wma(prices, period=20)

# Oscillators
rsi = TechnicalIndicators.rsi(prices, period=14)
stoch = TechnicalIndicators.stochastic(high, low, close)
williams_r = TechnicalIndicators.williams_r(high, low, close)

# Trend indicators
macd = TechnicalIndicators.macd(prices)
adx = TechnicalIndicators.adx(high, low, close)
aroon = TechnicalIndicators.aroon(high, low)

# Volatility indicators
bb = TechnicalIndicators.bollinger_bands(prices)
atr = TechnicalIndicators.atr(high, low, close)
```

### 📈 **Performance Analytics**
Comprehensive performance and risk metrics:

```python
metrics = results.metrics

# Returns and performance
print(f"Total Return: {metrics.total_return:.2f}%")
print(f"Annualized Return: {metrics.annualized_return:.2f}%")
print(f"Volatility: {metrics.volatility:.2f}%")

# Risk metrics
print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
print(f"Sortino Ratio: {metrics.sortino_ratio:.2f}")
print(f"Maximum Drawdown: {metrics.max_drawdown:.2f}%")

# Trading metrics
print(f"Win Rate: {metrics.win_rate:.2f}%")
print(f"Profit Factor: {metrics.profit_factor:.2f}")
print(f"Total Trades: {len(metrics.trades)}")
```

## 🎛️ **Built-in Strategies**

Portfolio-lib includes professionally implemented strategies ready to use:

```python
from portfolio_lib import (
    SMAStrategy, EMAStrategy, RSIStrategy, MACDStrategy,
    BollingerBandsStrategy, MeanReversionStrategy, MomentumStrategy
)

# Use built-in strategies directly
strategy = RSIStrategy(symbols=['AAPL'], rsi_period=14)
backtest = Backtest(strategy, initial_cash=100000)
```

## 🛠️ **Advanced Features**

### Multi-Asset Portfolio
```python
class DiversifiedStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.stocks = ['AAPL', 'MSFT', 'GOOGL']
        self.etfs = ['SPY', 'QQQ', 'IWM']
        self.symbols = self.stocks + self.etfs
```

### Risk Management
```python
from portfolio_lib import RiskMetrics

# Portfolio risk analysis
risk = RiskMetrics(portfolio)
var_95 = risk.value_at_risk(confidence=0.95)
cvar_95 = risk.conditional_var(confidence=0.95)
```

### Custom Data Sources
```python
class CustomDataFeed(DataFeed):
    def fetch_data(self, symbols, start_date, end_date):
        # Implement your custom data fetching logic
        return data_dict
```

## 📊 **Performance Metrics**

Portfolio-lib calculates 20+ professional metrics:

| **Returns** | **Risk** | **Trading** |
|-------------|----------|-------------|
| Total Return | Sharpe Ratio | Win Rate |
| Annualized Return | Sortino Ratio | Profit Factor |
| CAGR | Calmar Ratio | Total Trades |
| Alpha | Maximum Drawdown | Average Trade |
| Beta | Volatility | Best/Worst Trade |

## 🔧 **Configuration**

### Strategy Parameters
```python
class ConfigurableStrategy(BaseStrategy):
    def __init__(self, fast_ma=10, slow_ma=30, position_size=0.5):
        super().__init__()
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma  
        self.position_size = position_size
```

### Backtest Settings
```python
backtest = Backtest(
    strategy=strategy,
    initial_cash=100000,
    commission=0.001,  # 0.1% commission
    slippage=0.0005    # 0.05% slippage
)
```

## 🚀 **Why Portfolio-lib?**

### **🏃‍♂️ Speed & Efficiency**
- **Ultra-lightweight**: < 500KB package size
- **Minimal dependencies**: Only essential libraries
- **Optimized algorithms**: Maximum performance per operation
- **Memory efficient**: Minimal RAM usage

### **🔍 Professional Features**
- **81+ technical indicators** with professional implementations
- **Advanced risk metrics** including VaR, CVaR, drawdown analysis
- **Multi-asset support** for stocks, ETFs, forex, crypto
- **Real market data** integration via yfinance

### **🛡️ Production Ready**
- **Thoroughly tested** with comprehensive unit tests
- **Well documented** with clear examples and API reference
- **Active maintenance** by experienced quant developers
- **Community support** and regular updates

### **📈 Research Focused**
- **Academic rigor** with proper statistical implementations
- **Publication ready** results and charts
- **Extensible architecture** for custom strategies
- **Professional reporting** with detailed analytics

## 📋 **Examples & Tutorials**

### Complete Example: Momentum Strategy

```python
import pandas as pd
from portfolio_lib import BaseStrategy, Backtest, YFinanceDataFeed, TechnicalIndicators

class MomentumStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
        self.start_date = '2020-01-01'
        self.end_date = '2023-12-31'
        self.lookback = 20
        self.top_n = 2
        
    def init_indicators(self):
        print("Momentum Strategy: Buy top performing stocks")
        
    def next(self):
        if len(self.data[self.symbols[0]]) < self.lookback:
            return
            
        # Calculate momentum for each symbol
        momentum_scores = {}
        for symbol in self.symbols:
            prices = self.data[symbol]['Close']
            momentum = (prices.iloc[-1] / prices.iloc[-self.lookback] - 1) * 100
            momentum_scores[symbol] = momentum
            
        # Sort by momentum
        sorted_symbols = sorted(momentum_scores.items(), 
                              key=lambda x: x[1], reverse=True)
        
        # Close positions not in top N
        for symbol in self.symbols:
            position = self.position(symbol)
            if position and symbol not in [s[0] for s in sorted_symbols[:self.top_n]]:
                self.sell(symbol)
                
        # Open positions in top N
        for symbol, score in sorted_symbols[:self.top_n]:
            position = self.position(symbol)
            if not position:
                self.buy(symbol, 1.0 / self.top_n)

# Run the strategy
strategy = MomentumStrategy()
backtest = Backtest(strategy, initial_cash=100000)
data_feed = YFinanceDataFeed(strategy.symbols)
backtest.add_data_source(data_feed)

results = backtest.run(strategy.start_date, strategy.end_date)

# Display comprehensive results
print("🚀 MOMENTUM STRATEGY RESULTS")
print("=" * 40)
print(results.summary())

# Additional analysis
print("\\n📊 DETAILED METRICS")
print(f"Number of trades: {len(results.portfolio.trades)}")
print(f"Average position size: {100/strategy.top_n:.1f}%")
print(f"Portfolio volatility: {results.metrics.volatility:.2f}%")
print(f"Best trade return: {max([t.net_value for t in results.portfolio.trades]):,.2f}")
```

## 🤝 **Contributing**

Portfolio-lib is developed by **Rahul Ashok, Pritham Devaprasad, Siddarth S, and Anish R**. 

We welcome contributions! Please see our contributing guidelines for details on:
- Code standards and style
- Testing requirements
- Documentation guidelines
- Issue reporting

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♀️ **Support**


- **Email**: abcrahul111@gmail.com

## 🌟 **Star History**

If you find Portfolio-lib useful, please give it a star! ⭐

---

**Built with ❤️ by Rahul Ashok, Pritham Devaprasad, Siddarth S, and Anish R**

*Portfolio-lib: Where lightweight meets powerful in algorithmic trading.*