import sys
from collections.abc import Iterator
from stream.core import stream

from ...models.parameters import ProcessingPipelineParameters
from ...protocols.backend import StrFloatIntNDArray
from ...protocols.frontend import ProcessingPipelineProtocol
from ...utils.logging_utils import log
from .utils import DataStorage


class BatchProcessingPipeline(ProcessingPipelineProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(self, parameters: ProcessingPipelineParameters) -> None:
        """
        Initializes a batching pipeline

        This pipeline accumulates data into batches

        Arguments:

            parameters: The configuration parameters
        """
        if parameters.BatchProcessingPipeline is None:
            log.error("No configuration parameters found for BatchProcessingPipeline")
            sys.exit(1)
        self._batch_size: int = parameters.BatchProcessingPipeline.batch_size

    def __call__(
        self, stream: Iterator[dict[str, StrFloatIntNDArray | None]]
    ) -> Iterator[dict[str, StrFloatIntNDArray | None]]:
        """
        Arguments:

            data: A dictionary storing data belonging to a data event.

        Returns:

            data: The same data provided to the function as an input
        """
        data_storage: DataStorage = DataStorage()

        data: dict[str, StrFloatIntNDArray | None]
        for data in stream:
            data_storage.add_data(data=data)

            if len(data_storage) >= self._batch_size:
                yield data_storage.retrieve_stored_data()
                data_storage.reset_data_storage()

        if len(data_storage) > 0:
            yield data_storage.retrieve_stored_data()
