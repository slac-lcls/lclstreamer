import os
from io import BytesIO
import signal

import h5py  # type: ignore
from pynng import Pull0  # type: ignore

import pytest
from typer.testing import CliRunner
from lclstreamer.cmd.lclstreamer import app

runner = CliRunner()

template = """
lclstreamer:
    source_identifier: "none"
    event_source: GenericEventSource
    processing_pipeline: BatchProcessingPipeline
    data_serializer: Hdf5Serializer
    skip_incomplete_events: false
    data_handlers:
        - BinaryDataStreamingDataHandler

data_sources:
    random:
        type: GenericRandomNumpyArray
        array_shape: 20,2
        array_dtype: float32

event_source:
    GenericEventSource:
        events: 1001

processing_pipeline:
    BatchProcessingPipeline:
        batch_size: 10

data_serializer:
    Hdf5Serializer:
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

from contextlib import contextmanager

@contextmanager
def child_process(fn, *args, **kws):
    """ Create a child process and run fn.

        After context completes, the child
        process is sent a SIGTERM.
    """
    child_pid = os.fork()
    if child_pid: # parent process yields
       try:
           yield
       finally:
           os.kill(child_pid, signal.SIGTERM)
    else: # child process
       fn( *args, **kws)

def run_pull(**args):
    socket = Pull0(**args)
    while True:
        msg = socket.recv()
        #fh = h5py.File(BytesIO(msg))
        #fh.close()

#@pytest.mark.asyncio
#async def test_some_asyncio_code():
#    res = await library.do_something()
#    assert b"expected result" == res

def test_app(tmpdir):
    cfg = tmpdir/"lclstreamer.yaml"
    cfg.write_text(
        template.format(tmpdir=str(tmpdir)),
        "utf-8"
    )

    with child_process(run_pull, listen="tcp://127.0.0.1:50101"):
        result = runner.invoke(app, ["-c", str(cfg)])

    assert result.exit_code == 0
    print(result.stdout)
    print("---")
    print(result.output)
