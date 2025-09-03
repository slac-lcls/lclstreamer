import sys
from typing import Any, Callable

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
        additional_info: dict[str, Any],
    ):
        """
        Initializes a psana1 Timestamp data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        del name
        del parameters
        del additional_info

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves timestamp information from a psana1 event

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
        additional_info: dict[str, Any],
    ):
        """
        Initializes a psana1 area detector data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        del additional_info
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__

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
        Retrieves a detector frame from a psana1 event

        Arguments:

            event: A psana1 event

         Returns:

            timestamp: A 2d numpy array storing the detector frame as a grayscale
            image
        """
        return numpy.array(self._data_retrieval_function(event), dtype=numpy.float_)


class Psana1AssembledAreaDetector(DataSourceProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
        additional_info: dict[str, Any],
    ):
        """
        Initializes a psana1 assembled area detector data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        del additional_info
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)

        detector_interface: Any = Detector(extra_parameters["psana_name"])

        self._data_retrieval_function = detector_interface.image

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves an assembled detector frame from a psana1 event

        Arguments:

            event: A psana1 event

         Returns:

            timestamp: A 2d numpy array storing the assembeld detector frame as a
            grayscale image
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
        additional_info: dict[str, Any],
    ):
        """
        Initializes a psana1 PV data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        del additional_info
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)
        if "psana_function" in extra_parameters:
            if extra_parameters["psana_function"] not in ("sum", "channels"):
                log.error(
                    "Currently only 'sum' and 'channels' psana_functions are "
                    "supported (data source {name})"
                )
                sys.exit(1)

        self._detector_interface: Any = Detector(extra_parameters["psana_name"])

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves a PV value from a psana1 event

        Arguments:

            event: A psana1 event

         Returns:

            value: The value of the retrieved data in the format of a numpy float
            array
        """
        return numpy.array(self._detector_interface(event), dtype=numpy.float_)


class Psana1BbmonDetectorTotalIntensity(DataSourceProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
        additional_info: dict[str, Any],
    ):
        """
        Initializes a psana1 BbmonDetector data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        del additional_info
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)

        self._detector_interface: Any = Detector(extra_parameters["psana_name"])

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
        additional_info: dict[str, Any],
    ):
        """
        Initializes a psana1 IpmDetector data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        del additional_info
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)
        if "psana_function" not in extra_parameters:
            log.error(f"Entry 'psana_function' is not defined for data source {name}")
            sys.exit(1)
        if extra_parameters["psana_function"] not in ("channel"):
            log.error(
                "Currently only the 'channel' psana_functions is supported "
                "(data source {name})"
            )
            sys.exit(1)

        detector_interface: Any = Detector(extra_parameters["psana_name"])
        self._data_retrieval_function: Callable[[Any], Any] = detector_interface.channel

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves IpmDetector data from a psana1 event

        Arguments:

            event: A psana1 event

         Returns:

            value: The value of the retrieved data in the format of a numpy float
            array
        """
        return numpy.array(self._data_retrieval_function(event), dtype=numpy.float_)


class Psana1EvrCodes(DataSourceProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        *,
        name: str,
        parameters: DataSourceParameters,
        additional_info: dict[str, Any],
    ):
        """
        Intializes a psana1 EVR data source

        Arguments:
            name: An identifier for the data source

            parameters: The configuration parameters
        """
        del additional_info
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__
        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)

        self._detector_interface: Any = Detector(extra_parameters["psana_name"])

    def get_data(self, event: Any) -> NDArray[numpy.int_]:
        """
        Retrieves IpmDetector data from an event

        Arguments:

            event: A psana1 event

        Returns:

            value: A numpy array storing all the EVR codes associated with and
            event (max 256 event codes)
        """
        evr_codes: Any = self._detector_interface.eventCodes(event)
        if evr_codes is None:
            return numpy.ndarray([0] * 256, dtype=numpy.int_)

        current_evr_codes: NDArray[numpy.int_] = numpy.array(
            evr_codes, dtype=numpy.int_
        )

        return numpy.pad(
            current_evr_codes,
            pad_width=(0, 256 - len(current_evr_codes)),
            mode="constant",
            constant_values=(0, 0),
        )


class Psana1UsdUsbDetector(DataSourceProtocol):
    """
    See documentation of the `__init__` function.
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
        additional_info: dict[str, Any],
    ):
        """
        Initializes a psana1 UsdUsbDetector data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        del additional_info
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)
        if "psana_function" not in extra_parameters:
            log.error(f"Entry 'psana_function' is not defined for data source {name}")
            sys.exit(1)
        if extra_parameters["psana_function"] not in ("values"):
            log.error(
                "Currently only the 'channel' psana_functions is supported "
                "(data source {name})"
            )
            sys.exit(1)
        detector_interface: Any = Detector(extra_parameters["psana_name"])
        self._data_retrieval_function: Callable[[Any], Any] = detector_interface.values

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves UsdUsbDetector data from a psana1 event

        Arguments:

            event: A psana1 event

         Returns:

            value: The value of the retrieved data in the format of a numpy float
            array
        """
        return numpy.array(self._data_retrieval_function(event), dtype=numpy.float_)
