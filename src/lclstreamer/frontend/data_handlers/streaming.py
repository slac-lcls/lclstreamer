from typing import Any, Union

from pynng import ConnectionRefused, Push0  # type: ignore
from zmq import PUSH, Context, Socket, ZMQError

from ...models.parameters import BinaryDataStreamingDataHandlerParameters, Parameters
from ...protocols.frontend import DataHandlerProtocol


class BinaryDataStreamingDataHandler(DataHandlerProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(self, parameters: Parameters):
        """
        Initializes a binary data streaming data handler

        This data handler streams a byte object over a Zmq or Nng socket.

        Arguments:

              parameters: The configuration parameters
        """
        if parameters.data_handlers.BinaryDataStreamingDataHandler is None:
            raise RuntimeError(
                "No configuration parameters found forBinaryStreamingPushDataHandler"
            )

        data_handler_parameters: BinaryDataStreamingDataHandlerParameters = (
            parameters.data_handlers.BinaryDataStreamingDataHandler
        )

        if data_handler_parameters.library == "nng":
            self._streaming: Union[
                BinaryStreamingPushDataHandlerNng, BinaryStreamingPushDataHandlerZmq
            ] = BinaryStreamingPushDataHandlerNng(data_handler_parameters)
        else:
            self._streaming = BinaryStreamingPushDataHandlerZmq(data_handler_parameters)

    def handle_data(self, data: bytes) -> None:
        """
        Stream a bytes object through a Zmq or Nng socket.

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
        Initializes an Nng binary data streaming socket

        Arguments:

            data_handler_parameters: The configuration parameters for the streaming
                data_handler
        """
        self._socket: Any = Push0()

        url: str
        for url in data_handler_parameters.urls:
            try:
                if data_handler_parameters.role == "server":
                    self._socket.listen(url, block=True)
                else:
                    self._socket.dial(url, block=True)
            except ConnectionRefused as err:
                raise RuntimeError(
                    f"Unable to connect to the URL {url} due to the following "
                    f"error: {err}"
                )

    def handle_data(self, data: bytes) -> None:
        """
        Sends a binary object through the Nng socket

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
        Initializes a Zmq binary data streaming socket

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
                raise RuntimeError(
                    f"Unable to connect to the URL {url} due to the following "
                    f"error: {err}"
                )

    def handle_data(self, data: bytes) -> None:
        """
        Sends a binary object through the Nng socket

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
