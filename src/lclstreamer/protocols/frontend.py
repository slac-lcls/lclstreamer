from typing_extensions import Protocol

from ..models.parameters import Parameters
from .backend import StrFloatIntNDArray


class ProcessingPipelineProtocol(Protocol):
    def __init__(
        self,
        parameters: Parameters,
    ):
        """Initializes the data processing pipeline"""
        ...

    def process_data(
        self, data: dict[str, StrFloatIntNDArray]
    ) -> dict[str, StrFloatIntNDArray]:
        """Processes single data events and stores the results"""
        ...

    def collect_results(
        self, data: dict[str, StrFloatIntNDArray]
    ) -> dict[str, StrFloatIntNDArray]:
        """Collects the stored processing results"""
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
