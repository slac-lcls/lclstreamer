from collections.abc import Iterator
from typing import Any, Literal, cast

import numpy
from numpy.typing import NDArray

from ...models.parameters import (
    PeaknetPreprocessingPipelineParameters,
)
from ...utils.logging import log_error_and_exit
from ...utils.protocols import ProcessingPipelineProtocol
from ...utils.typing import StrFloatIntNDArray
from ..common.data_storage import DataStorage


class _NumpyPad:
    """
    See documentation of the `__init__` function
    """

    def __init__(
        self,
        target_height: int,
        target_width: int,
        pad_style: Literal["center", "bottom-right"] = "center",
    ):
        """
        Initializes a numpy array padder to a specified target size

        This class handles padding of 2D numpy arrays (H, W) to target dimensions
        It supports different padding styles and uses zero-padding

        Arguments:

            target_height: Target height after padding

            target_width: Target width after padding

            pad_style: Padding style - either "center" or "bottom-right"
        """
        self.target_height = target_height
        self.target_width = target_width
        self.pad_style = pad_style

    def calc_pad_width(
        self, img: NDArray[numpy.floating[Any]]
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        """
        Calculates padding widths for the given image

        Arguments:

            img: Input image array with shape (H, W)

        Returns:

            pad_width: Padding widths in format ((top, bottom), (left, right))
        """
        H_img, W_img = img.shape

        dH_padded = max(self.target_height - H_img, 0)
        dW_padded = max(self.target_width - W_img, 0)

        if self.pad_style == "center":
            pad_width = (
                (dH_padded // 2, dH_padded - dH_padded // 2),  # (top, bottom)
                (dW_padded // 2, dW_padded - dW_padded // 2),  # (left, right)
            )
        elif self.pad_style == "bottom-right":
            pad_width = (
                (0, dH_padded),  # (top, bottom)
                (0, dW_padded),  # (left, right)
            )
        else:
            raise ValueError(
                f"Invalid pad_style '{self.pad_style}'. Use 'center' or 'bottom-right'."
            )

        return pad_width

    def __call__(
        self,
        img: NDArray[numpy.floating[Any]],
    ) -> NDArray[numpy.floating[Any]]:
        """
        Applies padding to the input image

        Arguments:

            img: Input image array with shape (H, W)

        Returns:

            img_padded: Padded image array with shape (target_height, target_width)
        """
        pad_width = self.calc_pad_width(img)
        img_padded: NDArray[numpy.floating[Any]] = numpy.pad(
            img, pad_width, mode="constant", constant_values=0
        )

        return img_padded


def _add_channel_dimension(
    array: StrFloatIntNDArray, num_channels: int = 1
) -> StrFloatIntNDArray:
    """
    Adds a channel dimension to a batched array

    Converts (B, H, W) format to (B, C, H, W) format by inserting a channel
    dimension at axis 1. If `num_channels` is greater than 1, the new axis is
    tiled by repeating the data along that dimension

    Arguments:

        array: Input array with shape (B, H, W)

        num_channels: Number of channels to produce (default: 1)

    Returns:

        result: Array with an added channel dimension of shape (B, C, H, W)

    Raises:

        ValueError: If the input array does not have exactly 3 dimensions
    """
    if len(array.shape) != 3:
        raise ValueError(f"Expected 3D input array (B, H, W), got shape {array.shape}")

    # Add channel dimension at position 1: (B, H, W) -> (B, 1, H, W)
    result: StrFloatIntNDArray = numpy.expand_dims(array, axis=1)

    # If num_channels > 1, repeat along channel dimension
    if num_channels > 1:
        result = numpy.repeat(result, num_channels, axis=1)

    return result


def _is_image_data(data_key: str, data_value: StrFloatIntNDArray | None) -> bool:
    # Determines if a data entry represents image data that should be preprocessed
    # Heuristic: 2D arrays are likely images
    # You may want to refine this logic based on your specific data keys
    return isinstance(data_value, numpy.ndarray) and len(data_value.shape) == 2


class PeaknetPreprocessingPipeline(ProcessingPipelineProtocol):
    """
    See documentation of the `__init__` function
    """

    def __init__(self, parameters: PeaknetPreprocessingPipelineParameters) -> None:
        """
        Initializes a PeakNet Preprocessing Pipeline

        This pipeline applies image preprocessing and batching in the following
        order:

        1. Pad individual images to the configured target size (before batching)
        2. Accumulate padded images into batches of `batch_size`
        3. Add a channel dimension to the batched image data (after batching)

        Non-image data (timestamps, scalars, etc.) is passed through unchanged
        at every stage

        Arguments:

            parameters: The processing pipeline configuration parameters
        """

        if parameters.type != "PeaknetPreprocessingPipeline":
            log_error_and_exit(
                "Processing pipeline parameters do not match the expected type"
            )

        self._batch_size: int = parameters.batch_size

        # Initialize padding utility
        self._padder: _NumpyPad = _NumpyPad(
            target_height=parameters.target_height,
            target_width=parameters.target_width,
            pad_style=parameters.pad_style,
        )

        # Channel dimension settings
        self._add_channel_dim: bool = parameters.add_channel_dim
        self._num_channels: int = parameters.num_channels

    def __call__(
        self, stream: Iterator[dict[str, StrFloatIntNDArray | None]]
    ) -> Iterator[dict[str, StrFloatIntNDArray | None]]:
        """
        Applies the PeakNet Preprocessing Pipeline to incoming event data

        For each event, the steps of the processing pipeline are applied to the
        incoming data. Any remaining events that do not fill a complete batch at
        the end of the data stream are yielded as a partial batch.

        Arguments:

            stream: A dictionary storing event data

        Yields:

            batch: A dictionary of processed and batched events
        """
        data_storage: DataStorage = DataStorage()

        data: dict[str, StrFloatIntNDArray | None]
        for data in stream:
            # Apply preprocessing to image data before adding to batch
            preprocessed_data: dict[str, StrFloatIntNDArray | None] = {}

            data_key: str
            data_value: StrFloatIntNDArray | None
            for data_key, data_value in data.items():
                if data_value is not None and _is_image_data(data_key, data_value):
                    # Apply padding to image data
                    preprocessed_data[data_key] = self._padder(
                        cast(NDArray[numpy.floating[Any]], data_value)
                    )
                else:
                    # Pass through non-image data unchanged
                    preprocessed_data[data_key] = data_value

            data_storage.add_data(data=preprocessed_data)

            if len(data_storage) >= self._batch_size:
                batched_data: dict[str, StrFloatIntNDArray | None] = (
                    data_storage.retrieve_stored_data()
                )

                # Add channel dimension to image data after batching
                if self._add_channel_dim:
                    final_data: dict[str, StrFloatIntNDArray | None] = {}

                    for data_key, data_value in batched_data.items():
                        if data_value is not None and len(data_value.shape) == 3:
                            # This is batched image data (B, H, W) -> add channel (B, C, H, W)
                            final_data[data_key] = _add_channel_dimension(
                                data_value, self._num_channels
                            )
                        else:
                            # Pass through non-image data
                            final_data[data_key] = data_value
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
                for data_key, data_value in batched_data.items():
                    if data_value is not None and len(data_value.shape) == 3:
                        final_data[data_key] = _add_channel_dimension(
                            data_value, self._num_channels
                        )
                    else:
                        final_data[data_key] = data_value
                yield final_data
            else:
                yield batched_data
