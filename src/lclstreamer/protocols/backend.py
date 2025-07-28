from collections.abc import Generator
from typing import Any, Optional, Union

import numpy
from numpy.typing import NDArray
from stream.core import source
from typing_extensions import Protocol, TypeAlias

from ..models.parameters import DataSourceParameters, Parameters

StrFloatIntNDArray: TypeAlias = Union[NDArray[numpy.str_],NDArray[numpy.float_],NDArray[numpy.int_]]


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
    def get_events(self) -> Generator[dict[str, Optional[StrFloatIntNDArray]]]:
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
        run: Any,
    ):
        """Initializes the data source"""
        ...

    def get_data(self, event: Any) -> StrFloatIntNDArray:
        """Extracts data from an event"""
        ...
