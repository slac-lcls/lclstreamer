import os
import signal
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable

from pynng import Pull0  # type: ignore
from typer.testing import CliRunner

from lclstreamer.cmd.lclstreamer import app

runner: CliRunner = CliRunner()

configuration: str = """
lclstreamer:
    source_identifier: "none"
    event_source: InternalEventSource
    processing_pipeline: BatchProcessingPipeline
    data_serializer: Hdf5BinarySerializer
    skip_incomplete_events: false
    data_handlers:
        - BinaryDataStreamingDataHandler

data_sources:
    random:
        type: GenericRandomNumpyArray
        array_shape: 20,2
        array_dtype: float32

event_source:
    InternalEventSource:
        number_of_events_to_generate: 1001


processing_pipeline:
    BatchProcessingPipeline:
        batch_size: 10

data_serializer:
    Hdf5BinarySerializer:
        compression_level: 3
        compression: zfp
        fields:
            random: /data/random

data_handlers:
    BinaryDataStreamingDataHandler:
        urls:
            - "tcp://127.0.0.1:50101"
        role: client
        library: nng
        socket_type: push
"""


@contextmanager
def child_process(function: Callable[[str], None], args: list[str]):
    """Create a child process and run fn.

    After context completes, the child
    process is sent a SIGTERM.
    """
    child_pid = os.fork()
    if child_pid:  # parent process yields
        try:
            yield
        finally:
            os.kill(child_pid, signal.SIGTERM)
    else:  # child process
        function(*args)


def run_pull(uri: str):
    socket = Pull0(listen="tcp://127.0.0.1:50101")
    while True:
        _: Any = socket.recv()


def test_app() -> None:
    with child_process(run_pull, ["tcp://127.0.0.1:50101"]):
        with runner.isolated_filesystem():
            current_directory: Path = Path.cwd()
            configuration_file_name: Path = current_directory / "lclstreamer.yaml"
            configuration_file_name.write_text(configuration, "utf-8")
            result = runner.invoke(app, ["--config", str(configuration_file_name)])
            print("--- Output")
            print(result.output)
            if result.exception is not None:
                print("--- Exceptions")
                print(result.exception)
                print(result.exc_info)

            assert result.exit_code == 0
