from __future__ import annotations

import asyncio

import aiohttp

from okx_trader.config import AppConfig


async def main() -> None:
    config = AppConfig.from_env()
    url = f"{config.okx_base_url.rstrip('/')}/api/v5/public/time"
    proxy = config.https_proxy or config.http_proxy
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=config.timeout, proxy=proxy) as resp:
            data = await resp.json()
            print(data)


if __name__ == "__main__":
    asyncio.run(main())
