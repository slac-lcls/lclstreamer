from typing import Any

import numpy
from numpy.typing import NDArray
from psana import EventId  # type: ignore

from ..models.parameters import LCLStreamerParameters
from ..protocols.backend import DataSourceProtocol


class Psana1Timestamp(DataSourceProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        *,
        parameters: LCLStreamerParameters,
    ):
        """
        Intialized recovery of timestamp information from psana.

        No initialization needed, the function does nothing
        """

    def get_data(self, *, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves timestamp information for an event
        """
        psana_event_id: Any = event.get(
            EventId  # pyright: ignore[reportAttributeAccessIssue]
        )
        timestamp_epoch_format: Any = psana_event_id.time()
        return numpy.array(
            numpy.float64(
                str(timestamp_epoch_format[0]) + "." + str(timestamp_epoch_format[1])
            )
        )
