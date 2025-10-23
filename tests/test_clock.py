import pytest
from aiostream import stream

from lclstreamer.utils.stream_utils import clock

@pytest.mark.asyncio
async def test_clock():
    src = stream.count(interval=0.001)[1:100:3]
    src |= clock.pipe()
    async with src.stream() as streamer:
        async for c in streamer:
            print(c)
    assert c["wait"] >= 0.001*30
