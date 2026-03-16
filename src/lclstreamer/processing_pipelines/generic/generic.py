from collections.abc import Iterator

from ...models.parameters import (
    BatchProcessingPipelineParameters,
)
from ...utils.logging import log_error_and_exit
from ...utils.protocols import ProcessingPipelineProtocol
from ...utils.typing import StrFloatIntNDArray
from ..common.data_storage import DataStorage


class BatchProcessingPipeline(ProcessingPipelineProtocol):
    """
    See documentation of the `__init__` function
    """

    def __init__(self, parameters: BatchProcessingPipelineParameters) -> None:
        """
        Initializes a batching pipeline

        This pipeline accumulates data into batches

        Arguments:

            parameters: The processing pipeline configuration parameters
        """
        if parameters.type != "BatchProcessingPipeline":
            log_error_and_exit(
                "Processing pipeline parameters do not match the expected type"
            )

        self.batch_size: int = parameters.batch_size

    def __call__(
        self, stream: Iterator[dict[str, StrFloatIntNDArray | None]]
    ) -> Iterator[dict[str, StrFloatIntNDArray | None]]:
        """
        Applies the batching pipeline to incoming event data

        Accumulates individual events into batches. Once a full batch has been
        collected it is returned. Any remaining events that do not fill a
        complete batch at the end of the stream  are yielded as a partial batch

        Arguments:

            stream: A dictionary storing event data

        Yields:

            batch: A dictionary of processed and batched events
        """
        data_storage: DataStorage = DataStorage()

        data: dict[str, StrFloatIntNDArray | dict[str, StrFloatIntNDArray] | None]
        for data in stream:
            data_storage.add_data(data=data)

            if len(data_storage) >= self.batch_size:
                yield data_storage.retrieve_stored_data()
                data_storage.reset_data_storage()

        if len(data_storage) > 0:
            yield data_storage.retrieve_stored_data()
