import sys
from collections.abc import Generator
from typing import Any, cast

from psana import DataSource, MPIDataSource  # type: ignore
from stream.core import source

from ...models.parameters import DataSourceParameters, LclstreamerParameters, Parameters
from ...protocols.backend import (
    DataSourceProtocol,
    EventSourceProtocol,
    StrFloatIntNDArray,
)
from ...utils.logging_utils import log
from ..generic.data_sources import GenericRandomNumpyArray  # noqa: F401
from .data_sources import (  # noqa: F401
    Psana1AreaDetector,
    Psana1BbmonDetector,
    Psana1IpmDetector,
    Psana1PV,
    Psana1Timestamp,
)


class Psana1EventSource(EventSourceProtocol):
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

        if "shmem" in lclstreamer_parameters.source_identifier:
            self._event_source: Generator[Any] = cast(
                Generator[Any],
                DataSource(lclstreamer_parameters.source_identifier).events(),
            )
        else:
            psana_source_string: str = lclstreamer_parameters.source_identifier
            if not psana_source_string.endswith(":smd"):
                psana_source_string = f"{psana_source_string}:smd"
            self._event_source = cast(
                Generator[Any],
                MPIDataSource(psana_source_string).events(),
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
                )
            except NameError:
                log.error(
                    f"Data source {data_source_name} is not available for backend "
                    "PsanaEventSource"
                )
                sys.exit(1)

    @source
    def get_events(
        self,
    ) -> Generator[dict[str, StrFloatIntNDArray]]:
        """
        Retrieves an event from the data source

        Returns:

            data: A dictionary storing data for a an event
        """
        psana_event: Any
        for psana_event in self._event_source:
            data: dict[str, StrFloatIntNDArray] = {}

            data_source_name: str
            for data_source_name in self._data_sources:
                data[data_source_name] = self._data_sources[data_source_name].get_data(
                    event=psana_event
                )

            yield data
