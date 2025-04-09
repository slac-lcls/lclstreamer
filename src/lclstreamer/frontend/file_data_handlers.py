from pathlib import Path
from socket import gethostname

from ..models.parameters import BinaryFileWritingDataHandlerParameters, Parameters
from ..protocols.frontend import DataHandlerProtocol


class BinaryFileWritingDataHandler(DataHandlerProtocol):

    def __init__(self, parameters: Parameters):

        if parameters.data_handlers.BinaryFileWritingDataHandler is None:
            raise RuntimeError(
                "No configuration parameters found for BinaryFileWritingDataHandler"
            )

        data_handler_parameters: BinaryFileWritingDataHandlerParameters = (
            parameters.data_handlers.BinaryFileWritingDataHandler
        )

        self._hostname: str = gethostname()
        self._prefix: str = data_handler_parameters.file_prefix
        if self._prefix != "" and not self._prefix.endswith("_"):
            self._prefix = f"{self._prefix}_"
        else:
            self._prefix = data_handler_parameters.file_prefix
        self._suffix: str = data_handler_parameters.file_suffix
        self._write_directory: Path = data_handler_parameters.write_directory
        self._file_counter: int = 0

    def handle_data(self, data: bytes) -> None:

        filename: Path = (
            self._write_directory
            / f"{self._prefix}{self._hostname}_{self._file_counter}.{self._suffix}"
        )

        with open(filename, "wb") as fh:
            fh.write(data)

        self._file_counter += 1
