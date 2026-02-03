from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


def load_env(path: Optional[str] = None) -> None:
    if path:
        load_dotenv(path)
    else:
        load_dotenv()


@dataclass
class AppConfig:
    okx_api_key: str
    okx_secret_key: str
    okx_passphrase: str
    okx_base_url: str
    max_position_size: float
    max_daily_loss: float
    leverage_limit: int
    timeout: int
    enable_liquidation_hunting: bool
    enable_funding_arbitrage: bool
    enable_market_making: bool
    ws_reconnect_delay: int
    ws_ping_interval: int
    max_latency_ms: int
    dry_run: bool
    trading_mode: str
    log_level: str
    log_file: str
    http_proxy: str | None
    https_proxy: str | None

    @classmethod
    def from_env(cls) -> "AppConfig":
        load_env()
        return cls(
            okx_api_key=os.getenv("OKX_API_KEY", ""),
            okx_secret_key=os.getenv("OKX_SECRET_KEY", ""),
            okx_passphrase=os.getenv("OKX_PASSPHRASE", ""),
            okx_base_url=os.getenv("OKX_BASE_URL", "https://www.okx.com"),
            max_position_size=float(os.getenv("MAX_POSITION_SIZE", "1000")),
            max_daily_loss=float(os.getenv("MAX_DAILY_LOSS", "0.05")),
            leverage_limit=int(os.getenv("LEVERAGE_LIMIT", "20")),
            timeout=int(os.getenv("TIMEOUT", "30")),
            enable_liquidation_hunting=os.getenv("ENABLE_LIQUIDATION_HUNTING", "true").lower() == "true",
            enable_funding_arbitrage=os.getenv("ENABLE_FUNDING_ARBITRAGE", "true").lower() == "true",
            enable_market_making=os.getenv("ENABLE_MARKET_MAKING", "false").lower() == "true",
            ws_reconnect_delay=int(os.getenv("WS_RECONNECT_DELAY", "5")),
            ws_ping_interval=int(os.getenv("WS_PING_INTERVAL", "20")),
            max_latency_ms=int(os.getenv("MAX_LATENCY_MS", "500")),
            dry_run=os.getenv("DRY_RUN", "true").lower() == "true",
            trading_mode=os.getenv("TRADING_MODE", "paper"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "logs/validation.log"),
            http_proxy=os.getenv("HTTP_PROXY") or None,
            https_proxy=os.getenv("HTTPS_PROXY") or None,
        )
