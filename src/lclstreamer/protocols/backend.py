from typing import Any
from collections.abc import AsyncIterable, Iterable
from typing_extensions import Protocol

from aiostream.core import Stream
import numpy

from ..models.parameters import DataSourceParameters, Parameters
from ..models.types import StrFloatIntNDArray, LossyEvent


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

    def get_events(self) -> AsyncIterable[LossyEvent]:
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
