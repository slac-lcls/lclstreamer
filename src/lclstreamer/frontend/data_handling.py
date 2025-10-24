import sys
from typing import Self
from asyncio import TaskGroup
from contextlib import AsyncExitStack

from ..models.parameters import LclstreamerParameters, Parameters
from ..protocols.frontend import DataHandlerProtocol
from ..utils.logging_utils import log
from .data_handlers.files import BinaryFileWritingDataHandler  # noqa: F401
from .data_handlers.streaming import BinaryDataStreamingDataHandler  # noqa: F401

# Note: Ot would be simpler to write these as functions
# with the @contextlib.asynccontextmanager decorator.
# I *think* they would still type-check OK.

class ParallelDataHandler(DataHandlerProtocol):
    _data_handlers: list[DataHandlerProtocol]
    _stack: AsyncExitStack
    _live_handlers: list[DataHandlerProtocol]

    def __init__(self, parameters: Parameters) -> None:
        """
        A Parallel Data Handler calling all
        of the handlers specified by the configuration parameters
        concurrently.

        Arguments:

            parameters: The configuration parameters

        For more details, see the DataHandlerProtocol.
        """
        lclstreamer_parameters: LclstreamerParameters = parameters.lclstreamer

        data_handlers: list[DataHandlerProtocol] = []

        data_handler_name: str
        for data_handler_name in lclstreamer_parameters.data_handlers:
            try:
                data_handler: DataHandlerProtocol = globals()[data_handler_name](parameters)
                data_handlers.append(data_handler)
            except NameError:
                log.error(
                    f"Data serializer {lclstreamer_parameters.data_handlers} "
                    "is not available"
                )
                sys.exit(1)
        self._data_handlers = data_handlers

    async def __aenter__(self) -> Self:
        #async with AsyncExitStack() as stack - need to manually call aenter and aexit

        self._stack = await AsyncExitStack().__aenter__()
        self._live_handlers = [ await self._stack.enter_async_context(h)
                                for h in self._data_handlers ]
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._stack.__aexit__(exc_type, exc, tb)

    async def __call__(self, data: bytes) -> None:
        """ Handles the data

            Note this method forces synchronization at the end of each
            data item send.  We could, alternately, move the task group
            into aenter/aexit so that data sends get disconnected from
            the pipeline.  However, there many reasons we need to sync
            here.
            
            1. We don't want to return control to the main loop
               / downstream of data_handler before sends are done.

            2. The aiostream pipeline is already running each
               pipeline step concurrently, so we don't need the
               extra concurrency here.

            3. If the output times are very unbalanced, data in
               the pipeline can't be discarded for awhile - leading to a
               memory overflow.
        """
        async with TaskGroup() as tg:
            tasks = [ tg.create_task(h(data)) 
                      for h in self._live_handlers ]
