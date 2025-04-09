from typing import Any, Callable, Optional

import numpy
from numpy.typing import NDArray
from psana import Detector, EventId  # type: ignore

from ..models.parameters import DataSourceParameters
from ..protocols.backend import DataSourceProtocol


class Psana1Timestamp(DataSourceProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
    ):
        """
        Intialized recovery of timestamp information from psana.

        No initialization needed, the function does nothing
        """
        del name
        del parameters

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves timestamp information for an event
        """
        psana_event_id: Any = event.get(
            EventId  # pyright: ignore[reportAttributeAccessIssue]
        )
        timestamp_epoch_format: Any = psana_event_id.time()
        return numpy.array(
            numpy.float64(
                str(timestamp_epoch_format[0]) + "." + str(timestamp_epoch_format[1])
            )
        )


class Psana1AreaDetector(DataSourceProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
    ):
        """"""
        extra_parameters: Optional[dict[str, Any]] = parameters.__pydantic_extra__

        if extra_parameters is None:
            raise RuntimeError(
                f"Entries needed by the {name} data source are not defined"
            )
        if "psana_name" not in extra_parameters:
            raise RuntimeError(
                f"Entry 'psana_name' is not defined for data source {name}"
            )
        if "calibration" not in extra_parameters:
            raise RuntimeError(
                f"Entry 'calibration' is not defined for data source {name}"
            )

        detector_interface: Any = Detector(extra_parameters["psana_name"])

        if extra_parameters["calibration"]:
            self._data_retrieval_function: Callable[[Any], Any] = (
                detector_interface.calib
            )
        else:
            self._data_retrieval_function = detector_interface.raw

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves timestamp information for an event
        """

        return numpy.array(self._data_retrieval_function(event), dtype=numpy.float_)
