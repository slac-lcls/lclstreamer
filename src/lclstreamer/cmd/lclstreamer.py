#!/sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh

import asyncio
from collections.abc import AsyncIterator, AsyncIterable
from contextlib import AsyncExitStack
from pathlib import Path
from typing import (
    Annotated,
    Any,
)

import typer
from mpi4py import MPI
from aiostream import Stream, pipable_operator, pipe, streamcontext, async_

from ..backend.event_source import initialize_event_source
from ..frontend.data_handling import ParallelDataHandler
from ..frontend.data_serializer import initialize_data_serializer
from ..frontend.parameters import load_configuration_parameters
from ..frontend.processing_pipeline import initialize_processing_pipeline
from ..models.parameters import LclstreamerParameters, Parameters
from ..models.types import LossyEvent, Event, StrFloatIntNDArray
from ..protocols.backend import EventSourceProtocol
from ..protocols.frontend import (
    DataHandlerProtocol,
    DataSerializerProtocol,
    ProcessingPipelineProtocol,
)
from ..utils.stream_utils import clock, Clock

app = typer.Typer()


@pipable_operator
async def filter_incomplete_events(
    events: AsyncIterable[LossyEvent], max_consecutive: int = 100
) -> AsyncIterator[LossyEvent]:
    """
    Drops events that are incomplete

    Incomplete events are events where the retrieval of one or more data items
    failed.

    Arguments:

        events: An event iterator
        max_consecutive (int): maximum number of consecutive frames containing any "missing" value before terminating early

    Returns:

        events: An event iterator
    """
    consecutive: int = 0
    ev_num: int = 0
    num_dropped: int = 0
    nfailed: dict[str, int] = {}  # number from each detector
    async with streamcontext(events) as streamer:
        ev_num = -1
        async for event in streamer: # async doesn't commute through enumerate()
            ev_num += 1
            if all(v is not None for v in event.values()):
                yield event
                consecutive = 0
                continue
            for name, v in event.items():
                if v is None:
                    nfailed[name] = nfailed.get(name, 0) + 1
            consecutive += 1
            num_dropped += 1
            if consecutive >= max_consecutive:
                break
    if consecutive >= max_consecutive:
        print(f"Stopping early after {consecutive} errors")
    if num_dropped > 0:
        print(f"Failed detector counts: {nfailed}")
    print(f"Processed {ev_num+1} events with {num_dropped} dropped")


def data_counter(data: bytes) -> int:
    """
    Computes the size of the input data

    Arguments:

        data: A byte object storing the data

    Returns:

        size: The size of the data in bytes
    """
    return len(data)


async def amain(
    config: Path,
    num_events: int,
) -> None:
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
    processing_pipeline.__name__="processing_pipeline"
    run_processing = pipable_operator(processing_pipeline)
    print(f"[Rank {mpi_rank}] Initializing processing pipeline: Done!")

    print(f"[Rank {mpi_rank}] Initializing data serializer....")
    data_serializer: DataSerializerProtocol = initialize_data_serializer(parameters)
    print(f"[Rank {mpi_rank}] Initializing data serializer: Done!")

    print(f"[Rank {mpi_rank}] Initializing data handlers....")
    parallel_data_handler = ParallelDataHandler(parameters.data_handlers)
    print(f"[Rank {mpi_rank}] Initializing data handlers: Done!")

    async with parallel_data_handler as handle_data: # connect / open files / etc.
        lossy_events: Stream[LossyEvent] = Stream(source.get_events)

        if num_events > 0:
            lossy_events |= pipe.take(num_events)

        if lclstreamer_parameters.skip_incomplete_events is True:
            lossy_events |= filter_incomplete_events.pipe(max_consecutive=1)

        events = lossy_events | run_processing.pipe()

        serialized = ( events
                     | pipe.map(data_serializer.serialize_data) # type: ignore[arg-type]
                     | pipe.action(async_(handle_data))
                     )

        workflow : Stream[Clock] = ( serialized
                   | pipe.map(data_counter) # type: ignore[arg-type]
                   | clock.pipe()
                   )

        async with streamcontext(workflow) as streamer:
            async for stat in streamer:
                print(f"[Rank {mpi_rank}] {stat}]", flush=True)

    print(f"[Rank {mpi_rank}] Hello, I'm done now.  Have a most excellent day!")

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
    asyncio.run( amain(config, num_events) )
