from dataclasses import dataclass
from typing import Optional
import json


@dataclass
class ServerSettings:
    port: int
    host: str = "0.0.0.0"
    log_level: str = "INFO"
    max_order_size: int = 1000
    min_price: float = 0.01


class ConfigLoader:
    @staticmethod
    def load(config_path: str) -> ServerSettings:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            server_config = config["TradingEngineServerConfiguration"]["TradingEngineServerSettings"]
            return ServerSettings(**server_config)
