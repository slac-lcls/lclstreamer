import sys
from collections.abc import Iterator

from ...models.parameters import ProcessingPipelineParameters
from ...protocols.backend import StrFloatIntNDArray
from ...protocols.frontend import ProcessingPipelineProtocol
from ...utils.logging_utils import log
from .preprocessing import NumpyPad, add_channel_dimension
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


class PreprocessingBatchPipeline(ProcessingPipelineProtocol):
    """
    A processing pipeline that applies preprocessing (padding, channel dimension) and batching.

    This pipeline performs the following operations in order:
    1. Pad individual images to target size (before batching)
    2. Batch the padded images
    3. Add channel dimension to batched data (after batching)

    The preprocessing is applied to detector image data while other data types
    (timestamps, scalars, etc.) are passed through unchanged.
    """

    def __init__(self, parameters: ProcessingPipelineParameters) -> None:
        """
        Initializes a preprocessing batch pipeline.

        Arguments:
            parameters: The configuration parameters
        """
        if parameters.PreprocessingBatchPipeline is None:
            log.error("No configuration parameters found for PreprocessingBatchPipeline")
            sys.exit(1)

        config = parameters.PreprocessingBatchPipeline
        self._batch_size: int = config.batch_size

        # Initialize padding utility
        self._padder = NumpyPad(
            target_height=config.target_height,
            target_width=config.target_width,
            pad_style=config.pad_style
        )

        # Channel dimension settings
        self._add_channel_dim: bool = config.add_channel_dim
        self._num_channels: int = config.num_channels

    def _is_image_data(self, data_key: str, data_value: StrFloatIntNDArray | None) -> bool:
        """
        Determine if a data entry represents image data that should be preprocessed.

        Args:
            data_key: The key/name of the data entry
            data_value: The data array

        Returns:
            True if this looks like image data that should be preprocessed
        """
        if data_value is None:
            return False

        # Heuristic: 2D arrays are likely images
        # You may want to refine this logic based on your specific data keys
        return len(data_value.shape) == 2

    def __call__(
        self, stream: Iterator[dict[str, StrFloatIntNDArray | None]]
    ) -> Iterator[dict[str, StrFloatIntNDArray | None]]:
        """
        Process the data stream with preprocessing and batching.

        Arguments:
            stream: Iterator of data events

        Returns:
            Iterator of preprocessed and batched data events
        """
        data_storage: DataStorage = DataStorage()

        data: dict[str, StrFloatIntNDArray | None]
        for data in stream:
            # Apply preprocessing to image data before adding to batch
            preprocessed_data = {}

            for data_key, data_value in data.items():
                if self._is_image_data(data_key, data_value):
                    # Apply padding to image data
                    preprocessed_data[data_key] = self._padder(data_value)
                else:
                    # Pass through non-image data unchanged
                    preprocessed_data[data_key] = data_value

            data_storage.add_data(data=preprocessed_data)

            if len(data_storage) >= self._batch_size:
                batched_data = data_storage.retrieve_stored_data()

                # Add channel dimension to image data after batching
                if self._add_channel_dim:
                    final_data = {}
                    for data_key, batch_value in batched_data.items():
                        if batch_value is not None and len(batch_value.shape) == 3:
                            # This is batched image data (B, H, W) -> add channel (B, C, H, W)
                            final_data[data_key] = add_channel_dimension(
                                batch_value, self._num_channels
                            )
                        else:
                            # Pass through non-image data
                            final_data[data_key] = batch_value
                    yield final_data
                else:
                    yield batched_data

                data_storage.reset_data_storage()

        # Handle remaining data
        if len(data_storage) > 0:
            batched_data = data_storage.retrieve_stored_data()

            # Add channel dimension to remaining data if configured
            if self._add_channel_dim:
                final_data = {}
                for data_key, batch_value in batched_data.items():
                    if batch_value is not None and len(batch_value.shape) == 3:
                        final_data[data_key] = add_channel_dimension(
                            batch_value, self._num_channels
                        )
                    else:
                        final_data[data_key] = batch_value
                yield final_data
            else:
                yield batched_data
