from ..models.parameters import Parameters
from ..utils.logging import log_error_and_exit
from ..utils.protocols import EventSourceProtocol
from .generic.event_sources import InternalEventSource as InternalEventSource

try:
    from psana import (
        MPIDataSource as MPIDataSource,  # pyright: ignore[reportUnusedImport, reportUnknownVariableType]
    )

    from .psana1.event_sources import Psana1EventSource as Psana1EventSource
except ImportError:
    pass

try:
    from .psana2.event_sources import Psana2EventSource as Psana2EventSource
except ImportError:
    pass


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
    try:
        event_source: EventSourceProtocol = globals()[parameters.event_source.type](
            parameters=parameters.event_source,
            data_source_parameters=parameters.data_sources,
            source_identifier=parameters.source_identifier,
            worker_pool_size=worker_pool_size,
            worker_rank=worker_rank,
        )
    except NameError:
        log_error_and_exit(
            f"Event source {parameters.event_source.type} is not available"
        )

    return event_source
