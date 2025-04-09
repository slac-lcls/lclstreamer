from pathlib import Path
from typing import Literal, Optional, Self

from h5py._hl.base import ValuesView
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",  # Allows extra attributes during validation
    )


class HDF5SerializerParameters(CustomBaseModel):
    compression_level: int = Field(default=3)
    compression: Optional[
        Literal[
            "gzip",
            "gzip_with_shuffle",
            "bitshuffle_with_lz4",
            "bitshuffle_with_zstd",
            "zfp",
        ]
    ] = Field(default=None)
    fields: dict[str, str]


class NoOpProcessingPipelineParameters(CustomBaseModel):
    pass


class BinaryDataStreamingDataHandlerParameters(CustomBaseModel):
    urls: list[str] = Field(default=["0.0.0.0:12321"])
    role: Literal["server", "client"] = Field(default="server")
    library: Literal["zmq", "nng"] = Field(default="nng")
    socket_type: Literal["push"] = Field(default="push")


class BinaryFileWritingDataHandlerParameters(CustomBaseModel):
    file_prefix: str = Field(default="")
    file_suffix: str = Field(default="")
    write_directory: Path = Field(default=Path.cwd())


class DataSourceParameters(CustomBaseModel):
    type: str
    model_config = ConfigDict(
        extra="allow",  # Allows extra attributes during validation
    )


class LclstreamerParameters(CustomBaseModel):
    source_identifier: str
    batch_size: int
    event_source: str
    processing_pipeline: str
    data_serializer: str
    data_handlers: list[str]


class ProcessingPipelineParameters(CustomBaseModel):

    NoOpProcessingPipeline: Optional[NoOpProcessingPipelineParameters] = None


class DataSerializerParameters(CustomBaseModel):

    Hdf5Serializer: Optional[HDF5SerializerParameters] = None


class DataHandlerParameters(CustomBaseModel):

    BinaryDataStreamingDataHandler: Optional[
        BinaryDataStreamingDataHandlerParameters
    ] = None

    BinaryFileWritingDataHandler: Optional[BinaryFileWritingDataHandlerParameters] = (
        None
    )


class Parameters(CustomBaseModel):

    lclstreamer: LclstreamerParameters
    data_sources: dict[str, DataSourceParameters]
    data_serializer: DataSerializerParameters
    data_handlers: DataHandlerParameters
    processing_pipeline: ProcessingPipelineParameters

    @model_validator(mode="after")
    def check_model(self) -> Self:
        if self.lclstreamer.processing_pipeline != "NoOpProcessingPipeline":
            if (
                getattr(self.processing_pipeline, self.lclstreamer.processing_pipeline)
                is None
            ):
                raise ValueError(
                    f"No configuration found for {self.processing_pipeline} "
                    "processing pipeline"
                )

        if getattr(self.data_serializer, self.lclstreamer.data_serializer) is None:
            raise ValueError(
                f"No configuration found for {self.data_serializer} " "data serializer"
            )

        data_handler_name: str
        for data_handler_name in self.lclstreamer.data_handlers:
            if (
                getattr(
                    self.data_handlers,
                    data_handler_name,
                )
                is None
            ):
                raise ValueError(
                    f"No configuration found for {data_handler_name} " "data serializer"
                )

        return self
