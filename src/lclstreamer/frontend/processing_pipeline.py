import sys

from ..models.parameters import LclstreamerParameters, Parameters
from ..protocols.frontend import ProcessingPipelineProtocol
from ..utils.logging_utils import log
from .processing_pipelines.generic import (  # noqa: F401
    BatchProcessingPipeline,
    PreprocessingBatchPipeline,
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
    lclstreamer_parameters: LclstreamerParameters = parameters.lclstreamer

    try:
        processing_pipeline: ProcessingPipelineProtocol = globals()[
            lclstreamer_parameters.processing_pipeline
        ](parameters.processing_pipeline)
    except NameError:
        log.error(
            f"Processing pipeline {lclstreamer_parameters.processing_pipeline} "
            "is not available"
        )
        sys.exit(1)

    return processing_pipeline
