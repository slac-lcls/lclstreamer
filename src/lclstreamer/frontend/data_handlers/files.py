import sys
from pathlib import Path

from mpi4py import MPI

from ...models.parameters import (
    BinaryFileWritingDataHandlerParameters,
    DataHandlerParameters,
)
from ...protocols.frontend import DataHandlerProtocol
from ...utils.logging_utils import log


class BinaryFileWritingDataHandler(DataHandlerProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(self, parameters: DataHandlerParameters):
        """
        Initializes a binary file writing data handler

        This data handler writes byte objects to the filesystem as a files.

        Arguments:

              parameters: The configuration parameters
        """
        if parameters.BinaryFileWritingDataHandler is None:
            log.error(
                "No configuration parameters found for BinaryFileWritingDataHandler"
            )
            sys.exit(1)

        data_handler_parameters: BinaryFileWritingDataHandlerParameters = (
            parameters.BinaryFileWritingDataHandler
        )

        self._rank: int = MPI.COMM_WORLD.Get_rank()
        self._prefix: str = data_handler_parameters.file_prefix
        if self._prefix != "" and not self._prefix.endswith("_"):
            self._prefix = f"{self._prefix}_"
        else:
            self._prefix = data_handler_parameters.file_prefix
        self._suffix: str = data_handler_parameters.file_suffix
        self._write_directory: Path = data_handler_parameters.write_directory
        self._file_counter: int = 0

        self._write_directory.mkdir(exist_ok=True, parents=True)

    async def __call__(self, data: bytes) -> None:
        """
        Writes a bytes object to the filesystem as a single file.

        Arguments:

            data: A bytes object
        """
        filename: Path = (
            self._write_directory
            / f"{self._prefix}r{self._rank}_{self._file_counter}.{self._suffix}"
        )

        with open(filename, "wb") as fh:
            fh.write(data)

        self._file_counter += 1
