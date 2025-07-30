import sys
from collections.abc import Generator
from typing import Any, cast

from psana import DataSource  # type: ignore
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
    Psana2AreaDetector,
    Psana2AssembledAreaDetector,
    Psana2Camera,
    Psana2EBeam,
    Psana2Gmd,
    Psana2HsdDetector,
    Psana2PV,
    Psana2Timestamp,
)


def _parse_source_identifier(source_identifier: str) -> dict[str, str | int]:
    """
    Parses a source identifier string into an argument dict
    """
    source_dict: dict[str, str | int] = {}
    source_items: list[str] = source_identifier.split(",")
    item: str
    for item in source_items:
        if item.startswith("shmem="):
            source_dict["shmem"] = item.split("shmem=")[1].strip().lstrip()
        elif item.startswith("exp="):
            source_dict["exp"] = item.split("exp=")[1].strip().lstrip()
        elif item.startswith("run="):
            source_dict["run"] = int(item.split("run=")[1].strip().lstrip())
        elif item.startswith("files="):
            source_dict["files"] = item.split("files=")[1].strip().lstrip()
        elif item.startswith("drp="):
            source_dict["drp"] = item.split("drp=")[1].strip().lstrip()
        elif item.startswith("max_events="):
            source_dict["max_events"] = int(
                item.split("max_events=")[1].strip().lstrip()
            )
        else:
            log.error("Part of the source string for psana2 cannot be parsed:")
            log.error(f"{item}")
            sys.exit(1)
    return source_dict


class Psana2EventSource(EventSourceProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self, parameters: Parameters, worker_pool_size: int, worker_rank: int
    ) -> None:
        """
        Initializes a psana2 event source

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
            log.error(
                "Shared memory mode is not currently available for the psana2 data "
                "event source"
            )
            sys.exit(1)
        else:
            data_source_arguments: dict[str, str | int] = _parse_source_identifier(
                lclstreamer_parameters.source_identifier
            )
            psana_data_source: Any = DataSource(**data_source_arguments)
            self._psana_run: Any = next(psana_data_source.runs())
            self._event_source: Any = cast(
                Generator[Any],
                self._psana_run.events(),
            )

        # self._event_source = DataSource(lclstreamer_parameters.source_identifier).events()

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
                    additional_info=self._psana_run,
                )
            except NameError:
                log.error(
                    f"Data source {data_source_parameters[data_source_name].type} "
                    "is not available for backend Psana2EventSource"
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
        psana_event: Any
        for psana_event in self._event_source:
            data: dict[str, StrFloatIntNDArray | None] = {}

            data_source_name: str
            for data_source_name in self._data_sources:
                try:
                    data[data_source_name] = self._data_sources[
                        data_source_name
                    ].get_data(event=psana_event)
                except (TypeError, AttributeError):
                    data[data_source_name] = None
            yield data
