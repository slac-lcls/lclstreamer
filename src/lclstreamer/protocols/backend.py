from collections.abc import Generator
from typing import Any, Union

import numpy
from numpy.typing import NDArray
from stream.core import source
from typing_extensions import Protocol, TypeAlias

from ..models.parameters import DataSourceParameters, Parameters

StrFloatIntNDArray: TypeAlias = Union[
    NDArray[numpy.str_], NDArray[numpy.float_], NDArray[numpy.int_]
]


class EventSourceProtocol(Protocol):
    def __init__(
        self,
        node_pool_size: int,
        parameters: Parameters,
    ) -> None:
        """
        Initializes the event source
        """
        ...

    @source
    def get_events(self) -> Generator[dict[str, StrFloatIntNDArray]]:
        """
        Gets the next event from event source
        """
        ...


class DataSourceProtocol(Protocol):
    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
    ):
        """Initializes the data source"""
        ...

    def get_data(self, event: Any) -> StrFloatIntNDArray:
        """Extracts data from an event"""
        ...
