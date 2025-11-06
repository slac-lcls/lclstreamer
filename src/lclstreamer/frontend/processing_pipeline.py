import sys

from ..models.parameters import Parameters
from ..protocols.frontend import ProcessingPipelineProtocol
from ..utils.logging_utils import log
from .processing_pipelines.generic import (
    BatchProcessingPipeline,
    PeaknetPreprocessingPipeline,
)


def initialize_processing_pipeline(
    parameters: Parameters,
) -> ProcessingPipelineProtocol:
    """
    Initializes the Processing Pipeline specified by the configuration parameters

    Arguments:

        parameters: The configuration parameters

    Returns:

        data_handlers: An initialized Processing Pipeline
    """
    processing_pipeline: ProcessingPipelineProtocol = globals()[
        parameters.processing_pipeline.type
    ](parameters.processing_pipeline)

    return processing_pipeline
