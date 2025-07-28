#!/sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh

from collections.abc import Iterator
from pathlib import Path
from typing import (
    Annotated,
    Any,
)

import typer
from mpi4py import MPI
from stream.core import stream  # type: ignore
from stream.ops import chop, map, take, tap  # type: ignore

from ..backend.event_source import initialize_event_source
from ..frontend.data_handling import initialize_data_handlers
from ..frontend.data_serializer import initialize_data_serializer
from ..frontend.parameters import load_configuration_parameters
from ..frontend.processing_pipeline import initialize_processing_pipeline
from ..models.parameters import LclstreamerParameters, Parameters
from ..protocols.backend import EventSourceProtocol, StrFloatIntNDArray
from ..protocols.frontend import (
    DataHandlerProtocol,
    DataSerializerProtocol,
    ProcessingPipelineProtocol,
)
from ..utils.stream_utils import clock

app = typer.Typer()


@stream
def filter_incomplete_events(
    events: Iterator[dict[str, StrFloatIntNDArray | None]], max_consecutive: int = 100
) -> Iterator[dict[str, StrFloatIntNDArray | None]]:
    """
    Ddrops events that are incomplete

    Incomplete events are events where the retrieval of one or more data items
    failed.

    Arguments:

        events: An event iterator

    Returns:

        events: An event iterator
    """
    consecutive: int = 0
    ev_num: int = 0
    num_dropped: int = 0
    nfailed: dict[str, int] = {} # number from each detector
    for ev_num, event in enumerate(events):
        if all(v is not None for v in event.values()):
            yield event
            consecutive = 0
            continue
        for name, v in event.items():
            if v is None:
                nfailed[name] = nfailed.get(name, 0)+1
        consecutive += 1
        num_dropped += 1
        if consecutive >= max_consecutive:
            break
    if consecutive >= max_consecutive:
        print(f"Stopping early at event {ev_num} after {consecutive} errors")
        print(f"Failed detector counts: {nfailed}")
    print(f"Processed {ev_num} events with {num_dropped} dropped")


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

    workflow: Any = source.get_events()

    if num_events > 0:
        workflow >>= take(num_events)

    if lclstreamer_parameters.skip_incomplete_events is True:
        workflow >>= filter_incomplete_events(max_consecutive=1)

    workflow >>= map(processing_pipeline.process_data)

    workflow >>= chop(lclstreamer_parameters.batch_size)

    workflow >>= map(processing_pipeline.collect_results)

    workflow >>= map(data_serializer.serialize_data)

    data_handler: DataHandlerProtocol
    for data_handler in data_handlers:
        workflow >>= tap(data_handler.handle_data)

    workflow >>= map(data_counter)

    for stat in workflow >> clock():
        print(f"[Rank {mpi_rank}] {stat}]", flush=True)

    print(f"[Rank {mpi_rank}] Hello, I'm done now.  Have a most excellent day!")
