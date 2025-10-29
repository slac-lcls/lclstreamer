import sys

from ..models.parameters import (
    DataSerializerParameters,
    LclstreamerParameters,
    Parameters,
)
from ..protocols.frontend import DataSerializerProtocol
from ..utils.logging_utils import log
from .data_serializers.file_formats import Hdf5BinarySerializer  # noqa: F401
from .data_serializers.json import SimplonBinarySerializer  # noqa: F401


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
    data_serializer_parameters: DataSerializerParameters = parameters.data_serializer

    try:
        data_serializer: DataSerializerProtocol = globals()[
            lclstreamer_parameters.data_serializer
        ](data_serializer_parameters)
    except NameError:
        log.error(
            f"Data serializer {lclstreamer_parameters.data_serializer} is "
            "not available"
        )
        sys.exit(1)
    return data_serializer
