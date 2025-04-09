from typing_extensions import Protocol

from ..models.parameters import LCLStreamerParameters
from .backend import StrFloatIntNDArray


class ProcessingPipelineProtocol(Protocol):
    def __init__(
        self,
        *,
        parameters: LCLStreamerParameters,
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
