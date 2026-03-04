from ..models.parameters import Parameters
from ..utils.logging import log_error_and_exit
from ..utils.protocols import ProcessingPipelineProtocol
from .crystallography.peaknet import (
    PeaknetPreprocessingPipeline as PeaknetPreprocessingPipeline,
)
from .generic.generic import BatchProcessingPipeline as BatchProcessingPipeline


def initialize_processing_pipeline(
    parameters: Parameters,
) -> ProcessingPipelineProtocol:
    """
    Initializes the processing pipeline specified by the configuration parameters

    Arguments:

        parameters: The configuration parameters

    Returns:

        data_handlers: An initialized processing pipeline
    """
    try:
        processing_pipeline: ProcessingPipelineProtocol = globals()[
            parameters.processing_pipeline.type
        ](parameters.processing_pipeline)
    except NameError:
        log_error_and_exit(
            f"Event source {parameters.processing_pipeline.type} is not available"
        )

    return processing_pipeline
