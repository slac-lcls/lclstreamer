import sys
from typing import Union, Self

from pynng import ConnectionRefused, Push0  # type: ignore
from zmq import PUSH, ZMQError
from zmq.asyncio import Context, Socket

from ...models.parameters import BinaryDataStreamingDataHandlerParameters, Parameters
from ...protocols.frontend import DataHandlerProtocol
from ...utils.logging_utils import log


class BinaryDataStreamingDataHandler(DataHandlerProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(self, parameters: Parameters):
        """
        Initializes a binary data streaming data handler

        This data handler sends a byte object through a ZMQ or NNG socket.

        Arguments:

              parameters: The configuration parameters
        """
        if parameters.data_handlers.BinaryDataStreamingDataHandler is None:
            log.error(
                "No configuration parameters found for BinaryStreamingPushDataHandler"
            )
            sys.exit(1)

        data_handler_parameters: BinaryDataStreamingDataHandlerParameters = (
            parameters.data_handlers.BinaryDataStreamingDataHandler
        )

        if data_handler_parameters.library == "nng":
            self._streaming: Union[
                BinaryStreamingPushDataHandlerNng, BinaryStreamingPushDataHandlerZmq
            ] = BinaryStreamingPushDataHandlerNng(data_handler_parameters)
        else:
            self._streaming = BinaryStreamingPushDataHandlerZmq(data_handler_parameters)

    async def __aenter__(self) -> Self:
        await self._streaming.__aenter__()
        return self

    async def __aexit__(self, *exc) -> None:
        await self._streaming.__aexit__(*exc)

    async def __call__(self, data: bytes) -> None:
        """
        Stream a bytes object through the network socket.

        Arguments:

            data: A bytes object
        """
        await self._streaming(data)


class BinaryStreamingPushDataHandlerNng:
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self, data_handler_parameters: BinaryDataStreamingDataHandlerParameters
    ):
        """
        Initializes an NNG binary data streaming socket

        Arguments:

            data_handler_parameters: The configuration parameters for the streaming
                data_handler
        """
        self.data_handler_parameters = data_handler_parameters

    async def __aenter__(self) -> Self:
        self._socket: Push0 = Push0()

        url: str
        for url in self.data_handler_parameters.urls:
            try:
                if self.data_handler_parameters.role == "server":
                    self._socket.listen(url)
                else:
                    self._socket.dial(url, block=True)
            except ConnectionRefused as err:
                log.error(
                    f"Unable to connect to the URL {url} due to the following "
                    f"error: {err}"
                )
                sys.exit(1)
        return self

    async def __call__(self, data: bytes) -> None:
        """
        Sends a binary object through the NNG socket

        Arguments:

            data: a bytes object
        """
        await self._socket.asend(data)

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """
        Destructor
        """
        self._socket.close()


class BinaryStreamingPushDataHandlerZmq:
    def __init__(
        self, data_handler_parameters: BinaryDataStreamingDataHandlerParameters
    ):
        """
        Initializes a ZMQ binary data streaming socket

        Arguments:

            data_handler_parameters: The configuration parameters for the streaming
                data_handler
        """
        self.data_handler_parameters = data_handler_parameters
        self._context: Context[Socket[bytes]] = Context()

    async def __aenter__(self):
        self._socket: Socket[bytes] = self._context.socket(PUSH)

        url: str
        for url in self.data_handler_parameters.urls:
            try:
                if self.data_handler_parameters.role == "server":
                    self._socket.bind(url)
                else:
                    self._socket.connect(url)
            except ZMQError as err:
                log.error(
                    f"Unable to connect to the URL {url} due to the following "
                    f"error: {err}"
                )
                sys.exit(1)

    async def __call__(self, data: bytes) -> None:
        """
        Sends a binary object through the ZMQ socket

        Arguments:

            data: a bytes object
        """
        await self._socket.send(data)

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """
        Destructor
        """
        self._socket.close()

    def __del__(self) -> None:
        self._context.destroy()
