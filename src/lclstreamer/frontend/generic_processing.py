from typing import Any

from ..models.parameters import LCLStreamerParameters
from ..protocols.backend import StrFloatIntNDArray
from ..protocols.frontend import ProcessingPipelineProtocol
from .processing_pipeline import DataStorage


class NoOpProcessingPipeline(ProcessingPipelineProtocol):

    def __init__(self, parameters: LCLStreamerParameters) -> None:
        """ """

        self._data_storage = DataStorage()

    def process_data(
        self, data: dict[str, StrFloatIntNDArray]
    ) -> dict[str, StrFloatIntNDArray]:
        """"""

        self._data_storage.add_data(data=data)

        return data

    def collect_results(
        self, data: dict[str, StrFloatIntNDArray]
    ) -> dict[str, StrFloatIntNDArray]:

        results: dict[str, StrFloatIntNDArray] = (
            self._data_storage.retrieve_stored_data()
        )
        self._data_storage.reset_data_storage()

        return results
