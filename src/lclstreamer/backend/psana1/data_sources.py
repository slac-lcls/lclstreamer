import sys
from typing import Any, Callable, Literal, Optional

import numpy
from numpy.typing import NDArray
from psana import Detector, EventId  # type: ignore

from ...models.parameters import DataSourceParameters
from ...protocols.backend import DataSourceProtocol
from ...utils.logging_utils import log


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
        Initializes a psana1 Timestamp data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        del name
        del parameters

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves timestamp information from an event

        Arguments:

            event: A psana1 event

        Returns:

            timestamp: a 1D numpy array (of type float64) containing the timestamp
            information
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
        """
        Initializes a psana1 area detector data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        extra_parameters: Optional[dict[str, Any]] = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)
        if "calibration" not in extra_parameters:
            log.error(f"Entry 'calibration' is not defined for data source {name}")
            sys.exit(1)

        detector_interface: Any = Detector(extra_parameters["psana_name"])

        if extra_parameters["calibration"]:
            self._data_retrieval_function: Callable[[Any], Any] = (
                detector_interface.calib
            )
        else:
            self._data_retrieval_function = detector_interface.raw

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves a detector frame from an event

        Arguments:

            event: A psana1 event

         Returns:

            timestamp: A 2d numpy array storing the detector frame as a grayscale
            image
        """
        return numpy.array(self._data_retrieval_function(event), dtype=numpy.float_)


class Psana1PV(DataSourceProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
    ):
        """
        Initializes a psana1 PV data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        extra_parameters: Optional[dict[str, Any]] = parameters.__pydantic_extra__
        psana_function: Optional[Literal["sum", "channels"]] = None

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)
        if "psana_function" in extra_parameters:
            if extra_parameters["psana_function"] not in ("sum", "channels"):
                log.error(
                    f"Currently only 'sum' and 'channels' psana_functions are "
                    "supported (data source {name})"
                )
                sys.exit(1)

        self._detector_interface: Any = Detector(extra_parameters["psana_name"])

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves a PV value from an event

        Arguments:

            event: A psana1 event

         Returns:

            value: The value of the retrieved data in the format of a numpy float
            array
        """
        return numpy.array(self._detector_interface(event), dtype=numpy.float_)


class Psana1BbmonDetector(DataSourceProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
    ):
        """
        Initializes a psana1 BbmonDetector data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        extra_parameters: Optional[dict[str, Any]] = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_function' is not defined for data source {name}")
            sys.exit(1)
        if extra_parameters["psana_function"] not in ("TotalIntensity"):
            log.error(
                f"Currently only the 'TotalIntensity' psana_functions is supported "
                "(data source {name})"
            )
            sys.exit(1)

        self._detector_interface: Any = Detector(extra_parameters["psana_name"])
        self._psana_function = extra_parameters["psana_function"]

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves BmmonDetector data from an event

        Arguments:

            event: A psana1 event

         Returns:

            value: The value of the retrieved data in the format of a numpy float
            array
        """
        return numpy.array(
            self._detector_interface.get(event).TotalIntensity(), dtype=numpy.float_
        )


class Psana1IpmDetector(DataSourceProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
    ):
        """
        Initializes a psana1 IpmDetector data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        extra_parameters: Optional[dict[str, Any]] = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_function' is not defined for data source {name}")
            sys.exit(1)
        if extra_parameters["psana_function"] not in ("channel"):
            log.error(
                f"Currently only the 'channel' psana_functions is supported "
                "(data source {name})"
            )
            sys.exit(1)

        self._detector_interface: Any = Detector(extra_parameters["psana_name"])
        self._psana_function = extra_parameters["psana_function"]

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves IpmDetector data from an event

        Arguments:

            event: A psana1 event

         Returns:

            value: The value of the retrieved data in the format of a numpy float
            array
        """
        return numpy.array(self._detector_interface.channel(event), dtype=numpy.float_)
