from typing import Any, Union

from pynng import ConnectionRefused, Push0  # type: ignore
from zmq import PUSH, Context, Socket, ZMQError

from ..models.parameters import BinaryDataStreamingDataHandlerParameters, Parameters
from ..protocols.frontend import DataHandlerProtocol


class BinaryDataStreamingDataHandler(DataHandlerProtocol):

    def __init__(self, parameters: Parameters):

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

        self._streaming.handle_data(data)


class BinaryStreamingPushDataHandlerNng:

    def __init__(
        self, data_handler_parameters: BinaryDataStreamingDataHandlerParameters
    ):

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

        self._socket.send(data)

    def __del__(self) -> None:
        self._socket.close()


class BinaryStreamingPushDataHandlerZmq:

    def __init__(
        self, data_handler_parameters: BinaryDataStreamingDataHandlerParameters
    ):

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

        self._socket.send(data)

    def __del__(self) -> None:
        self._socket.close()
        self._context.destroy()
