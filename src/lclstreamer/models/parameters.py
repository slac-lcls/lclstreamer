from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, model_validator


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",  # Allows extra attributes during validation
    )


class InternalEventSourceParameters(CustomBaseModel):
    number_of_events_to_generate: int


class Psana1EventSourceParameters(CustomBaseModel): ...  # noqa: E701


class Psana2EventSourceParameters(CustomBaseModel): ...  # noqa: E701


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


class PreprocessingBatchPipelineParameters(CustomBaseModel):
    batch_size: int
    target_height: int
    target_width: int
    pad_style: Literal["center", "bottom-right"] = "center"
    add_channel_dim: bool = True
    num_channels: int = 1


class BinaryDataStreamingDataHandlerParameters(CustomBaseModel):
    urls: list[str]
    role: Literal["server", "client"] = "server"
    library: Literal["zmq", "nng"] = "nng"
    socket_type: Literal["push"] = "push"


class BinaryFileWritingDataHandlerParameters(CustomBaseModel):
    file_prefix: str = ""
    file_suffix: str = "h5"
    write_directory: Path = Path.cwd()


class DataSourceParameters(CustomBaseModel):
    type: str

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
    PreprocessingBatchPipeline: PreprocessingBatchPipelineParameters | None = None


class DataSerializerParameters(CustomBaseModel):
    Hdf5BinarySerializer: HDF5BinarySerializerParameters | None = None


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

        return self
