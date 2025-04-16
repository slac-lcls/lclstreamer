from ..models.parameters import LclstreamerParameters, Parameters
from ..protocols.frontend import DataSerializerProtocol
from .data_serializers.file_formats import Hdf5Serializer  # noqa: F401


def initialize_data_serializer(
    parameters: Parameters,
) -> DataSerializerProtocol:
    """
    Initializes the data serializer specified by the configuration parameters

    Arguments:

        parameters: The configuration parameters

    Returns:

        data_serializer: An initialized data serializer
    """
    lclstreamer_parameters: LclstreamerParameters = parameters.lclstreamer

    try:
        data_serializer: DataSerializerProtocol = globals()[
            lclstreamer_parameters.data_serializer
        ](parameters)s




    except NameError:
        raise RuntimeError(
            f"Data serializer {lclstreamer_parameters.data_serializer} is "
            "not available"
        )
    return data_serializer
