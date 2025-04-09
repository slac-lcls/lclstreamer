from collections.abc import Generator
from typing import Any, cast

from psana import DataSource, MPIDataSource  # type: ignore

from ..models.parameters import LCLStreamerParameters
from ..protocols.backend import (
    DataSourceProtocol,
    EventSourceProtocol,
    StrFloatIntNDArray,
)
from .psana1_data_sources import Psana1Timestamp  # noqa: F401


class Psana1EventSource(EventSourceProtocol):
    def __init__(
        self,
        *,
        source_string: str,
        node_pool_size: int,
        parameters: LCLStreamerParameters,
    ) -> None:
        """"""
        if "shmem" in source_string:
            self._event_source: Generator[Any] = cast(
                Generator[Any], DataSource(source_string)
            )
        else:
            if not source_string.endswith(":smd"):
                source_string = f"{source_string}:smd"
            self._event_source = cast(Generator[Any], MPIDataSource(source_string))

        self._data_sources: dict[str, DataSourceProtocol] = {}
        data_source_name: str
        for data_source_name in parameters.data_sources:
            try:
                data_source_class: type[DataSourceProtocol] = globals()[
                    data_source_name
                ]
                self._data_sources[data_source_name] = data_source_class(
                    parameters=parameters
                )
            except NameError:
                raise RuntimeError(
                    f"Data source {data_source_name} is not available for backend "
                    "PsanaEventSource"
                )

    def get_events(
        self,
    ) -> Generator[dict[str, StrFloatIntNDArray]]:
        """"""
        psana_event: Any
        for psana_event in self._event_source:
            data: dict[str, StrFloatIntNDArray] = {}

            data_source_name: str
            for data_source_name in self._data_sources:
                data[data_source_name] = self._data_sources[data_source_name].get_data(
                    event=psana_event
                )

            yield data
