import sys
from collections.abc import Generator
from typing import Any, cast

from stream.core import source

from ...models.parameters import DataSourceParameters, LclstreamerParameters, Parameters
from ...protocols.backend import (
    DataSourceProtocol,
    EventSourceProtocol,
    StrFloatIntNDArray,
)
from ...utils.logging_utils import log
from .data_sources import (  # noqa: F401
    GenericRandomNumpyArray,
)


class GenericEventSource(EventSourceProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self, parameters: Parameters, worker_pool_size: int, worker_rank: int
    ) -> None:
        """
        Initializes a psana1 event source

        Arguments:

            parameters: The configuration parameters

            worker_pool_size: The size of the worker pool

            worker_rank: The rank of the worker calling the function
        """
        del worker_pool_size
        del worker_rank

        lclstreamer_parameters: LclstreamerParameters = parameters.lclstreamer
        data_source_parameters: dict[str, DataSourceParameters] = (
            parameters.data_sources
        )
        if parameters.event_source.GenericEventSource is None:
            log.error(
                "GenericEventSource must be defined in event_source:"
            )
            sys.exit(1)
        self.events = parameters.event_source.GenericEventSource.events

        self._data_sources: dict[str, DataSourceProtocol] = {}
        data_source_name: str
        for data_source_name in data_source_parameters:
            try:
                data_source_class: type[DataSourceProtocol] = globals()[
                    data_source_parameters[data_source_name].type
                ]

                self._data_sources[data_source_name] = data_source_class(
                    name=data_source_name,
                    parameters=data_source_parameters[data_source_name],
                    additional_info=None,
                )
            except NameError:
                log.error(
                    f"Data source {data_source_parameters[data_source_name].type} "
                    "is not available for backend GenericEventSource"
                )
                sys.exit(1)

    @source
    def get_events(
        self,
    ) -> Generator[dict[str, StrFloatIntNDArray | None]]:
        """
        Retrieves an event from the data source

        Returns:

            data: A dictionary storing data for an event
        """
        for i in range(self.events):
            data: dict[str, StrFloatIntNDArray | None] = {}

            data_source_name: str
            for data_source_name in self._data_sources:
                try:
                    data[data_source_name] = self._data_sources[
                        data_source_name
                    ].get_data(event=i)
                except (TypeError, AttributeError):
                    data[data_source_name] = None
            yield data
