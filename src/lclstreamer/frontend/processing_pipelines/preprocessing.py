"""
Preprocessing utilities for image data.

This module contains utilities for preprocessing image data, including padding
and channel dimension manipulation. The implementations are adapted from peaknet
but use numpy arrays instead of PyTorch tensors to match the lclstreamer data format.
"""

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from ...protocols.backend import StrFloatIntNDArray


class NumpyPad:
    """
    Pads numpy arrays to a specified target size.

    This class handles padding of 2D numpy arrays (H, W) to target dimensions.
    It supports different padding styles and uses zero-padding.

    Args:
        target_height: Target height after padding
        target_width: Target width after padding
        pad_style: Padding style - "center" or "bottom-right"
    """

    def __init__(
        self,
        target_height: int,
        target_width: int,
        pad_style: Literal["center", "bottom-right"] = "center"
    ):
        self.target_height = target_height
        self.target_width = target_width
        self.pad_style = pad_style

    def calc_pad_width(self, img: NDArray) -> tuple[tuple[int, int], tuple[int, int]]:
        """
        Calculate padding widths for the given image.

        Args:
            img: Input image array with shape (H, W)

        Returns:
            Padding widths in format ((top, bottom), (left, right))
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
            raise ValueError(f"Invalid pad_style '{self.pad_style}'. Use 'center' or 'bottom-right'.")

        return pad_width

    def __call__(self, img: NDArray) -> NDArray:
        """
        Apply padding to the input image.

        Args:
            img: Input image array with shape (H, W)

        Returns:
            Padded image array with shape (target_height, target_width)
        """
        pad_width = self.calc_pad_width(img)
        img_padded = np.pad(img, pad_width, mode='constant', constant_values=0)

        return img_padded


def add_channel_dimension(
    batch_array: StrFloatIntNDArray,
    num_channels: int = 1
) -> StrFloatIntNDArray:
    """
    Add channel dimension to batched array.

    Converts (B, H, W) format to (B, C, H, W) format by adding a channel dimension.

    Args:
        batch_array: Input batched array with shape (B, H, W)
        num_channels: Number of channels to add (default: 1)

    Returns:
        Array with added channel dimension (B, C, H, W)

    Raises:
        ValueError: If input array doesn't have expected 3D shape
    """
    if len(batch_array.shape) != 3:
        raise ValueError(
            f"Expected 3D input array (B, H, W), got shape {batch_array.shape}"
        )

    # Add channel dimension at position 1: (B, H, W) -> (B, 1, H, W)
    result = np.expand_dims(batch_array, axis=1)

    # If num_channels > 1, repeat along channel dimension
    if num_channels > 1:
        result = np.repeat(result, num_channels, axis=1)

    return result
