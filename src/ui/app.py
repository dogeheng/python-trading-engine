from src.core.order import Order, OrderSide
from src.config.settings import ConfigLoader
from src.server.trading_server import TradingServer
from src.ui.strategies import get_strategy, STRATEGIES
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add the project root to the Python path
root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


class TradingUI:
    def __init__(self):
        self.config = ConfigLoader.load("appsettings.json")
        self.server = TradingServer(self.config)

    def load_stock_data(self, symbol: str, period: str = "1y"):
        """Load stock data from Yahoo Finance"""
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        return hist

    def run_backtest(self, symbol: str, strategy_name: str, strategy_params: dict, period: str = "1y"):
        """Run backtest for selected strategy"""
        data = self.load_stock_data(symbol, period)

        # Get strategy instance with parameters
        strategy = get_strategy(strategy_name, **strategy_params)

        # Run strategy and get results
        results = strategy.generate_signals(data)

        return results


def main():
    st.set_page_config(page_title="Trading Engine UI", layout="wide")
    st.title("Trading Engine Interface")

    # Initialize the trading UI
    trading_ui = TradingUI()

    # Sidebar for configuration
    st.sidebar.header("Configuration")

    # Strategy selection
    strategy = st.sidebar.selectbox(
        "Select Trading Strategy",
        list(STRATEGIES.keys())
    )

    # Strategy parameters
    st.sidebar.subheader("Strategy Parameters")
    strategy_params = {}

    if strategy == "SMA Crossover":
        strategy_params['short_window'] = st.sidebar.slider(
            "Short Window", 5, 50, 20)
        strategy_params['long_window'] = st.sidebar.slider(
            "Long Window", 20, 200, 50)
    elif strategy == "RSI Strategy":
        strategy_params['period'] = st.sidebar.slider("RSI Period", 2, 30, 14)
        strategy_params['overbought'] = st.sidebar.slider(
            "Overbought Level", 50, 90, 70)
        strategy_params['oversold'] = st.sidebar.slider(
            "Oversold Level", 10, 50, 30)
    elif strategy == "MACD Strategy":
        strategy_params['fast_period'] = st.sidebar.slider(
            "Fast Period", 5, 20, 12)
        strategy_params['slow_period'] = st.sidebar.slider(
            "Slow Period", 20, 40, 26)
        strategy_params['signal_period'] = st.sidebar.slider(
            "Signal Period", 5, 15, 9)

    # Stock selection
    symbol = st.sidebar.text_input("Enter Stock Symbol", "AAPL")

    # Time period selection
    period = st.sidebar.selectbox(
        "Select Time Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
    )

    # Run backtest button
    if st.sidebar.button("Run Backtest"):
        with st.spinner("Running backtest..."):
            try:
                # Load data and run backtest with strategy parameters
                results = trading_ui.run_backtest(
                    symbol, strategy, strategy_params, period)

                if results is not None:
                    # Create tabs for different views
                    tab1, tab2, tab3 = st.tabs(
                        ["Chart", "Performance", "Trade Log"])

                    with tab1:
                        # Create price chart
                        fig = go.Figure()

                        # Add candlestick chart
                        fig.add_trace(go.Candlestick(
                            x=results.index,
                            open=results['Open'],
                            high=results['High'],
                            low=results['Low'],
                            close=results['Close'],
                            name="OHLC"
                        ))

                        # Add strategy-specific indicators
                        if strategy == "SMA Crossover":
                            fig.add_trace(go.Scatter(
                                x=results.index,
                                y=results['SMA_Short'],
                                name=f"SMA{strategy_params['short_window']}",
                                line=dict(color='orange')
                            ))
                            fig.add_trace(go.Scatter(
                                x=results.index,
                                y=results['SMA_Long'],
                                name=f"SMA{strategy_params['long_window']}",
                                line=dict(color='blue')
                            ))
                        elif strategy == "RSI Strategy":
                            # Create a secondary y-axis for RSI
                            fig.add_trace(go.Scatter(
                                x=results.index,
                                y=results['RSI'],
                                name="RSI",
                                yaxis="y2"
                            ))
                            # Add overbought/oversold lines
                            fig.add_hline(
                                y=strategy_params['overbought'],
                                line=dict(color='red', dash='dash'),
                                yref="y2"
                            )
                            fig.add_hline(
                                y=strategy_params['oversold'],
                                line=dict(color='green', dash='dash'),
                                yref="y2"
                            )
                        elif strategy == "MACD Strategy":
                            # Add MACD subplot
                            fig.add_trace(go.Scatter(
                                x=results.index,
                                y=results['MACD'],
                                name="MACD",
                                yaxis="y2"
                            ))
                            fig.add_trace(go.Scatter(
                                x=results.index,
                                y=results['Signal_line'],
                                name="Signal Line",
                                yaxis="y2"
                            ))
                            # Add MACD histogram
                            fig.add_trace(go.Bar(
                                x=results.index,
                                y=results['MACD_hist'],
                                name="MACD Histogram",
                                yaxis="y2"
                            ))

                        # Update layout based on strategy
                        layout_updates = {
                            "title": f"{symbol} - {strategy}",
                            "yaxis": {"title": "Price", "side": "left"},
                            "xaxis": {"title": "Date"},
                            "height": 800,  # Make the chart taller
                            "showlegend": True,
                            # Move legend outside
                            "legend": {"x": 1.05, "y": 1}
                        }

                        if strategy in ["RSI Strategy", "MACD Strategy"]:
                            layout_updates.update({
                                "yaxis2": {
                                    "title": "RSI" if strategy == "RSI Strategy" else "MACD",
                                    "overlaying": "y",
                                    "side": "right",
                                    "showgrid": False
                                }
                            })

                        fig.update_layout(**layout_updates)
                        st.plotly_chart(fig, use_container_width=True)

                    with tab2:
                        # Performance metrics
                        st.subheader("Performance Metrics")
                        col1, col2, col3 = st.columns(3)

                        total_return = (
                            results['Cumulative_Returns'].iloc[-1] - 1) * 100
                        sharpe_ratio = (results['Strategy_Returns'].mean(
                        ) / results['Strategy_Returns'].std()) * (252 ** 0.5)
                        max_drawdown = (
                            results['Cumulative_Returns'] / results['Cumulative_Returns'].cummax() - 1).min() * 100

                        col1.metric("Total Return", f"{total_return:.2f}%")
                        col2.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
                        col3.metric("Max Drawdown", f"{max_drawdown:.2f}%")

                        # Plot cumulative returns
                        fig_returns = go.Figure()
                        fig_returns.add_trace(go.Scatter(
                            x=results.index,
                            y=results['Cumulative_Returns'],
                            name="Strategy Returns"
                        ))
                        fig_returns.update_layout(
                            title="Cumulative Returns",
                            yaxis_title="Returns",
                            xaxis_title="Date"
                        )
                        st.plotly_chart(fig_returns, use_container_width=True)

                    with tab3:
                        # Trading signals log
                        st.subheader("Trading Signals")
                        signals_df = results[[
                            'Close', 'Signal', 'Strategy_Returns']].copy()
                        signals_df['Position'] = signals_df['Signal'].map(
                            {1: 'Buy', -1: 'Sell', 0: 'Hold'})
                        st.dataframe(signals_df.tail(10))

            except Exception as e:
                st.error(f"Error running backtest: {str(e)}")

    # Display real-time stock info
    if symbol:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            st.subheader("Stock Information")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Current Price",
                          f"${info.get('currentPrice', 'N/A')}")
            with col2:
                st.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}")
            with col3:
                st.metric("Volume", f"{info.get('volume', 'N/A'):,}")
        except Exception as e:
            st.warning(f"Could not fetch real-time data for {symbol}")


if __name__ == "__main__":
    main()
