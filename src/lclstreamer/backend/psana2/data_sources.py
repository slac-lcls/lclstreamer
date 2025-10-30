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


class Psana2DetectorInterface(DataSourceProtocol):
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

        self._name: str = name
        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "psana_name" not in extra_parameters:
            log.error(f"Entry 'psana_name' is not defined for data source {name}")
            sys.exit(1)
        if "psana_fields" not in extra_parameters:
            if ":" in extra_parameters["psana_name"]:
                self._is_pv: bool = True
            else:
                log.error(f"Entry 'psana_fields' is not defined for data source {name}")
                sys.exit(1)
        else:
            fields: list[str] | str = extra_parameters["psana_fields"]
            self._det_params: list[str] = [fields] if isinstance(fields, str) else fields

        self._detector_interface: Any = additional_info["run"].Detector(
            extra_parameters["psana_name"]
        )


    def get_data(self, event: Any) -> NDArray[Any]:
        """
        Retrieves Detector values from a psana2 event

        Arguments:

            event: A psana2 event

         Returns:

            value: The retrieved data is a list of object, such as:
            [Object1, Object2, Object3, ...]
            in the format of a numpy array.
        """

        data: list[Any] = []

        base: Any
        if getattr(self, "_is_pv", False):
            base = self._detector_interface
            data.append(base(event))
        else:
            for param in self._det_params:
                base = self._detector_interface
                subfields: list[str] = param.split(".")
                for field in subfields:
                    if hasattr(base, field):
                        base = getattr(base, field)
                    else:
                        log.error(f"Detector {base} has no parameter {field}")
                        sys.exit(1)
                if callable(base):
                    try:
                        base = base(event)
                    except TypeError:
                        base = base()
                    data.append(base)
                else:
                    data.append(base)

        if len(data) == 1:
            data = data[0]
            if isinstance(data, dict):
                log.error(f"Data is in dict format: {self._name}!")
                exit(1)
            else:
                return numpy.array(data, dtype=numpy.float_)
        return numpy.array(data, dtype=object)


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

        run: dict[str, Any] = additional_info["run"]
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
