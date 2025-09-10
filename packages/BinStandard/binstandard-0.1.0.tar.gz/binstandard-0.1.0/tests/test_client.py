import asyncio
import pytest
from binstandard import BinClient

@pytest.mark.asyncio
async def test_bin_lookup():
    async with BinClient() as client:
        data = await client.get_bin_info("45717360")
        assert "scheme" in data or "error" in data

