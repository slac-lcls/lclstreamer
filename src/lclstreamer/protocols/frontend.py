from collections.abc import Iterator

from typing_extensions import Protocol

from ..models.parameters import (
    DataHandlerParameters,
    DataSerializerParameters,
    ProcessingPipelineParameters,
)
from .backend import StrFloatIntNDArray


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
        ...
