from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, model_validator, Field, conlist


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",  # Allows extra attributes during validation
    )


class InternalEventSourceParameters(CustomBaseModel):
    number_of_events_to_generate: int


class Psana1EventSourceParameters(CustomBaseModel): ...  # noqa: E701


class Psana2EventSourceParameters(CustomBaseModel): ...  # noqa: E701


class SimplonBinarySerializerParameters(CustomBaseModel):
    data_source_to_serialize: str
    polarization_fraction: float
    polarization_axis: list[float]
    data_collection_rate: str
    detector_name: str
    detector_type: str


class HDF5BinarySerializerParameters(CustomBaseModel):
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
    fields: dict[str, str]


class BatchProcessingPipelineParameters(CustomBaseModel):
    batch_size: int


class BinaryDataStreamingDataHandlerParameters(CustomBaseModel):
    urls: list[str]
    role: Literal["server", "client"] = "server"
    library: Literal["zmq", "nng"] = "nng"
    socket_type: Literal["push"] = "push"


class BinaryFileWritingDataHandlerParameters(CustomBaseModel):
    file_prefix: str = ""
    file_suffix: str = "h5"
    write_directory: Path = Path.cwd()


class TimestampParameters(CustomBaseModel):
    type: str


class DetectorDataParameters(CustomBaseModel):
    type: str
    psana_name: str


class PhotonWavelengthParameters(CustomBaseModel):
    type: str
    psana_name: str


class DetectorGeometryParameters(CustomBaseModel):
    type: str
    psana_name: str
    psana_fields: list[str] = Field(
        default_factory = list, min_length=2, max_length=3
    )


class BeamPointingParameters(CustomBaseModel):
    type: str
    psana_name: str
    psana_fields: list[str] = Field(
        default_factory = list, min_length=4, max_length=4
    )


class RunInfoParameters(CustomBaseModel):
    type: str


class DataSourceParameters(CustomBaseModel):
    type: str
    timestamp: TimestampParameters | None = None
    detector_data: DetectorDataParameters | None = None
    photon_wavelength: PhotonWavelengthParameters | None = None
    detector_info: DetectorGeometryParameters | None = None
    beam_pointing: BeamPointingParameters | None = None
    run_info: RunInfoParameters | None = None

    model_config = ConfigDict(extra="allow")


class LclstreamerParameters(CustomBaseModel):
    source_identifier: str
    event_source: str
    processing_pipeline: str
    data_serializer: str
    data_handlers: list[str]
    skip_incomplete_events: bool


class EventSourceParameters(CustomBaseModel):
    InternalEventSource: InternalEventSourceParameters | None = None
    Psana1EventSource: Psana1EventSourceParameters | None = None
    Psana2EventSource: Psana2EventSourceParameters | None = None


class ProcessingPipelineParameters(CustomBaseModel):
    BatchProcessingPipeline: BatchProcessingPipelineParameters | None = None


class DataSerializerParameters(CustomBaseModel):
    Hdf5BinarySerializer: HDF5BinarySerializerParameters | None = None
    SimplonBinarySerializer: SimplonBinarySerializerParameters | None = None


class DataHandlerParameters(CustomBaseModel):
    BinaryDataStreamingDataHandler: BinaryDataStreamingDataHandlerParameters | None = (
        None
    )

    BinaryFileWritingDataHandler: BinaryFileWritingDataHandlerParameters | None = None


class Parameters(CustomBaseModel):
    lclstreamer: LclstreamerParameters
    event_source: EventSourceParameters
    data_sources: dict[str, DataSourceParameters]
    data_serializer: DataSerializerParameters
    data_handlers: DataHandlerParameters
    processing_pipeline: ProcessingPipelineParameters

    @model_validator(mode="after")
    def check_model(self) -> Self:
        if getattr(self.event_source, self.lclstreamer.event_source) is None:
            raise ValueError(
                f"No configuration found for {self.lclstreamer.event_source} event "
                "source"
            )
        if (
            getattr(self.processing_pipeline, self.lclstreamer.processing_pipeline)
            is None
        ):
            raise ValueError(
                f"No configuration found for {self.lclstreamer.processing_pipeline} "
                "processing pipeline"
            )

        if getattr(self.data_serializer, self.lclstreamer.data_serializer) is None:
            raise ValueError(
                f"No configuration found for {self.lclstreamer.data_serializer} data "
                "serializer"
            )

        data_handler_name: str
        for data_handler_name in self.lclstreamer.data_handlers:
            if getattr(self.data_handlers, data_handler_name) is None:
                raise ValueError(
                    f"No configuration found for {data_handler_name} data handler"
                )

        if self.lclstreamer.data_serializer == "SimplonBinarySerializer":
            required_sources = [
                "timestamp",
                "detector_data",
                "photon_wavelength",
                "detector_geometry",
                "run_info"
            ]
            source_missing = [k for k in required_sources if k not in self.data_sources.keys()]
            if source_missing:
                raise ValueError(
                    f"Required field: {source_missing} is missing from data_sources "
                    " for SimplonBinarySerializer."
                )

        return self
