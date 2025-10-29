import sys

from ..models.parameters import (
    DataSerializerParameters,
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
    data_serializer_parameters: DataSerializerParameters = parameters.data_serializer

    data_serializer: DataSerializerProtocol = globals()[
        data_serializer_parameters.type
    ](data_serializer_parameters)

    return data_serializer
