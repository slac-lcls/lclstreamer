import sys
from collections.abc import AsyncIterator, AsyncIterable
from io import BytesIO
from typing import Any

import h5py  # type: ignore
import hdf5plugin  # type: ignore

from aiostream import streamcontext

from ...models.parameters import DataSerializerParameters, HDF5BinarySerializerParameters
from ...models.types import Event
from ...protocols.backend import StrFloatIntNDArray
from ...protocols.frontend import DataSerializerProtocol
from ...utils.logging_utils import log


class HDF5BinarySerializer(DataSerializerProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(self, data_serializer_parameters: DataSerializerParameters) -> None:
        """
        Initializes an HDF5 data serializer

        This serializers turns a dictionary of numpy arrays into a binary blob with the
        internal structure of an HDF5 file, according to the preferences specified by
        the configuration parameters.

        Arguments:

            parameters: The configuration parameters
        """
        assert isinstance(data_serializer_parameters, HDF5BinarySerializerParameters)
        if data_serializer_parameters.compression == "gzip":
            self._compression_options: dict[str, Any] = {
                "compression": "gzip",
                "compression_opts": data_serializer_parameters.compression_level,
                "shuffle": False,
            }
        elif data_serializer_parameters.compression == "gzip_with_shuffle":
            self._compression_options = {
                "compression": "gzip",
                "compression_opts": data_serializer_parameters.compression_level,
                "shuffle": True,
            }
        elif data_serializer_parameters.compression == "bitshuffle_with_lz4":
            self._compression_options = {
                "compression": hdf5plugin.Bitshuffle(
                    cname="lz4",
                    clevel=data_serializer_parameters.compression_level,
                )
            }
        elif data_serializer_parameters.compression == "bitshuffle_with_zstd":
            self._compression_options = {
                "compression": hdf5plugin.Bitshuffle(
                    cname="zstd",
                    clevel=data_serializer_parameters.compression_level,
                )
            }
        elif data_serializer_parameters.compression == "zfp":
            self._compression_options = {"compression": hdf5plugin.Zfp()}
        else:
            self._compression_options = {}

        self._hdf5_fields: dict[str, str] = data_serializer_parameters.fields

    async def __call__(
        self, source: AsyncIterable[Event]
    ) -> AsyncIterator[bytes]:
        """
        Serializes data to a binary blob with an internal HDF5 structure

        Arguments:

            source: An async iterable (stream) of event data.

        Yields:

            byte_block: A binary blob (a bytes object)
        """
        async with streamcontext(source) as streamer:
          data: Event
          async for data in streamer:
            depth_of_data_blocks: list[int] = [
                value.shape[0]
                for data_block in data
                if (value := data[data_block]) is not None
            ]

            if len(set(depth_of_data_blocks)) != 1:
                log.error(
                    "The data blocks that should be written to the HDF5 file have"
                    "different depths"
                )
                sys.exit(1)

            mismatching_entries: set[str] = data.keys() - self._hdf5_fields.keys()

            if len(mismatching_entries) != 0:
                log.error(
                    "The Hdf5BinarySerializer is asked to serialize the following data "
                    "entries but data for these entries is not available: "
                    f"{' '.join(list(mismatching_entries))}"
                )
                sys.exit(1)

            with BytesIO() as byte_block:
                with h5py.File(byte_block, "w") as fh:
                    data_block_name: str
                    for data_block_name in data:
                        if (
                            data_block_name in self._hdf5_fields
                            and (data_block := data[data_block_name]) is not None
                        ):
                            fh.create_dataset(
                                name=self._hdf5_fields[data_block_name],
                                shape=data_block.shape,
                                dtype=data_block.dtype,
                                chunks=(1,) + data_block[0].shape,
                                data=data_block,
                                **self._compression_options,
                            )

                yield byte_block.getvalue()
