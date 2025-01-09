import asyncio
import signal
from pathlib import Path
from src.config.settings import ConfigLoader
from src.utils.logger import LoggerSetup
from src.server.trading_server import TradingServer
from src.core.order import Order, OrderSide


async def main():
    # Load configuration
    config = ConfigLoader.load("appsettings.json")

    # Setup logging
    LoggerSetup.setup(
        level=config.log_level,
        log_file="trading_server.log"
    )

    # Create and start the trading server
    server = TradingServer(config)

    # Handle shutdown signals
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig, lambda: asyncio.create_task(server.stop()))

    try:
        await server.start()

        # Add some test orders
        server.add_order(
            Order("B1", price=100.0, quantity=10, side=OrderSide.BUY))
        server.add_order(
            Order("S1", price=100.0, quantity=5, side=OrderSide.SELL))

        # Keep the server running
        while True:
            await asyncio.sleep(1)
    finally:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
