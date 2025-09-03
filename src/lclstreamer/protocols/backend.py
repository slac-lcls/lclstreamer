from collections.abc import Generator
from typing import Any

import numpy
from numpy.typing import NDArray
from stream.core import source
from typing_extensions import Protocol, TypeAlias

from ..models.parameters import DataSourceParameters, Parameters

StrFloatIntNDArray: TypeAlias = NDArray[numpy.str_ | numpy.float64 | numpy.int_]


class EventSourceProtocol(Protocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        parameters: Parameters,
        worker_pool_size: int,
        worker_rank: int,
    ):
        """
        Initializes the event source
        """
        ...

    @source
    def get_events(self) -> Generator[dict[str, StrFloatIntNDArray | None]]:
        """
        Gets the next event from event source
        """
        ...


class DataSourceProtocol(Protocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
        additional_info: dict[str, Any],
    ):
        """Initializes the data source"""
        ...

    def get_data(self, event: Any) -> StrFloatIntNDArray:
        """Extracts data from an event"""
        ...
