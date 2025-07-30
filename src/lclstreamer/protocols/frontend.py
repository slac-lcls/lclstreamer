from collections.abc import Iterator

from typing_extensions import Protocol

from ..models.parameters import Parameters
from .backend import StrFloatIntNDArray


class ProcessingPipelineProtocol(Protocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        parameters: Parameters,
    ):
        """Initializes the data processing pipeline"""
        ...

    def __call__(
        self, stream: Iterator[dict[str, StrFloatIntNDArray | None]]
    ) -> Iterator[dict[str, StrFloatIntNDArray | None]]:
        """Applies the data processing pipeline"""
        ...


class DataSerializerProtocol(Protocol):
    def __init__(self, parameters: Parameters):
        """Initializes the data serializers"""
        ...

    def serialize_data(self, data: dict[str, StrFloatIntNDArray]) -> bytes:
        """Serializes the data"""
        ...


class DataHandlerProtocol(Protocol):
    def __init__(self, parameters: Parameters):
        """Initializes the data handler"""
        ...

    def handle_data(self, data: bytes) -> None:
        """Handles the data"""
        ...
