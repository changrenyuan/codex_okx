from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal

from okx_trader import (
    AppConfig,
    ExecutionEngine,
    FeatureEngine,
    OrderBookStreamer,
    RiskManager,
    StorageManager,
    StrategyEngine,
)
from okx_trader.execution import OkxRestClient, OrderRequest


def _calc_latency_ms(message_data) -> int | None:
    data = message_data.get("data")
    if not data:
        return None
    ts = data[0].get("ts")
    if not ts:
        return None
    msg_time = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
    latency = datetime.now(tz=timezone.utc) - msg_time
    return int(latency.total_seconds() * 1000)


async def main() -> None:
    config = AppConfig.from_env()
    log_path = Path(config.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger("okx_trader")
    logger.info("Starting OKX trader in %s mode (dry_run=%s).", config.trading_mode, config.dry_run)

    proxy = config.https_proxy or config.http_proxy
    streamer = OrderBookStreamer(instrument_id="BTC-USDT", depth=400, proxy=proxy)
    feature_engine = FeatureEngine(depth=25)
    strategy_engine = StrategyEngine(
        enable_liquidation_hunting=config.enable_liquidation_hunting,
        enable_funding_arbitrage=config.enable_funding_arbitrage,
        enable_market_making=config.enable_market_making,
    )
    risk_manager = RiskManager(
        max_daily_loss=config.max_daily_loss,
        max_position_size=config.max_position_size,
        max_latency_ms=config.max_latency_ms,
    )
    storage = StorageManager()
    rest_client = OkxRestClient(
        api_key=config.okx_api_key,
        secret_key=config.okx_secret_key,
        passphrase=config.okx_passphrase,
        base_url=config.okx_base_url,
        proxy=proxy,
    )
    execution = ExecutionEngine(rest_client, dry_run=config.dry_run)

    if config.okx_api_key and config.okx_secret_key and config.okx_passphrase:
        try:
            positions = await rest_client.get_positions()
            logger.info("当前持仓信息: %s", positions)
        except Exception as exc:
            logger.warning("获取持仓信息失败: %s", exc)
    else:
        logger.warning("未配置 OKX API Key/Secret/Passphrase，跳过持仓查询。")

    try:
        eth_ticker = await rest_client.get_latest_ticker("ETH-USDT-SWAP")
        logger.info("ETH 永续合约最新价格: %s", eth_ticker)
    except Exception as exc:
        logger.warning("获取 ETH 永续合约价格失败: %s", exc)

    async def handler(orderbook, message):
        latency_ms = _calc_latency_ms(message.data)
        if latency_ms is not None:
            risk_manager.update_latency(latency_ms)
        features = feature_engine.compute(orderbook)
        storage.write_hot(
            {
                "instrument": orderbook.instrument_id,
                "features": features,
                "latency_ms": latency_ms,
            }
        )
        signals = strategy_engine.generate_signals(orderbook, features)
        if message.action in {"snapshot", "update"}:
            bids, asks = orderbook.top_levels()
            logger.info("最新订单簿(Top 5) bids=%s asks=%s", bids[:5], asks[:5])
        if not risk_manager.is_trading_allowed():
            logger.warning("Risk guard blocked trading (latency=%s).", latency_ms)
            return
        for signal in signals:
            order = OrderRequest(
                instrument_id=orderbook.instrument_id,
                side=signal.side,
                size=Decimal(signal.size),
                price=Decimal(signal.price),
            )
            result = await execution.execute(order)
            logger.info("Order executed: %s", result)
            storage.write_hot({"order": result, "reason": signal.reason})

    await streamer.run_forever(handler)


if __name__ == "__main__":
    asyncio.run(main())
