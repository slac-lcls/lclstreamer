from collections.abc import Iterator
from io import BytesIO
from typing import Any

import h5py
import hdf5plugin  # pyright: ignore[reportMissingTypeStubs]

from ...models.parameters import (
    HDF5BinarySerializerParameters,
)
from ...utils.logging import log_error_and_exit
from ...utils.protocols import DataSerializerProtocol
from ...utils.typing import StrFloatIntNDArray


class HDF5BinarySerializer(DataSerializerProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(self, parameters: HDF5BinarySerializerParameters) -> None:
        """
        Initializes an HDF5 data serializer

        This serializers turns a dictionary of numpy arrays into a binary blob with the
        internal structure of an HDF5 file, according to the preferences specified by
        the configuration parameters.

        Arguments:

            parameters: The configuration parameters
        """
        if parameters.type != "HDF5BinarySerializer":
            log_error_and_exit(
                "Data serializer parameters do not match the expected type"
            )
        if parameters.compression == "gzip":
            self._compression_options: dict[str, Any] = {
                "compression": "gzip",
                "compression_opts": parameters.compression_level,
                "shuffle": False,
            }
        elif parameters.compression == "gzip_with_shuffle":
            self._compression_options = {
                "compression": "gzip",
                "compression_opts": parameters.compression_level,
                "shuffle": True,
            }
        elif parameters.compression == "bitshuffle_with_lz4":
            self._compression_options = {
                "compression": hdf5plugin.Bitshuffle(  # pyright: ignore[reportPrivateImportUsage]
                    cname="lz4",
                    clevel=parameters.compression_level,
                )
            }
        elif parameters.compression == "bitshuffle_with_zstd":
            self._compression_options = {
                "compression": hdf5plugin.Bitshuffle(  # pyright: ignore[reportPrivateImportUsage]
                    cname="zstd",
                    clevel=parameters.compression_level,
                )
            }
        elif parameters.compression == "zfp":
            self._compression_options = {
                "compression": hdf5plugin.Zfp()  # pyright: ignore[reportPrivateImportUsage]
            }
        else:
            self._compression_options = {}

        self._hdf5_fields: dict[str, str] = parameters.fields

    def __call__(
        self, stream: Iterator[dict[str, StrFloatIntNDArray | None]]
    ) -> Iterator[bytes]:
        """
        Serializes data to a binary blob with an internal HDF5 structure

        Arguments:

            data: A dictionary storing numpy arrays

        Returns

            byte_block: A binary blob (a bytes object)
        """
        data: dict[str, StrFloatIntNDArray | None]
        for data in stream:
            depth_of_data_blocks: list[int] = [
                value.shape[0]
                for data_block in data
                if (value := data[data_block]) is not None
            ]

            if len(set(depth_of_data_blocks)) != 1:
                log_error_and_exit(
                    "The data blocks that should be written to the HDF5 file have"
                    "different depths"
                )

            mismatching_entries: set[str] = data.keys() - self._hdf5_fields.keys()

            if len(mismatching_entries) != 0:
                log_error_and_exit(
                    "The Hdf5BinarySerializer is asked to serialize the following data "
                    "entries but data for these entries is not available: "
                    f"{' '.join(list(mismatching_entries))}"
                )

            with BytesIO() as byte_block:
                with h5py.File(
                    byte_block,  # pyright: ignore[reportArgumentType]  # ty: ignore[invalid-argument-type]
                    "w",
                ) as fh:
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
