import sys

from pynng import ConnectionRefused, Push0  # pyright: ignore[reportMissingTypeStubs]
from zmq import PUSH, Context, Socket, ZMQError

from ...models.parameters import (
    BinaryDataStreamingDataHandlerParameters,
)
from ...utils.logging import log
from ...utils.protocols import DataHandlerProtocol


class BinaryDataStreamingDataHandler(DataHandlerProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self, data_handler_parameters: BinaryDataStreamingDataHandlerParameters
    ) -> None:
        """
        Initializes a binary data streaming data handler

        This data handler sends a byte object through a ZMQ or NNG socket.

        Arguments:

              parameters: The configuration parameters
        """
        if data_handler_parameters.library == "nng":
            self._streaming: (
                BinaryStreamingPushDataHandlerNng | BinaryStreamingPushDataHandlerZmq
            ) = BinaryStreamingPushDataHandlerNng(data_handler_parameters)
        else:
            self._streaming = BinaryStreamingPushDataHandlerZmq(data_handler_parameters)

    def __call__(self, data: bytes) -> None:
        self._streaming(data)


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
        self._socket: Push0 = Push0()

        url: str
        for url in self.data_handler_parameters.urls:
            try:
                if self.data_handler_parameters.role == "server":
                    self._socket.listen(url)  # pyright: ignore[reportUnknownMemberType]
                else:
                    self._socket.dial(url, block=True)  # pyright: ignore[reportUnknownMemberType]
            except ConnectionRefused as err:
                log.error(
                    f"Unable to connect to the URL {url} due to the following "
                    f"error: {err}"
                )

    def __call__(self, data: bytes) -> None:
        """
        Sends a binary object through the NNG socket

        Arguments:

            data: a bytes object
        """
        return self._socket.send(data)  # pyright: ignore[reportUnknownMemberType]


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
        self._context: Context[Socket[bytes]] = Context()
        self._socket: Socket[bytes] = self._context.socket(PUSH)
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
        """
        Sends a binary object through the ZMQ socket

        Arguments:

            data: a bytes object
        """
        self._socket.send(data)

    def __del__(self) -> None:
        self._context.destroy()
