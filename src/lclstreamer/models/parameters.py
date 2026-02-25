from pathlib import Path
from typing import Dict, List, Literal, Self, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Annotated


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",  # Allows extra attributes during validation
    )


####### Event Sources ########


class InternalEventSourceParameters(CustomBaseModel):
    type: Literal["InternalEventSource"]
    number_of_events_to_generate: int
    model_config = ConfigDict(extra="allow")


class Psana1EventSourceParameters(CustomBaseModel):
    type: Literal["Psana1EventSource"]


class Psana2EventSourceParameters(CustomBaseModel):
    type: Literal["Psana2EventSource"]


EventSourceParameters = Annotated[
    Union[
        InternalEventSourceParameters,
        Psana1EventSourceParameters,
        Psana2EventSourceParameters,
    ],
    Field(discriminator="type"),
]


###### Data Sources #######


class DataSourceParameters(CustomBaseModel):
    type: str
    model_config = ConfigDict(extra="allow")


####### Processing Pipelines #########


class BatchProcessingPipelineParameters(CustomBaseModel):
    type: Literal["BatchProcessingPipeline"]
    batch_size: int


class PeaknetPreprocessingPipelineParameters(CustomBaseModel):
    type: Literal["PeaknetPreprocessingPipeline"]
    batch_size: int
    target_height: int
    target_width: int
    pad_style: Literal["center", "bottom-right"] = "center"
    add_channel_dim: bool = True
    num_channels: int = 1


ProcessingPipelineParameters = Annotated[
    Union[BatchProcessingPipelineParameters, PeaknetPreprocessingPipelineParameters],
    Field(discriminator="type"),
]


####### Serializers ##########


class SimplonBinarySerializerParameters(CustomBaseModel):
    type: Literal["SimplonBinarySerializer"]
    data_source_to_serialize: str
    polarization_fraction: float
    polarization_axis: List[float]
    data_collection_rate: str
    detector_name: str
    detector_type: str


class HDF5BinarySerializerParameters(CustomBaseModel):
    type: Literal["HDF5BinarySerializer"]
    compression_level: int = 3
    compression: (
        Literal[
            "gzip",
            "gzip_with_shuffle",
            "bitshuffle_with_lz4",
            "bitshuffle_with_zstd",
            "zfp",
        ]
        | None
    ) = None
    fields: Dict[str, str]


DataSerializerParameters = Annotated[
    Union[HDF5BinarySerializerParameters, SimplonBinarySerializerParameters],
    Field(discriminator="type"),
]


######### Data Handlers #################


class BinaryDataStreamingDataHandlerParameters(CustomBaseModel):
    type: Literal["BinaryDataStreamingDataHandler"]
    urls: List[str]
    role: Literal["server", "client"] = "server"
    library: Literal["zmq", "nng"] = "nng"
    socket_type: Literal["push"] = "push"


class BinaryFileWritingDataHandlerParameters(CustomBaseModel):
    type: Literal["BinaryFileWritingDataHandler"]
    file_prefix: str = ""
    file_suffix: str = "h5"
    write_directory: Path = Path.cwd()


DataHandlerParameters = Annotated[
    Union[
        BinaryDataStreamingDataHandlerParameters, BinaryFileWritingDataHandlerParameters
    ],
    Field(discriminator="type"),
]


class Parameters(CustomBaseModel):
    source_identifier: str
    skip_incomplete_events: bool

    event_source: EventSourceParameters
    data_sources: Dict[str, DataSourceParameters]
    processing_pipeline: ProcessingPipelineParameters
    data_serializer: DataSerializerParameters
    data_handlers: List[DataHandlerParameters]

    @model_validator(mode="after")
    def check_model(self) -> Self:
        if self.data_serializer.type == "SimplonBinarySerializer":
            required_sources = [
                "timestamp",
                "detector_data",
                # "photon_wavelength",
                "detector_geometry",
                "run_info",
            ]
            source_missing = [
                k for k in required_sources if k not in self.data_sources.keys()
            ]
            if source_missing:
                raise ValueError(
                    f"Required fields: {source_missing} is missing from data_sources "
                    " for SimplonBinarySerializer."
                )

        return self
