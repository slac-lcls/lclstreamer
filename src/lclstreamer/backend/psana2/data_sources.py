import sys
from typing import Any, Callable

import numpy
from numpy.typing import NDArray

from ...models.parameters import DataSourceParameters
from ...protocols.backend import DataSourceProtocol
from ...utils.logging_utils import log

# Note: smalldata provides a "data producer"
# that shows interfaces to psana2 detectors here:
# https://github.com/slac-lcls/smalldata_tools/blob/master/lcls2_producers/smd_producer.py


class Psana2Timestamp(DataSourceProtocol):
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
        Initializes a psana2 Timestamp data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        pass

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves timestamp information from a psana2 event

        Arguments:

            event: A psana2 event

        Returns:

            timestamp: a 1D numpy array (of type float64) containing the timestamp
            information
        """
        return numpy.array(event.timestamp, dtype=numpy.float64)


class Psana2AreaDetector(DataSourceProtocol):
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
        Initializes a psana2 area detector data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
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

        detector_interface: Any = additional_info["run"].Detector(
            extra_parameters["psana_name"]
        )

        if extra_parameters["calibration"]:
            self._data_retrieval_function: Callable[[Any], Any] = (
                detector_interface.raw.calib
            )
        else:
            self._data_retrieval_function = detector_interface.raw.raw

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves a detector frame from a psana2 event

        Arguments:

            event: A psana2 event

         Returns:

            image: A 2d numpy array storing the detector frame as a grayscale
            image
        """
        return numpy.array(self._data_retrieval_function(event), dtype=numpy.float_)


class Psana2AssembledAreaDetector(DataSourceProtocol):
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
        Initializes a psana2 assembled area detector data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)

        detector_interface: Any = additional_info["run"].Detector(
            extra_parameters["psana_name"]
        )

        self._data_retrieval_function = detector_interface.raw.image

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves an assembled detector frame from a psana2 event

        Arguments:

            event: A psana2 event

         Returns:

            image: A 2d numpy array storing the assembeld detector frame as a
            grayscale image
        """
        return numpy.array(self._data_retrieval_function(event), dtype=numpy.float_)


class Psana2PV(DataSourceProtocol):
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
        Initializes a psana2 PV data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)

        self._detector_interface: Any = additional_info["run"].Detector(
            extra_parameters["psana_name"]
        )

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves a PV value from a psana2 event

        Arguments:

            event: A psana2 event

         Returns:

            value: The value of the retrieved data in the format of a numpy float
            array
        """
        return numpy.array(self._detector_interface(event), dtype=numpy.float_)


class Psana2EBeam(DataSourceProtocol):
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
        Initializes a psana2 EBeam data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_function" not in extra_parameters:
            log.error(f"Entry 'psana_function' is not defined for data source {name}")
            sys.exit(1)
        if extra_parameters["psana_function"] not in ("ebeamL3Energy"):
            log.error(
                "Currently only the 'ebeamL3Energy` psana function is "
                f"supported (data source {name})"
            )
            sys.exit(1)

        self._detector_interface: Any = additional_info["run"].Detector("ebeam")

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves EBeam data from a psana2 event

        Arguments:

            event: A psana2 event

         Returns:

            value: The value of the retrieved data in the format of a numpy float
            array
        """
        return numpy.array(
            self._detector_interface.raw.ebeamL3Energy(event)(event), dtype=numpy.float_
        )


class Psana2Gmd(DataSourceProtocol):
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
        Initializes a psana2 GMD data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
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
        if extra_parameters["psana_function"] not in ("milliJoulesPerPulse"):
            log.error(
                "Currently only the 'milliJoulesPerPulse` psana function is "
                f"supported (data source {name})"
            )
            sys.exit(1)

        self._detector_interface: Any = additional_info["run"].Detector(
            extra_parameters["psana_name"]
        )

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves GMD data from a psana2 event

        Arguments:

            event: A psana2 event

         Returns:

            value: The value of the retrieved data in the format of a numpy float
            array
        """
        return numpy.array(
            self._detector_interface.raw.milliJoulesPerPulse(event), dtype=numpy.float_
        )


class Psana2Camera(DataSourceProtocol):
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
        Initializes a psana2 camera data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)

        detector_interface: Any = additional_info["run"].Detector(
            extra_parameters["psana_name"]
        )

        self._data_retrieval_function = detector_interface.raw.raw

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves a camera frame from a psana2 event

        Arguments:

            event: A psana2 event

         Returns:

            image: A 2d numpy array storing the detector frame as a grayscale
            image
        """
        return numpy.array(self._data_retrieval_function(event), dtype=numpy.float_)


class Psana2HsdDetector(DataSourceProtocol):
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
        Initializes a psana2 HSD detector data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
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
        if extra_parameters["psana_function"] not in ("peaks", "waveforms"):
            log.error(
                "Currently only the 'peaks' and 'waverform` psana functions are "
                f"supported (data source {name})"
            )
            sys.exit(1)

        detector_interface: Any = additional_info["run"].Detector(
            extra_parameters["psana_name"]
        )

        if extra_parameters["psana_function"] == "peaks":
            self._data_retrieval_function: Callable[[Any], Any] = (
                detector_interface.raw.peaks
            )
        else:
            self._data_retrieval_function = detector_interface.raw.waveforms

    def get_data(self, event: Any) -> NDArray[numpy.float_]:
        """
        Retrieves Hsd data from a psana2 event

        Arguments:

            event: A psana2 event

         Returns:

            value: The value of the retrieved data in the format of a numpy float
            array
        """
        return numpy.array(self._data_retrieval_function(event), dtype=numpy.float_)


class Psana2DetectorValues(DataSourceProtocol):
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
        Initializes a psana2 Detector values data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)
        if "psana_fields" not in extra_parameters:
            log.error(f"Entry 'psana_fields' is not defined for data source {name}")
            sys.exit(1)
        self._detector_interface: Any = additional_info["run"].Detector(
            extra_parameters["psana_name"]
        )

        self._det_params = []
        for fields in extra_parameters["psana_fields"]:
            self._det_params.append(fields)

    def get_data(self, event: Any) -> NDArray[numpy.str_]:
        """
        Retrieves Detector values from a psana2 event

        Arguments:

            event: A psana2 event

         Returns:

            value: The retrieved data is a list, such as:
            [Value1, Value2, Value3, ...]
            in the format of a numpy string array.
        """

        data = []

        for param in self._det_params:
            subfields = param.split(".")
            base = self._detector_interface
            for field in subfields:
                if hasattr(base, field):
                    base = getattr(base, field)
                else:
                    log.error(f"Detector {base} has no parameter {field}")
                    sys.exit(1)
            data.append(str(base(event)) if callable(base) else str(base))

        return numpy.array(data, dtype=numpy.str_)


class Psana2RunInfo(DataSourceProtocol):
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
        Initializes a psana2 run info data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__

        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)

        run = additional_info["run"]
        self._data = [
            run.expt,
            str(run.timestamp),
            str(run.runnum),
            additional_info["source_identifier"],
        ]

    def get_data(self, event: Any) -> NDArray[numpy.str_]:
        """
        Retrieves the detector info from a psana2 event

        Arguments:

            event: A psana2 event

         Returns:

            value: A list of the experiment's name, run start's timestamp,
            run number and source identifier.
        """

        return numpy.array(self._data, dtype=numpy.str_)
