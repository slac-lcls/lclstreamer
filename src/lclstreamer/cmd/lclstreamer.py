#!/sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh

from collections.abc import Iterator
from pathlib import Path
from typing import (
    Annotated,
    Any,
)

import typer
from mpi4py import MPI
from stream.core import Source, stream
from stream.ops import chop, map, take, tap

from ..backend.event_source import initialize_event_source
from ..frontend.data_handling import initialize_data_handlers
from ..frontend.data_serializer import initialize_data_serializer
from ..frontend.parameters import load_configuration_parameters
from ..frontend.processing_pipeline import initialize_processing_pipeline
from ..utils.stream_utils import clock
from ..models.parameters import LclstreamerParameters, Parameters
from ..protocols.backend import EventSourceProtocol, StrFloatIntNDArray
from ..protocols.frontend import (
    DataHandlerProtocol,
    DataSerializerProtocol,
    ProcessingPipelineProtocol,
)

app = typer.Typer()


@stream
def filter_incomplete_events(
    events: Iterator[dict[str, StrFloatIntNDArray]], max_consecutive: int = 100
) -> Iterator[dict[str, StrFloatIntNDArray]]:
    """
    A stream function that drops events that are incomplete

    Arguments:

        events: An event iterator

    Returns:

        events: An event iterator
    """
    errs = []
    consecutive: int = 0
    ev_num: int = 0
    for ev_num, event in enumerate(events):
        failed: list[str] = [key for key in event.keys() if event[key] is None]
        if len(failed) == 0:
            yield event
            consecutive = 0
            continue
        consecutive += 1
        errs.append(failed)
        if consecutive >= max_consecutive:
            break
    if consecutive >= max_consecutive:
        print(f"Stopping early at event {ev_num} after {consecutive} errors")
        print("Failed detector list:")
        for e in errs:
            print(errs[-consecutive:])
    print(f"Processed {ev_num} events with {len(errs)} dropped.")


def data_counter(data: bytes) -> int:
    """
    Computes the size of the input data

    Arguments:

        data: A byte object storing the data

    Returns:

        size: The size of the data in bytes
    """
    return len(data)


@app.command()
def main(
    config: Annotated[
        Path,
        typer.Option(
            "--config",
            "-c",
            help="configuration file (default: monitor.yaml file in the current "
            "working directory",
        ),
    ] = Path("lclstreamer.yaml"),
    num_events: Annotated[
        int,
        typer.Option(
            "--num-events", "-n", help="number of data events to read before stopping"
        ),
    ] = 0,
) -> None:
    """
    An application that retrieves data from an event source, processes it, serializes
    it, and passes it to a series of data handlers that forwards it to external
    applications. The event source, data processing, serialization strategy, and
    further data handling are defined by a configuration file.
    """
    # 1. Read and recover configuration parameters
    mpi_size: int = MPI.COMM_WORLD.Get_size()
    mpi_rank: int = MPI.COMM_WORLD.Get_rank()

    parameters: Parameters = load_configuration_parameters(filename=config)
    lclstreamer_parameters: LclstreamerParameters = parameters.lclstreamer

    # # geometric sequence (1, 2, 4, ..., 512, 1024, 1024, ...)
    # sizes = gseq(2) >> takewhile(lambda x: x < 1024)
    # sizes << seq(1024, 0)  # pyright: ignore[reportUnusedExpression]

    # 2. Initialize event source and data processing pipeline

    print(f"[Rank {mpi_rank}] Initializing event source....")

    source: EventSourceProtocol = initialize_event_source(
        parameters=parameters,
        worker_pool_size=mpi_size,
        worker_rank=mpi_rank,
    )

    print(f"[Rank {mpi_rank}] Initializing event source: Done!")

    print(f"[Rank {mpi_rank}] Initializing processing pipeline....")
    processing_pipeline: ProcessingPipelineProtocol = initialize_processing_pipeline(
        parameters
    )
    print(f"[Rank {mpi_rank}] Initializing processing pipeline: Done!")

    print(f"[Rank {mpi_rank}] Initializing data serializer....")
    data_serializer: DataSerializerProtocol = initialize_data_serializer(parameters)
    print(f"[Rank {mpi_rank}] Initializing data serializer: Done!")

    print(f"[Rank {mpi_rank}] Inirializing data handlers....")
    data_handlers: list[DataHandlerProtocol] = initialize_data_handlers(parameters)
    print(f"[Rank {mpi_rank}] Inirializing data handlers: Done!")

    # 3. Assemble the stream to execute

    # - Start from a stream of data events (]ionaries)

    workflow: Source[dict[str, Any]] = source.get_events()

    # - Start from a stream of (eventnum, event).
    if num_events > 0:  # truncate to nshots?
        workflow >>= take(num_events)

    # - but don't pass items that contain any None-s.
    #   (note: classes test as True)
    workflow >>= filter_incomplete_events()

    workflow >>= map(processing_pipeline.process_data)

    # - Now chop the stream into lists of length n.
    workflow >>= chop(lclstreamer_parameters.batch_size)

    workflow >>= map(processing_pipeline.collect_results)

    # - Now group those by increasing size and concatenate them.
    # - This makes increasingly large groupings of the output data.
    # s >>= chopper([1, 10, 100, 1000]) >> map(concat_batch) # TODO

    workflow >>= map(data_serializer.serialize_data)

    # 5. The entire stream "runs" when connected to a sink:
    data_handler: DataHandlerProtocol
    for data_handler in data_handlers:
        workflow >>= tap(data_handler.handle_data)

    workflow >>= map(data_counter)

    for stat in workflow >> clock():
        print(f"[Rank {mpi_rank}] {stat}]", flush=True)

    print(f"[Rank {mpi_rank}] Hello, I'm done now.  Have a most excellent day!")
