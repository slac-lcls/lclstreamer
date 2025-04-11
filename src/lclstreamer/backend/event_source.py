from ..models.parameters import LclstreamerParameters, Parameters
from ..protocols.backend import EventSourceProtocol
from .psana1.event_sources import Psana1EventSource  # noqa: F401


def initialize_event_source(
    parameters: Parameters,
    worker_pool_size: int,
    worker_rank: int,
) -> EventSourceProtocol:
    """
    Initializes the event source specified by the configuration parameters

    Arguments:

        parameters: The configuration parameters

        worker_pool_size: The size of the worker pool

        worker_rank: The rank of the worker calling the function

    Returns:

        event_source: The initialized event source
    """
    lclstreamer_parameters: LclstreamerParameters = parameters.lclstreamer

    try:
        event_source: EventSourceProtocol = globals()[
            lclstreamer_parameters.event_source
        ](
            parameters=parameters,
            worker_pool_size=worker_pool_size,
            worker_rank=worker_rank,
        )
    except NameError:
        raise RuntimeError(
            f"Event source {lclstreamer_parameters.event_source} is not available"
        )
    return event_source
