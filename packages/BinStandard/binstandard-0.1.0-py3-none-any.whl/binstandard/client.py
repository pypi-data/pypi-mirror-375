import aiohttp
import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class BinClient:
    BASE_URL = "https://lookup.binlist.net"

    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def get_bin_info(self, bin_number: str) -> dict:
        url = f"{self.BASE_URL}/{bin_number}"
        async with self.session.get(url) as resp:
            if resp.status != 200:
                return {"error": f"Failed to fetch BIN info (status {resp.status})"}
            return await resp.json()

