from collections.abc import Generator
from typing import Any, Union

import numpy
from numpy.typing import NDArray
from typing_extensions import Protocol, TypeAlias

from ..models.parameters import LCLStreamerParameters

StrFloatIntNDArray: TypeAlias = Union[
    NDArray[numpy.str_], NDArray[numpy.float_], NDArray[numpy.int_]
]


class EventSourceProtocol(Protocol):
    def __init__(
        self,
        *,
        source_string: str,
        node_pool_size: int,
        parameters: LCLStreamerParameters,
    ) -> None:
        """
        Initializes the event source
        """
        ...

    def get_data(self) -> Generator[dict[str, StrFloatIntNDArray]]:
        """
        Gets the next event from event source
        """
        ...


class DataSourceProtocol(Protocol):
    def __init__(
        self,
        *,
        parameters: LCLStreamerParameters,
    ):
        """Initializes the data source"""
        ...

    def get_data(self, *, event: Any) -> StrFloatIntNDArray:
        """Extracts data from an event"""
        ...
