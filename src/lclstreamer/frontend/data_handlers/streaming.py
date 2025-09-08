import sys
from typing import Any

from pynng import ConnectionRefused, Message, Push0  # type: ignore
from zmq import PUSH, Context, Socket, ZMQError

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

    def __init__(self, parameters: DataHandlerParameters):
        """
        Initializes a binary data streaming data handler

        This data handler sends a byte object through a ZMQ or NNG socket.

        Arguments:

              parameters: The configuration parameters
        """
        if parameters.BinaryDataStreamingDataHandler is None:
            log.error(
                "No configuration parameters found for BinaryStreamingPushDataHandler"
            )
            sys.exit(1)

        data_handler_parameters: BinaryDataStreamingDataHandlerParameters = (
            parameters.BinaryDataStreamingDataHandler
        )

        if data_handler_parameters.library == "nng":
            self._streaming: (
                BinaryStreamingPushDataHandlerNng | BinaryStreamingPushDataHandlerZmq
            ) = BinaryStreamingPushDataHandlerNng(data_handler_parameters)
        else:
            self._streaming = BinaryStreamingPushDataHandlerZmq(data_handler_parameters)

    def __call__(self, data: bytes) -> None:
        """
        Stream a bytes object through the network socket.

        Arguments:

            data: A bytes object
        """
        self._streaming.handle_data(data)


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
        self._socket: Any = Push0()

        url: str
        for url in data_handler_parameters.urls:
            try:
                if data_handler_parameters.role == "server":
                    self._socket.listen(url)
                else:
                    self._socket.dial(url, block=True)
            except ConnectionRefused as err:
                log.error(
                    f"Unable to connect to the URL {url} due to the following "
                    f"error: {err}"
                )
                sys.exit(1)

    def handle_data(self, data: bytes) -> None:
        """
        Sends a binary object through the NNG socket

        Arguments:

            data: a bytes object
        """
        self._socket.send(data)

    def __del__(self) -> None:
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

    def handle_data(self, data: bytes) -> None:
        """
        Sends a binary object through the ZMQ socket

        Arguments:

            data: a bytes object
        """
        self._socket.send(data)

    def __del__(self) -> None:
        """
        Destructor
        """
        self._socket.close()
        self._context.destroy()
