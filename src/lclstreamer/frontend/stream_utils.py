from time import time
from typing import Any, Callable, Union

from stream.core import Stream
from stream.ops import fold

clock0: Callable[[], dict[str, Union[int, float]]] = lambda: {
    "count": 0,
    "size": 0,
    "wait": 0,
    "time": time(),
}


def rate_clock(
    state: dict[str, Union[int, float]], sz: int
) -> dict[str, Union[int, float]]:

    t = time()
    return {
        "count": state["count"] + 1,
        "size": state["size"] + sz,
        "wait": state["wait"] + t - state["time"],
        "time": t,
    }


def clock() -> Stream[Any, Any]:
    """Return a rate-clock counting from now.
    This transforms a stream of counts into a stream
    of dicts (describing the count rate).
    """
    return fold(rate_clock, clock0())
