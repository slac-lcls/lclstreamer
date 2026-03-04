from time import time
from typing import Any, Dict, Union

from stream.core import Stream
from stream.ops import fold

Clock = Dict[str, Union[int, float]]


def _clock_init() -> Clock:
    # Returns the initial state of a rate clock

    return {
        "count": 0,
        "size": 0,
        "wait": 0,
        "time": time(),
    }


def _rate_clock(state: Clock, sz: int) -> Clock:
    # Implements a rate clock for a data stream
    # sz is the size to add in the current step

    t = time()
    return {
        "count": state["count"] + 1,
        "size": state["size"] + sz,
        "wait": state["wait"] + t - state["time"],
        "time": t,
    }


def clock() -> Stream[Any, Any]:
    """
    Returns a rate clock counting from now

    This transforms a stream of counts into a stream of dicts (describing the count
    rate)

    Returns:

        clock: A Stream objet
    """
    return fold(_rate_clock, _clock_init())
