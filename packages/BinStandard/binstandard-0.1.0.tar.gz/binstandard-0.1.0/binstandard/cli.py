import asyncio
import uvloop
import argparse
from .client import BinClient

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def main():
    parser = argparse.ArgumentParser(description="BinStandard CLI - Fetch BIN info from binlist.net")
    parser.add_argument("bin", help="BIN number to lookup")
    args = parser.parse_args()

    async with BinClient() as client:
        data = await client.get_bin_info(args.bin)
        print(data)

def cli():
    asyncio.run(main())

