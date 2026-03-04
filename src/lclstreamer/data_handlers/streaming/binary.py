import sys
import time

from zmq import LINGER, PUSH, SNDTIMEO, Context, Socket, ZMQError

from ...models.parameters import (
    BinaryDataStreamingDataHandlerParameters,
)
from ...utils.logging import log
from ...utils.protocols import DataHandlerProtocol


class BinaryDataStreamingDataHandler(DataHandlerProtocol):
    """
    See documentation of the `__init__` function
    """

    def __init__(
        self, data_handler_parameters: BinaryDataStreamingDataHandlerParameters
    ) -> None:
        """
        Initializes a Binary Data Streaming Data Handler

        This data handler sends a byte object through a network socket

        Arguments:

              parameters: The data handler configuration parameters
        """
        if data_handler_parameters.library == "zmq":
            self._streaming: BinaryStreamingPushDataHandlerZmq = (
                BinaryStreamingPushDataHandlerZmq(data_handler_parameters)
            )
        else:
            self._streaming = BinaryStreamingPushDataHandlerZmq(data_handler_parameters)

    def __call__(self, data: bytes) -> None:
        """
        Forwards a binary object to the underlying streaming transport

        Arguments:

            data: A bytes object containing serialized event data
        """
        self._streaming(data)


class BinaryStreamingPushDataHandlerZmq:
    """
    See documentation of the `__init__` function
    """

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
        # Set send timeout to 5 seconds to prevent indefinite blocking
        self._socket.setsockopt(SNDTIMEO, 5000)
        # Set linger to 0 so socket closes immediately without waiting
        self._socket.setsockopt(LINGER, 0)
        url: str
        for url in data_handler_parameters.urls:
            try:
                if data_handler_parameters.role == "server":
                    self._socket.bind(url)
                else:
                    self._socket.connect(url)
                    # Add delay to allow ZMQ connection to fully establish (slow joiner fix)
                    time.sleep(1.0)
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

            data: A bytes object containing serialized event data
        """
        self._socket.send(data)

    def close(self) -> None:
        """Explicitly close the socket and context with timeout"""
        try:
            self._socket.close(linger=0)
            self._context.term()
        except Exception:
            pass

    def __del__(self) -> None:
        """Cleanup on deletion"""
        self.close()
