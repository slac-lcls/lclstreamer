from typing import Any

import numpy
from numpy.typing import NDArray

from ...models.parameters import DataSourceParameters
from ...utils.logging import log_error_and_exit
from ...utils.protocols import DataSourceProtocol


class Psana2Timestamp(DataSourceProtocol):
    """
    See documentation of the `__init__` function
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
        additional_info: dict[str, Any],
    ):
        """
        Initializes a psana2 Timestamp Data Source

        Arguments:

            name: An identifier for the data source

            parameters: The data source configuration parameters
        """
        pass

    def get_data(self, event: Any) -> NDArray[numpy.float64]:
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
    See documentation of the `__init__` function
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
        additional_info: dict[str, Any],
    ):
        """
        Initializes a psana2 Detector values data source

        Arguments:

            name: An identifier for the data source

            parameters: The data source configuration parameters
        """

        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__
        self._call_get_data: list[tuple[str, Any, Any]] = []

        if extra_parameters is None:
            log_error_and_exit(
                f"Entries needed by the {name} data source are not defined"
            )
            return  # For the type checker

        if "psana_name" not in extra_parameters:
            log_error_and_exit(
                f"Entry 'psana_name' is not defined for data source {name}"
            )
        detector_name = extra_parameters["psana_name"]
        detector_interface: Any = additional_info["run"].Detector(
            detector_name
        )

        if "psana_fields" not in extra_parameters:
            if ":" in detector_name:
                # it is a PV
                self._call_get_data.append((detector_name, detector_interface, self._get_callable_with_event))
            else:
                log_error_and_exit(
                    f"Entry 'psana_fields' is not defined for data source {name}"
                )
        else:
            fields: list[str] | str = extra_parameters["psana_fields"]
            det_fields: list[str] = ([fields] if isinstance(fields, str) else fields)
            det_fields = [f.split(".") for f in det_fields]

            for psana_fields in det_fields:
                data_caller: Any = None
                base = detector_interface
                psana_field: str = ".".join([detector_name, *psana_fields])

                for field in psana_fields:
                    # Find the full name of the function we will call
                    if hasattr(base, field):
                        base = getattr(base, field)
                    else:
                        log_error_and_exit(f"Detector {base} has no parameter {field}")

                if callable(base):
                    # Check if bound method or not plus the number of args
                    arg_number = base.__code__.co_argcount - (1 if hasattr(base, "__self__") else 0)
                    if arg_number > 0:
                        data_caller = self._get_callable_with_event
                    else:
                        data_caller = self._get_callable_with_noevent
                else:
                    data_caller = self._get_noncallable
                self._call_get_data.append((psana_field, base, data_caller))

        self.dtype: type
        if "dtype" not in extra_parameters:
            self.dtype = numpy.float64
        else:
            self.dtype = extra_parameters["dtype"]

    def _get_callable_with_event(self, name, base, event):
        return (name, numpy.array(base(event), dtype=self.dtype))

    def _get_callable_with_noevent(self, name, base, event):
        return (name, numpy.array(base(), dtype=self.dtype))

    def _get_noncallable(self, name, base, event):
        return (name, numpy.array(base, dtype=self.dtype))

    def get_data(self, event: Any) -> NDArray[Any]:
        """
        Retrieves Detector values from a psana2 event

        Arguments:

            event: A psana2 event

         Returns:

            value: The retrieved data in the format of a numpy array
        """
        data_dict: dict[str, Any] = {}

        for name, base, data_caller in self._call_get_data:
            name, data = data_caller(name, base, event)
            if isinstance(data, dict):
                log_error_and_exit(
                    f"Data for the psana2 data source {self._name} has "
                    "the format of a dictionary! HSD detectors are not supported yet."
                )
            data_dict[name] = data

        return data_dict


class Psana2RunInfo(DataSourceProtocol):
    """
    See documentation of the `__init__` function
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
        additional_info: dict[str, Any],
    ):
        """
        Initializes a Psana2 Run Info Data Source

        Arguments:

            name: An identifier for the data source

            parameters: The data source configuration parameters
        """
        run: Any = additional_info["run"]
        self._run_data: dict[str, NDArray[numpy.str_]] = {  # pyright: ignore[reportUnknownMemberType]
            "experiment": numpy.array(run.expt, dtype=numpy.str_),  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            "run_timestamp": numpy.array(str(run.timestamp), dtype=numpy.str_),  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownArgumentType]
            "run_number": numpy.array(str(run.runnum), dtype=numpy.str_),  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownArgumentType]
            "source_identifier": numpy.array(additional_info["source_identifier"], dtype=numpy.str_),
        }

    def get_data(self, event: Any) -> dict[str, NDArray[numpy.str_]]:
        """
        Retrieves the detector info from a psana2 event

        Arguments:

            event: A psana2 event

         Returns:

            value: The retrieved data in the format of a numpy array
        """

        return self._run_data
