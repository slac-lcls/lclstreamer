from ..models.parameters import LclstreamerParameters, Parameters
from ..protocols.backend import EventSourceProtocol
from .psana1_event_sources import Psana1EventSource  # noqa: F401


def initialize_event_source(
    parameters: Parameters,
    node_pool_size: int,
) -> EventSourceProtocol:
    """ """

    lclstreamer_parameters: LclstreamerParameters = parameters.lclstreamer

    try:
        event_source: EventSourceProtocol = globals()[
            lclstreamer_parameters.event_source
        ](
            parameters=parameters,
            node_pool_size=node_pool_size,
        )
    except NameError:
        raise RuntimeError(
            f"Event source {lclstreamer_parameters.event_source} is not available"
        )
    return event_source
