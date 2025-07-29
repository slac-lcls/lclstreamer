from collections.abc import Iterator
import numpy as np

from ...models.parameters import Parameters
from ...protocols.backend import StrFloatIntNDArray
from ...protocols.frontend import ProcessingPipelineProtocol
from .utils import DataStorage

class NoOpPipeline(ProcessingPipelineProtocol):
    """
    See documentation of the `__init__` function.
    """
    def __init__(self, parameters: Parameters) -> None:
        """
        Initializes a NoOp processing pipeline

        This pipeline performs no operations on the data.
        It simply forwards each item.

        Arguments:

             parameters: The configuration parameters
        """
        pass

    def __call__(
        self, stream: Iterator[dict[str, StrFloatIntNDArray]]
    ) -> Iterator[dict[str, StrFloatIntNDArray]]:
        """
        Arguments:
            data: A dictionary storing data belonging to a data event.

        Returns:
            data: The same data provided to the function as an input
        """
        #yield from stream
        for data in stream: # FIXME: need to add 1 dimension at start so the serializer works
            yield {key:np.array([val]) for key,val in data.items()}

class BatchPipeline(ProcessingPipelineProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(self, parameters: Parameters) -> None:
        """
        Initializes a Batching pipeline

        This pipeline collects data into batches.

        Arguments:

             parameters: The configuration parameters
        """
        self.batch_size = parameters.batch_size

    def __call__(
        self, stream: Iterator[dict[str, StrFloatIntNDArray]]
    ) -> Iterator[dict[str, StrFloatIntNDArray]]:
        """
        Arguments:
            data: A dictionary storing data belonging to a data event.

        Returns:
            data: The same data provided to the function as an input
        """
        data_storage = DataStorage()

        for data in stream:
            data_storage.add_data(data=data)

            if len(data_storage) >= self.batch_size:
                yield data_storage.retrieve_stored_data()
                data_storage.reset_data_storage()

        if len(data_storage) > 0:
            yield data_storage.retrieve_stored_data()
