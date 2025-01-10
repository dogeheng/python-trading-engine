from abc import ABC, abstractmethod
import pandas as pd
import numpy as np


class TradingStrategy(ABC):
    """Base class for all trading strategies"""

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals for the given data"""
        pass

    def calculate_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate strategy returns based on signals"""
        # Calculate daily returns
        data['Returns'] = data['Close'].pct_change()

        # Calculate position (this will maintain the position between signals)
        data['Position'] = data['Signal'].fillna(0)
        data['Position'] = data['Position'].replace(
            to_replace=0, method='ffill')

        # Calculate strategy returns (using the position from the previous day)
        data['Strategy_Returns'] = data['Position'].shift(1) * data['Returns']

        # Calculate cumulative returns starting from 1
        data['Cumulative_Returns'] = (1 + data['Strategy_Returns']).cumprod()

        return data


class SMAStrategy(TradingStrategy):
    """Simple Moving Average Crossover Strategy"""

    def __init__(self, short_window: int = 20, long_window: int = 50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # Calculate moving averages
        data['SMA_Short'] = data['Close'].rolling(
            window=self.short_window).mean()
        data['SMA_Long'] = data['Close'].rolling(
            window=self.long_window).mean()

        # Initialize signals
        data['Signal'] = 0

        # Generate signals only when both MAs are available
        valid_data = data.dropna(subset=['SMA_Short', 'SMA_Long'])

        for idx in valid_data.index:
            if data.loc[idx, 'SMA_Short'] > data.loc[idx, 'SMA_Long']:
                data.loc[idx, 'Signal'] = 1  # Buy signal
            elif data.loc[idx, 'SMA_Short'] < data.loc[idx, 'SMA_Long']:
                data.loc[idx, 'Signal'] = -1  # Sell signal

        return self.calculate_returns(data)


class RSIStrategy(TradingStrategy):
    """Relative Strength Index Strategy"""

    def __init__(self, period: int = 14, overbought: float = 70, oversold: float = 30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def calculate_rsi(self, data: pd.DataFrame) -> pd.Series:
        """Calculate RSI with handling for division by zero"""
        delta = data['Close'].diff()

        # Separate gains and losses
        gains = delta.copy()
        losses = delta.copy()

        gains[gains < 0] = 0
        losses[losses > 0] = 0
        losses = abs(losses)

        # Calculate average gains and losses
        avg_gains = gains.rolling(window=self.period, min_periods=1).mean()
        avg_losses = losses.rolling(window=self.period, min_periods=1).mean()

        # Calculate RS and RSI
        rs = pd.Series(index=data.index, dtype=float)
        rsi = pd.Series(index=data.index, dtype=float)

        # Handle division by zero
        valid_losses = avg_losses != 0
        rs[valid_losses] = avg_gains[valid_losses] / avg_losses[valid_losses]
        rs[~valid_losses] = 100.0  # When no losses, RSI should be 100

        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        data['RSI'] = self.calculate_rsi(data)
        data['Signal'] = 0

        # Generate signals based on RSI values
        data.loc[data['RSI'] < self.oversold, 'Signal'] = 1  # Buy signal
        data.loc[data['RSI'] > self.overbought, 'Signal'] = -1  # Sell signal

        return self.calculate_returns(data)


class MACDStrategy(TradingStrategy):
    """Moving Average Convergence Divergence Strategy"""

    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate_macd(self, data: pd.DataFrame) -> tuple:
        # Calculate the MACD line
        exp1 = data['Close'].ewm(span=self.fast_period, adjust=False).mean()
        exp2 = data['Close'].ewm(span=self.slow_period, adjust=False).mean()
        macd = exp1 - exp2

        # Calculate the signal line
        signal = macd.ewm(span=self.signal_period, adjust=False).mean()

        # Calculate MACD histogram
        hist = macd - signal

        return macd, signal, hist

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # Calculate MACD components
        data['MACD'], data['Signal_line'], data['MACD_hist'] = self.calculate_macd(
            data)

        # Initialize signals
        data['Signal'] = 0

        # Generate signals when MACD crosses Signal line
        data.loc[data['MACD'] > data['Signal_line'],
                 'Signal'] = 1  # Buy signal
        data.loc[data['MACD'] < data['Signal_line'],
                 'Signal'] = -1  # Sell signal

        return self.calculate_returns(data)


# Strategy factory
STRATEGIES = {
    'SMA Crossover': SMAStrategy,
    'RSI Strategy': RSIStrategy,
    'MACD Strategy': MACDStrategy
}


def get_strategy(name: str, **kwargs) -> TradingStrategy:
    """Get strategy instance by name"""
    strategy_class = STRATEGIES.get(name)
    if strategy_class is None:
        raise ValueError(f"Strategy '{name}' not found")
    return strategy_class(**kwargs)
