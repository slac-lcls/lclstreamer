from collections.abc import (
    Generator,
)
from typing import Any, cast

from psana import DataSource, MPIDataSource  # type: ignore
from stream.core import source

from ..models.parameters import DataSourceParameters, LclstreamerParameters, Parameters
from ..protocols.backend import (
    DataSourceProtocol,
    EventSourceProtocol,
    StrFloatIntNDArray,
)
from .psana1_data_sources import Psana1AreaDetector, Psana1Timestamp  # noqa: F401


class Psana1EventSource(EventSourceProtocol):
    def __init__(self, parameters: Parameters, node_pool_size: int) -> None:
        """"""
        del node_pool_size

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
                raise RuntimeError(
                    f"Data source {data_source_name} is not available for backend "
                    "PsanaEventSource"
                )

    @source
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
