import sys

from ..models.parameters import DataHandlerParameters, LclstreamerParameters, Parameters
from ..protocols.frontend import DataHandlerProtocol
from ..utils.logging_utils import log
from .data_handlers.files import BinaryFileWritingDataHandler  # noqa: F401
from .data_handlers.streaming import BinaryDataStreamingDataHandler  # noqa: F401


def initialize_data_handlers(
    parameters: Parameters,
) -> list[DataHandlerProtocol]:
    """
    Initializes the Data Handlers specified by the configuration parameters

    Arguments:

        parameters: The configuration parameters

    Returns:

        data_handlers: A list of initialized Data Handlers
    """
    lclstreamer_parameters: LclstreamerParameters = parameters.lclstreamer
    data_handler_parameters: DataHandlerParameters = parameters.data_handlers

    data_handlers: list[DataHandlerProtocol] = []

    data_handler_name: str
    for data_handler_name in lclstreamer_parameters.data_handlers:
        try:
            data_handler: DataHandlerProtocol = globals()[data_handler_name](
                data_handler_parameters
            )
            data_handlers.append(data_handler)
        except NameError:
            log.error(f"Data serializer {data_handler_name} is not available")
            sys.exit(1)
    return data_handlers
