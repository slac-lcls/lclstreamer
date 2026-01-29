import sys
from collections.abc import AsyncIterator, AsyncIterable
from io import BytesIO
from typing import Any

from aiostream import streamcontext

from ...models.parameters import DataSerializerParameters, TensorSerializerParameters
from ...models.types import Event
from ...protocols.frontend import DataSerializerProtocol
from ...utils.logging_utils import log

#import torch
import numpy


class TensorSerializer(DataSerializerProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(self, data_serializer_parameters: DataSerializerParameters) -> None:
        """
        Initializes a Torch Tensor data serializer

        This serializers turns a dictionary of numpy arrays into a tensor blob.

        Arguments:

            parameters: The configuration parameters
        """
        pass

    async def __call__(
        self, source: AsyncIterable[Event]
    ) -> AsyncIterator[bytes]:
        """
        Serializes data to a tensor blob to be used with torch.

        Arguments:

            source: An async iterable (stream) of event data.

        Yields:

            byte_block: A binary blob (a bytes object)
        """
        async with streamcontext(source) as streamer:
          datas: Event
          async for datas in streamer:
            #tensors: dict[Any, Any] = {
            #    k: v for k, v in data.items() if v is not None
            #}

            #if not tensors:
            #    log.error("Received empty event, nothing to serialize")
            #    continue

            #batch_sizes: set[int] = {
            #    v.shape[0] for v in tensors.values()
            #    if hasattr(v, "shape") and len(v.shape) > 0
            #}

            #if len(batch_sizes) > 1:
            #    log.error(
            #        "The data blocks to be serialized have different batch sizes"
            #    )
            #    sys.exit(1)

            #buffer: BytesIO = BytesIO()
            #torch.save(tensors, buffer)

            #yield buffer.getvalue()
            for data_block in datas:
                data2: numpy.ndarray = datas[data_block]
                data = data2[0]

                if data is None:
                    continue

                if isinstance(data, numpy.ndarray) and data.dtype == object:
                    blob = data[0]
                    print("Type of sent data:", type(blob))
                    print("Length of sent data:", len(blob))
                    yield blob
                elif isinstance(data, bytes):
                    print("Type of data:", type(data))
                    print("Length of data:", len(data))
                    yield data
                else:
                    raise TypeError(f"Cannot serialize type {type(data)}.")
