import sys
from collections.abc import Iterator
from time import time
from typing import Any

import numpy
from bitshuffle import compress_lz4  # type: ignore
from cbor import dumps  # type: ignore
from mpi4py import MPI
from numpy.typing import NDArray

from ...models.parameters import DataSerializerParameters
from ...protocols.backend import StrFloatIntNDArray
from ...protocols.frontend import DataSerializerProtocol
from ...utils.logging_utils import log


class SimplonBinarySerializer(DataSerializerProtocol):
    def __init__(self, parameters: DataSerializerParameters):
        """
        Initializes an HDF5 data serializer

        This serializers turns a dictionary of numpy arrays into a binary with an
        internal structure of a Simplon message. This serializer follows the 1.8
        version of the Simplon specification (published by Dectris)

        Arguments:

            parameters: The configuration parameters
        """
        if parameters.SimplonBinarySerializer is None:
            log.error(
                "No configuration parameters found for "
                "SimplonPythonDictionarySerializer"
            )
            sys.exit(1)
        self._data_source_to_serialize: str = (
            parameters.SimplonBinarySerializer.data_source_to_serialize
        )
        self._node_rank: int = MPI.COMM_WORLD.Get_rank()
        self._node_pool_size: int = MPI.COMM_WORLD.Get_size()
        self._rank_message_count: int = 1

    def __call__(
        self, stream: Iterator[dict[str, StrFloatIntNDArray | None]]
    ) -> Iterator[bytes]:
        """
        Serializes data to a binary blob with an internal Simplon message structure

        Arguments:

            data: A dictionary storing numpy arrays

        Returns

            byte_block: A binary blob (a bytes object)
        """

        if self._node_rank == self._node_pool_size - 1:
            yield b"".join(
                (
                    b"c",
                    dumps(
                        {
                            "type": "start",
                            "timestamp": time(),
                        }
                    ),
                )
            )
        data: dict[str, StrFloatIntNDArray | None]
        for data in stream:
            try:
                if (data_block := data[self._data_source_to_serialize]) is not None:
                    array: StrFloatIntNDArray = data_block[-1]
                else:
                    continue
            except KeyError:
                log.error(
                    f"The {self._data_source_to_serialize} data source, that the "
                    "SimplonBinarySerializer is supposed to serialize, cannot be found in"
                    "the data"
                )
                sys.exit(1)

            if not (
                numpy.issubdtype(array.dtype, numpy.int_)
                or numpy.issubdtype(array.dtype, numpy.float_)
            ):
                log.error(
                    f"The {self._data_source_to_serialize} data source is not of type int "
                    "or float, as required by the SimplonBinarySerializer"
                )
                sys.exit(1)

            array_sum: float | int = array.sum()

            compressed_data: NDArray[numpy.int_] = compress_lz4(array, block_size=2**12)

            message: dict[str, Any] = {
                "type": "image",
                "compressed_data": compressed_data.tobytes(),
                "shape": array.shape,
                "dtype": str(array.dtype),
                "sum": array_sum,
                "message_id": self._node_rank * 10000 + self._rank_message_count,
                "timestamp": time(),  # Will be set at send time
            }

            yield b"".join((b"m", dumps(message)))

        if self._node_rank == self._node_pool_size - 1:
            yield b"".join(
                (
                    b"m",
                    dumps(
                        {
                            "type": "stop",
                            "timestamp": time(),
                        }
                    ),
                ),
            )
