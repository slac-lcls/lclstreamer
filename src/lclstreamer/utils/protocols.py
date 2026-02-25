from collections.abc import Generator, Iterator
from typing import Any

from stream.core import source
from typing_extensions import Protocol

from ..models.parameters import (
    DataHandlerParameters,
    DataSerializerParameters,
    DataSourceParameters,
    EventSourceParameters,
    ProcessingPipelineParameters,
)
from ..utils.typing import StrFloatIntNDArray


class EventSourceProtocol(Protocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        parameters: EventSourceParameters,
        data_source_parameters: dict[str, DataSourceParameters],
        source_identifier: str,
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


class ProcessingPipelineProtocol(Protocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        parameters: ProcessingPipelineParameters,
    ):
        """Initializes the data processing pipeline"""
        ...

    def __call__(
        self, stream: Iterator[dict[str, StrFloatIntNDArray | None]]
    ) -> Iterator[dict[str, StrFloatIntNDArray | None]]:
        """Applies the data processing pipeline"""
        ...


class DataSerializerProtocol(Protocol):
    def __init__(self, parameters: DataSerializerParameters):
        """Initializes the data serializers"""
        ...

    def __call__(
        self, stream: Iterator[dict[str, StrFloatIntNDArray | None]]
    ) -> Iterator[bytes]: ...


class DataHandlerProtocol(Protocol):
    def __init__(self, parameters: DataHandlerParameters):
        """Initializes the data handler"""
        ...

    def __call__(self, data: bytes) -> None:
        """Handles the data"""
