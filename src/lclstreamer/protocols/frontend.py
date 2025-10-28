from collections.abc import Iterator, AsyncIterator, AsyncIterable
from typing import Callable, Self
from typing_extensions import Protocol, TypeAlias
from contextlib import AbstractAsyncContextManager

from aiostream.core import PipableOperator

from ..models.parameters import Parameters, ProcessingPipelineParameters
from .backend import StrFloatIntNDArray
from ..models.types import LossyEvent, Event, StrFloatIntNDArray


class ProcessingPipelineProtocol(Protocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        parameters: Parameters,
    ):
        """Initializes the data processing pipeline"""
        ...

    def __call__(
        self, stream: AsyncIterable[LossyEvent]
    ) -> AsyncIterator[LossyEvent]:
        """Applies the data processing pipeline"""
        ...


class DataSerializerProtocol(Protocol):
    def __init__(self, parameters: Parameters):
        """Initializes the data serializers"""
        ...

    def serialize_data(self, data: Event) -> bytes:
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
