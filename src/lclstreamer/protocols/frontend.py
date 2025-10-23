from collections.abc import Iterator
from typing import Callable
from typing_extensions import Protocol, TypeAlias

from aiostream.core import PipableOperator

from ..models.parameters import Parameters, ProcessingPipelineParameters
from .backend import StrFloatIntNDArray
from ..models.types import LossyEvent, Event, StrFloatIntNDArray

""" A processing pipeline is a PipableOperator that takes a stream of events
    and returns a stream of events.
"""
# this is the type of the function which outputs a processing pipeline
#ProcessingPipelineProtocol = TypeAlias[ Callable[[ProcessingPipelineParameters], PipableOperator[LossyEvent, [], LossyEvent]] ]
# this is the actual processing pipeline type
ProcessingPipelineProtocol : TypeAlias = PipableOperator[LossyEvent, [], LossyEvent]

class DataSerializerProtocol(Protocol):
    def __init__(self, parameters: Parameters):
        """Initializes the data serializers"""
        ...

    def serialize_data(self, data: dict[str, StrFloatIntNDArray]) -> bytes:
        """Serializes the data"""
        ...


class DataHandlerProtocol(Protocol):
    def __init__(self, parameters: Parameters):
        """Initializes the data handler"""
        ...

    def handle_data(self, data: bytes) -> None:
        """Handles the data"""
        ...
