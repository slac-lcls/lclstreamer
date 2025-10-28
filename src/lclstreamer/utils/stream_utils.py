from typing import Dict, Union
from collections.abc import AsyncIterable, AsyncIterator
from time import time

#from stream.core import Stream
#from stream.ops import fold
from aiostream import stream, Stream, pipable_operator

Clock = Dict[str, Union[int, float]]

def clock0() -> Clock:
    return {
        "count": 0,
        "size": 0,
        "wait": 0,
        "time": time(),
    }

def rate_clock(
    state: Clock, sz: int
) -> Clock:
    """
    Implements a rate clock

    Arguments:

        clock: the values of the clock at the previous step of the stream
        sz: size to add to state["size"]

    Returns:

        clock: the values of the clock at the current step of the stream
    """
    t = time()
    return {
        "count": state["count"] + 1,
        "size": state["size"] + sz,
        "wait": state["wait"] + t - state["time"],
        "time": t,
    }

@pipable_operator # type: ignore[arg-type]
def clock(source: AsyncIterable[int]) -> Stream[Clock]:
    """
    Returns a rate clock counting from now.

    This transforms a stream of counts into a stream of dicts(describing the count
    rate).

    Returns:

        clock: A Stream objet
    """
    return stream.reduce(source, rate_clock, clock0()) # type: ignore[arg-type]
