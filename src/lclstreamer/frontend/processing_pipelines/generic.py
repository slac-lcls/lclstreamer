from ...models.parameters import Parameters
from ...protocols.backend import StrFloatIntNDArray
from ...protocols.frontend import ProcessingPipelineProtocol
from .utils import DataStorage


class NoOpProcessingPipeline(ProcessingPipelineProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(self, parameters: Parameters) -> None:
        """
        Initializes a NoOp processing pipeline

        This pipeline performs no operations on the data: it simply collects
        it.

        Arguments:

             parameters: The configuration parameters
        """
        self._data_storage = DataStorage()

    def process_data(
        self, data: dict[str, StrFloatIntNDArray]
    ) -> dict[str, StrFloatIntNDArray]:
        """
        Processes a single data event and stores the results

        Since this is a NoOp processing pipeline, this function simply accumulates
        data from each event without performing any processing

        Arguments:

            data: A dictionary storing data for a single event

        Returns:

            data: The same data provided to the function as an input
        """

        self._data_storage.add_data(data=data)

        return data

    def collect_results(
        self, data: dict[str, StrFloatIntNDArray]
    ) -> dict[str, StrFloatIntNDArray]:
        """
        Retrieved the accumulated processing results

        Since this is a NoOp processing pipeline, this function simply
        returns the unprocessed data that was accumulated by the pipeline

        Arguments:

            data: A dictionary storing data for a single event. This is
                ignored

        Returns:

            data: A dictionary storing the accumulated data
        """
        results: dict[str, StrFloatIntNDArray] = (
            self._data_storage.retrieve_stored_data()
        )

        self._data_storage.reset_data_storage()

        return results
