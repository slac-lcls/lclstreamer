import sys
from io import BytesIO
from typing import Any

import h5py  # type: ignore
import hdf5plugin  # type: ignore

from ...models.parameters import HDF5SerializerParameters, Parameters
from ...protocols.backend import StrFloatIntNDArray
from ...protocols.frontend import DataSerializerProtocol
from ...utils.logging_utils import log


class Hdf5Serializer(DataSerializerProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(self, parameters: Parameters):
        """
        Initializes an HDF5 data serializer

        This serializers turns a dictionary of numpy arrays into a binary blob with the
        internal structure of an HDF5 file, according to the preferences specified by
        the configuration parameters.

        Arguments:

            parameters: The configuration parameters
        """
        if parameters.data_serializer.Hdf5Serializer is None:
            log.error("No configuration parameters found for Hdf5Serializer")
            sys.exit(1)

        data_serializer_parameters: HDF5SerializerParameters = (
            parameters.data_serializer.Hdf5Serializer
        )

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

    def serialize_data(self, data: dict[str, StrFloatIntNDArray]) -> bytes:
        """
        Serializes data to a binary blob with an internal HDF5 structure

        Arguments:

            data: A dictionary storing numpy arrays

        Returns

            byte_block: A binary blob (a bytes object)
        """

        depth_of_data_blocks: list[int] = [
            data[data_block].shape[0] for data_block in data
        ]

        if len(set(depth_of_data_blocks)) != 1:
            log.error(
                "The data blocks that should be written to the HDF5 file have"
                "different depths"
            )
            sys.exit(1)

        with BytesIO() as byte_block:
            with h5py.File(byte_block, "w") as fh:

                data_block_name: str
                for data_block_name in data:

                    if data_block_name in self._hdf5_fields:

                        fh.create_dataset(
                            name=self._hdf5_fields[data_block_name],
                            shape=data[data_block_name].shape,
                            dtype=data[data_block_name].dtype,
                            chunks=(1,) + data[data_block_name][0].shape,
                            data=data[data_block_name],
                            **self._compression_options,
                        )

            return byte_block.getvalue()
