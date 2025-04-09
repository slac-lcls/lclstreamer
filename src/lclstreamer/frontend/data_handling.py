from ..models.parameters import LclstreamerParameters, Parameters
from ..protocols.frontend import DataHandlerProtocol
from .file_data_handlers import BinaryFileWritingDataHandler  # noqa: F401
from .streaming_data_handlers import BinaryDataStreamingDataHandler  # noqa: F401


def initialize_data_handlers(
    parameters: Parameters,
) -> list[DataHandlerProtocol]:
    """ """
    lclstreamer_parameters: LclstreamerParameters = parameters.lclstreamer

    data_handlers: list[DataHandlerProtocol] = []

    data_handler_name: str
    for data_handler_name in lclstreamer_parameters.data_handlers:
        try:
            data_handler: DataHandlerProtocol = globals()[data_handler_name](parameters)
            data_handlers.append(data_handler)
        except NameError:
            raise RuntimeError(
                f"Data serializer {lclstreamer_parameters.data_handlers} "
                "is not available"
            )
    return data_handlers
