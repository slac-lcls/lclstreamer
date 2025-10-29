import sys
from collections.abc import AsyncIterable

from ...models.parameters import DataSourceParameters, LclstreamerParameters, Parameters
from ...models.types import LossyEvent
from ...protocols.backend import (
    DataSourceProtocol,
    EventSourceProtocol,
    StrFloatIntNDArray,
)
from ...utils.logging_utils import log
from .data_sources import GenericRandomNumpyArray  # noqa: F401


class InternalEventSource(EventSourceProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self, parameters: Parameters, worker_pool_size: int, worker_rank: int
    ) -> None:
        """
        Initializes an internal event source

        This event source does not rely on any external framework to generate events
        and is only compatible with data sources that don't use any external
        framework to generate data. It is intended mainly for testing

        Arguments:

            parameters: The configuration parameters

            worker_pool_size: The size of the worker pool

            worker_rank: The rank of the worker calling the function
        """
        del worker_pool_size
        del worker_rank

        data_source_parameters: dict[str, DataSourceParameters] = (
            parameters.data_sources
        )
        if parameters.event_source.type != "InternalEventSource":
            log.error(f"Tried to initialize an InternalEventSource from a {parameters.event_source.type}!")
            sys.exit(1)
        self.number_of_events_to_generate = (
            parameters.event_source.number_of_events_to_generate
        )

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
                    additional_info={
                        "source_identifier": parameters.lclstreamer.source_identifier
                    },
                )
            except NameError:
                log.error(
                    f"Data source {data_source_parameters[data_source_name].type} "
                    "is not available for backend InternalEventSource"
                )
                sys.exit(1)

    async def get_events(
        self,
    ) -> AsyncIterable[LossyEvent]:
        """
        Retrieves an event from the data source
        Returns:
            data: A dictionary storing data for an event
        """
        for i in range(self.number_of_events_to_generate):

            data: LossyEvent = {}
            data_source_name: str

            for data_source_name in self._data_sources:
                try:
                    data[data_source_name] = self._data_sources[
                        data_source_name
                    ].get_data(event=i)
                except (TypeError, AttributeError):
                    data[data_source_name] = None
            yield data
