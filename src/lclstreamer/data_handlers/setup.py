from ..models.parameters import Parameters
from ..utils.logging import log_error_and_exit
from ..utils.protocols import DataHandlerProtocol
from .files.binary import (
    BinaryFileWritingDataHandler as BinaryFileWritingDataHandler,
)
from .streaming.binary import (
    BinaryDataStreamingDataHandler as BinaryDataStreamingDataHandler,
)

# Note: It would be simpler to write these as functions
# with the @contextlib.asynccontextmanager decorator.
# I *think* they would still type-check OK.


def initialize_data_handlers(
    parameters: Parameters,
) -> list[DataHandlerProtocol]:
    """
    Initializes the data handlers specified by the configuration parameters

    Arguments:
    parameters: The configuration parameters

    Returns:
        data_handlers: A list of initialized data handlers
    """
    data_handlers: list[DataHandlerProtocol] = []

    # data_handler_name: str
    for data_handler_name in parameters.data_handlers:
        try:
            data_handler: DataHandlerProtocol = globals()[data_handler_name.type](
                data_handler_name
            )
            data_handlers.append(data_handler)
        except NameError:
            log_error_and_exit(f"Data handler {data_handler_name} is not available")
    return data_handlers
