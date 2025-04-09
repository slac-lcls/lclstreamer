from collections.abc import Generator

from stream.core import source as source
from stream.core import stream as stream

from ..models.parameters import LCLStreamerParameters
from ..protocols.backend import EventSourceProtocol, StrFloatIntNDArray
from .psana1_event_sources import Psana1EventSource  # noqa: F401


class DataSource:

    def __init__(
        self,
        *,
        source_string: str,
        parameters: LCLStreamerParameters,
        node_pool_size: int,
    ) -> None:
        try:
            self._event_source: EventSourceProtocol = globals()[
                parameters.event_source
            ](
                source_string=source_string,
                node_pool_size=node_pool_size,
                parameters=parameters,
            )
        except NameError:
            raise RuntimeError(
                f"Event source {parameters.event_source} is not available"
            )

    @source
    def get_data(self) -> Generator[dict[str, StrFloatIntNDArray]]:
        """ """
        for event in self._event_source.get_data():
            yield event


@stream
def filter_incomplete_events(
    events: Generator[dict[str, StrFloatIntNDArray]], max_consecutive: int = 100
) -> Generator[dict[str, StrFloatIntNDArray]]:
    """ """
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
