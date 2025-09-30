import sys

from ..models.parameters import LclstreamerParameters, Parameters
from ..protocols.frontend import DataSerializerProtocol
from ..utils.logging_utils import log
from .data_serializers.file_formats import (  # noqa: F401
    Hdf5BinarySerializer,
    NumpyBinarySerializer,
)


def initialize_data_serializer(
    parameters: Parameters,
) -> DataSerializerProtocol:
    """
    Initializes the Data Serializer specified by the configuration parameters

    Arguments:

        parameters: The configuration parameters

    Returns:

        data_serializer: An initialized Data Serializer
    """
    lclstreamer_parameters: LclstreamerParameters = parameters.lclstreamer

    try:
        data_serializer: DataSerializerProtocol = globals()[
            lclstreamer_parameters.data_serializer
        ](parameters)
    except NameError:
        log.error(
            f"Data serializer {lclstreamer_parameters.data_serializer} is "
            "not available"
        )
        sys.exit(1)
    return data_serializer
