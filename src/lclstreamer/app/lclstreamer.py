#!/sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh

from pathlib import Path
from typing import (
    Annotated,
    Any,
)

import typer
from mpi4py import MPI
from stream.core import Source
from stream.ops import chop, gseq, map, seq, take, takewhile

from ..backend.event_source import DataSource, filter_incomplete_events
from ..frontend.parameters import load_configuration_parameters
from ..frontend.processing_pipeline import ProcessingPipeline
from ..models.parameters import LCLStreamerParameters

app = typer.Typer()


@app.command()
def main(
    *,
    source_string: Annotated[
        str,
        typer.Argument(help="Data source string"),
    ],
    config: Annotated[
        Path,
        typer.Option(
            "--config",
            "-c",
            help="configuration file (default: monitor.yaml file in the current "
            "working directory",
        ),
    ] = Path("monitor.yaml"),
    num_events: Annotated[
        int,
        typer.Option(
            "--num-events", "-n", help="number of data events to read before stopping"
        ),
    ] = 0,
) -> None:

    # 1. Read and recover configuration parameters
    mpi_size: int = MPI.COMM_WORLD.Get_size()
    parameters: LCLStreamerParameters = load_configuration_parameters(filename=config)

    # geometric sequence (1, 2, 4, ..., 512, 1024, 1024, ...)
    sizes = gseq(2) >> takewhile(lambda x: x < 1024)
    sizes << seq(1024, 0)  # pyright: ignore[reportUnusedExpression]

    # 2. Initialize event source and data processing pipeline

    source: DataSource = DataSource(
        source_string=source_string, parameters=parameters, node_pool_size=mpi_size
    )

    processing_pipeline: ProcessingPipeline = ProcessingPipeline(
        parameters=parameters,
    )

    # 3. Assemble the stream to execute

    # - Start from a stream of data events (]ionaries)

    workflow: Source[dict[str, Any]] = source.get_data()

    # - Start from a stream of (eventnum, event).
    if num_events > 0:  # truncate to nshots?
        workflow >>= take(num_events)

    # - but don't pass items that contain any None-s.
    #   (note: classes test as True)
    workflow >>= filter_incomplete_events()

    workflow >>= map(processing_pipeline.process_data)

    # - Now chop the stream into lists of length n.
    workflow >>= chop(512)

    workflow >>= map(processing_pipeline.collect_results)

    # - Now group those by increasing size and concatenate them.
    # - This makes increasingly large groupings of the output data.
    # s >>= chopper([1, 10, 100, 1000]) >> map(concat_batch) # TODO

    # 5. The entire stream "runs" when connected to a sink:
    if dial is None:
        s >>= write_out(outname)
    else:
        send_pipe = map(serialize_h5) >> pusher(dial, 1)
        # do both hdf5 file writing
        # and send_pipe.  Use cut[0] to pass only
        # the result of write_out (event counts).
    s >>= split(write_out(outname), send_pipe) >> cut[0]
    for stat in s >> clock():
    print(stat, flush=True)

    print("Hello, I'm done now.  Have a most excellent day!")
