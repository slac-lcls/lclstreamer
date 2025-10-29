import sys
from ast import Import
from collections.abc import AsyncIterable

from aiostream import operator

from ..models.parameters import LclstreamerParameters, Parameters
from ..models.types import LossyEvent
from ..protocols.backend import EventSourceProtocol
from ..utils.logging_utils import log

from .generic.event_sources import InternalEventSource

try:
    from psana import MPIDataSource  # type: ignore

    from .psana1.event_sources import Psana1EventSource  # noqa: F401
except ImportError:
    pass

try:
    from .psana2.event_sources import Psana2EventSource  # noqa: F401
except ImportError:
    pass


def initialize_event_source(
    parameters: Parameters,
    worker_pool_size: int,
    worker_rank: int,
) -> EventSourceProtocol:
    """
    Initializes the Event Source specified by the configuration parameters

    Arguments:

        parameters: The configuration parameters

        worker_pool_size: The size of the worker pool

        worker_rank: The rank of the worker calling the function

    Returns:

        event_source: The initialized event source
    """
    event_source: EventSourceProtocol = globals()[
        parameters.event_source.type
    ](
        parameters=parameters,
        worker_pool_size=worker_pool_size,
        worker_rank=worker_rank,
    )
    return event_source
