from ..models.parameters import LclstreamerParameters, Parameters
from ..protocols.frontend import DataSerializerProtocol
from .file_format_serializers import Hdf5Serializer  # noqa: F401


def initialize_data_serializer(
    parameters: Parameters,
) -> DataSerializerProtocol:
    """ """
    lclstreamer_parameters: LclstreamerParameters = parameters.lclstreamer

    try:
        data_serializer: DataSerializerProtocol = globals()[
            lclstreamer_parameters.data_serializer
        ](parameters)
    except NameError:
        raise RuntimeError(
            f"Data serializer {lclstreamer_parameters.data_serializer} is "
            "not available"
        )
    return data_serializer
