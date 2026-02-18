import sys
from typing import Self

from pynng import ConnectionRefused, Push0  # type: ignore
from zmq import PUSH, ZMQError
from zmq.asyncio import Context, Socket

from ...models.parameters import (
    BinaryDataStreamingDataHandlerParameters,
    DataHandlerParameters,
)
from ...protocols.frontend import DataHandlerProtocol
from ...utils.logging_utils import log


class BinaryDataStreamingDataHandler(DataHandlerProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(self, data_handler_parameters: BinaryDataStreamingDataHandlerParameters) -> None:
        """
        Initializes a binary data streaming data handler

        This data handler sends a byte object through a ZMQ or NNG socket.

        Arguments:

              parameters: The configuration parameters
        """
        self.async_on = data_handler_parameters.async_on

        if data_handler_parameters.library == "nng":
            self._streaming: (
                BinaryStreamingPushDataHandlerNng | BinaryStreamingPushDataHandlerZmq
            ) = BinaryStreamingPushDataHandlerNng(data_handler_parameters)
        else:
            self._streaming = BinaryStreamingPushDataHandlerZmq(data_handler_parameters)
        #if async_on:
        #    print("picked async")
        #    self.__call__ = self._asynccall
        #else:
        #    print("picked sync")
        #    self.__call__ = self._synccall

    async def __aenter__(self) -> Self:
        await self._streaming.__aenter__()
        return self

    async def __aexit__(self, *exc) -> None:
        await self._streaming.__aexit__(*exc)

    async def _asynccall(self, data: bytes) -> None:
        """
        Stream a bytes object through the network socket.

        Arguments:

            data: A bytes object
        """
        await self._streaming(data)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc) -> None:
        pass

    def _synccall(self, data: bytes) -> None:
        self._streaming(data)

    def __call__(self, data: bytes) -> None:
        if self.async_on:
            return self._asynccall(data)
        else:
            return self._synccall(data)


class BinaryStreamingPushDataHandlerNng:
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self, data_handler_parameters: BinaryDataStreamingDataHandlerParameters
    ) -> None:
        """
        Initializes an NNG binary data streaming socket

        Arguments:

            data_handler_parameters: The configuration parameters for the streaming
                data_handler
        """
        self.data_handler_parameters = data_handler_parameters
        self._async_on = data_handler_parameters.async_on
        if self._async_on == 0:
            self._setup_socket()

    def _setup_socket(self):
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

    async def __aenter__(self):
        self._setup_socket()

    async def _asynccall(self, data: bytes) -> None:
        """
        Sends a binary object through the NNG socket

        Arguments:

            data: a bytes object
        """
        await self._socket.asend(data)

    def _synccall(self, data: bytes) -> None:
        """
        Sends a binary object through the NNG socket

        Arguments:

            data: a bytes object
        """
        return self._socket.send(data)

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """
        Destructor
        """
        self._socket.close()

    def __exit__(self, exc_type, exc, tb) -> None:
        """
        Destructor
        """
        self._socket.close()

    def __call__(self, data: bytes) -> None:
        if self._async_on:
            return self._asynccall(data)
        else:
            return self._synccall(data)

class BinaryStreamingPushDataHandlerZmq:
    def __init__(
        self, data_handler_parameters: BinaryDataStreamingDataHandlerParameters
    ) -> None:
        """
        Initializes a ZMQ binary data streaming socket

        Arguments:

            data_handler_parameters: The configuration parameters for the streaming
                data_handler
        """
        self.data_handler_parameters = data_handler_parameters
        self._async_on = data_handler_parameters.async_on
        self._context: Context = Context()
        if self._async_on == 0:
            self._socket: Socket = self._context.socket(PUSH)
            url: str
            for url in data_handler_parameters.urls:
                try:
                    if data_handler_parameters.role == "server":
                        self._socket.bind(url)
                    else:
                        self._socket.connect(url)
                except ZMQError as err:
                    log.error(
                        f"Unable to connect to the URL {url} due to the following "
                        f"error: {err}"
                    )
                    sys.exit(1)



    def __call__(self, data: bytes) -> None:
        if self._async_on:
            return self._asynccall(data)
        else:
            return self._synccall(data)

    async def __aenter__(self) -> Self:
        self._socket: Socket = self._context.socket(PUSH)

        url: str
        for url in self.data_handler_parameters.urls:
            try:
                if self.data_handler_parameters.role == "server":
                    self._socket.bind(url)
                else:
                    self._socket.connect(url)
                print("ZMQ BINARY sending")
            except ZMQError as err:
                log.error(
                    f"Unable to connect to the URL {url} due to the following "
                    f"error: {err}"
                )
                sys.exit(1)
        return self

    async def _asynccall(self, data: bytes) -> None:
        """
        Sends a binary object through the ZMQ socket

        Arguments:

            data: a bytes object
        """
        await self._socket.send(data)

    def _synccall(self, data: bytes) -> None:
        """
        Sends a binary object through the ZMQ socket

        Arguments:

            data: a bytes object
        """
        self._socket.send(data)

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """
        Destructor
        """
        self._socket.close()

    def __exit__(self, exc_type, exc, tb) -> None:
        """
        Destructor
        """
        self._socket.close()

    def __del__(self) -> None:
        self._context.destroy()
