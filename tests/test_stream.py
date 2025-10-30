import multiprocessing
import os
import time
import signal
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Tuple

from pynng import Pull0, Timeout # type: ignore[import-untyped]
from typer.testing import CliRunner

from lclstreamer.cmd.lclstreamer import app

runner: CliRunner = CliRunner()

configuration: str = """
source_identifier: "none"
skip_incomplete_events: false

data_sources:
    random:
        type: GenericRandomNumpyArray
        array_shape: 200,20
        array_dtype: float32

event_source:
    type: InternalEventSource
    number_of_events_to_generate: 1009

processing_pipeline:
    type: BatchProcessingPipeline
    batch_size: 10

data_serializer:
    type: HDF5BinarySerializer
    compression_level: 3
    compression: zfp
    fields:
        random: /data/random

data_handlers:
  - type: BinaryDataStreamingDataHandler
    urls:
        - "tcp://127.0.0.1:50101"
    role: client
    library: nng
    socket_type: push
"""

@contextmanager
def child_process(target_func, *args):
    """
    A context manager that sets up a pipe
    and starts a new multiprocessing.Process to run a target function.

    It ensures the process is terminated after a timeout upon exit.
    """
    p = None

    try:
        parent_conn, child_conn = multiprocessing.Pipe()
        p = multiprocessing.Process(target=target_func,
                                    args=(child_conn,)+tuple(args))
        p.start()
        yield parent_conn, p

    finally:
        # 5. Cleanup block: Ensure the process terminates
        if p is not None:
            p.join(timeout=1.0)
            if p.is_alive():
                print(f"\n⚠️ Process (PID {p.pid}) did not complete in 1 second. Terminating...")
                p.terminate()
                p.join() # Wait for the process to be fully terminated
            else:
                print(f"\n✅ Process (PID {p.pid}) completed successfully.")

"""Create a child process and run fn.
    After context completes, the child
    process is sent a SIGTERM.
@contextmanager
def child_process(function: Callable[[str], None], args: list[str]):

    child_pid = os.fork()
    if child_pid:  # parent process yields
        try:
            yield
        finally:
            os.kill(child_pid, signal.SIGTERM)
    else:  # child process
        function(*args)
"""


def run_pull(conn, uri: str) -> None:
    count = 0
    done = 0
    started = 0
    def show_open(pipe):
        nonlocal started
        print("Pull: pipe opened")
        started += 1
    def show_close(pipe):
        nonlocal done
        print("Pull: pipe closed")
        done += 1

    try:
        with Pull0(listen=uri, recv_timeout=500) as pull:
            pull.add_post_pipe_connect_cb(show_open)
            pull.add_post_pipe_remove_cb(show_close)
            while started == 0 or (done != started):
                try:
                    _: bytes = pull.recv()
                    count += 1
                    time.sleep(0.001)
                except Timeout:
                    pass
    except Exception as e:
        print("Pull raised error: {e}")
        pass
    conn.send(count)
    conn.close()

def test_app() -> None:
    with child_process(run_pull, "tcp://127.0.0.1:50101") as (conn, p):
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
                #print(result.exc_info)
                traceback.print_tb(result.exc_info[2])

            assert result.exit_code == 0

            if conn.poll(2.0):
                count = conn.recv()
                print(f"Receiver counted {count} messages")
                assert count == 101
            else:
                assert False, "Receiver did not report before its timeout."
    pass
