# Python Trading Engine

A comprehensive trading engine with backtesting capabilities and an interactive web interface.

## Features

- **Interactive Web Interface**: Built with Streamlit for easy visualization and interaction
- **Multiple Trading Strategies**:
  - SMA (Simple Moving Average) Crossover
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
- **Real-time Data**: Integration with Yahoo Finance API
- **Advanced Backtesting**:
  - Performance metrics (Total Return, Sharpe Ratio, Max Drawdown)
  - Interactive charts with technical indicators
  - Trading signals visualization
- **Customizable Parameters**: Adjust strategy parameters in real-time

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Sam-superlab/python-trading-engine.git
cd python-trading-engine
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Trading Server
To run the main trading server:
```bash
python main.py
```

### Running the Web Interface
To start the interactive web interface:
```bash
streamlit run src/ui/app.py
```

The web interface will be available at http://localhost:8501

### Using the Web Interface

1. **Select a Trading Strategy**:
   - Choose from SMA Crossover, RSI, or MACD strategies
   - Adjust strategy parameters using the sliders

2. **Choose a Stock**:
   - Enter any valid stock symbol (e.g., AAPL, GOOGL)
   - Select the time period for analysis

3. **Run Backtest**:
   - Click "Run Backtest" to see the results
   - View performance metrics and trading signals
   - Analyze the interactive charts

## Project Structure

```
python-trading-engine/
├── src/
│   ├── config/         # Configuration settings
│   ├── core/           # Core trading functionality
│   ├── server/         # Trading server implementation
│   ├── ui/             # Web interface components
│   └── utils/          # Utility functions
├── main.py             # Main server entry point
└── requirements.txt    # Project dependencies
```

## Trading Strategies

### SMA Crossover
- Uses two moving averages (short and long-term)
- Generates buy signals when short MA crosses above long MA
- Generates sell signals when short MA crosses below long MA
- Customizable window periods

### RSI Strategy
- Measures overbought and oversold conditions
- Generates buy signals when RSI drops below oversold level
- Generates sell signals when RSI rises above overbought level
- Adjustable RSI period and threshold levels

### MACD Strategy
- Combines trend-following and momentum indicators
- Generates buy signals when MACD crosses above signal line
- Generates sell signals when MACD crosses below signal line
- Customizable fast, slow, and signal periods

## Performance Metrics

- **Total Return**: Overall strategy performance
- **Sharpe Ratio**: Risk-adjusted return metric
- **Maximum Drawdown**: Largest peak-to-trough decline

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the open-source community for providing valuable tools and 
libraries
- Special thanks to my love Risa for her support and encouragement