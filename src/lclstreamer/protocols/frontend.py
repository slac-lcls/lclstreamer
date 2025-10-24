from collections.abc import Iterator
from typing import Callable, Self
from typing_extensions import Protocol, TypeAlias
from contextlib import AbstractAsyncContextManager

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

class DataHandlerProtocol(Protocol, AbstractAsyncContextManager):
    def __init__(self, parameters: Parameters):
        """Initializes the data handler.

           Use this as in,

               async with handler(parameters) as handle_data:
                   async for data in stream:
                       await handle_data(data)
        """
        ...

    async def __aenter__(self) -> Self:
        return self
    async def __aexit__(self, exc_type, exc, tb) -> None:
        pass

    async def __call__(self, data: bytes) -> None:
        """Handles the data"""
        ...
