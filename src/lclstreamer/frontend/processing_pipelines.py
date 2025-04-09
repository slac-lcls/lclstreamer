from ..models.parameters import LclstreamerParameters, Parameters
from ..protocols.frontend import ProcessingPipelineProtocol
from .generic_processing_pipelines import NoOpProcessingPipeline  # noqa: F401


def initialize_processing_pipeline(
    parameters: Parameters,
) -> ProcessingPipelineProtocol:
    """ """
    lclstreamer_parameters: LclstreamerParameters = parameters.lclstreamer

    try:
        processing_pipeline: ProcessingPipelineProtocol = globals()[
            lclstreamer_parameters.processing_pipeline
        ](parameters)
    except NameError:
        raise RuntimeError(
            f"Event source {lclstreamer_parameters.event_source} is not available"
        )

    return processing_pipeline
