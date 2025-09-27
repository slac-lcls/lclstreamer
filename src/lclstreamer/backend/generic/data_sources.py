import sys
from typing import Any

import numpy
from numpy.typing import NDArray

from ...models.parameters import DataSourceParameters
from ...protocols.backend import DataSourceProtocol
from ...utils.logging_utils import log


class GenericRandomNumpyArray(DataSourceProtocol):
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
        Initializes a Generic Random Numpy Array data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        del additional_info
        extra_parameters: dict[str, Any] | None = parameters.__pydantic_extra__
        if extra_parameters is None:
            log.error(f"Entries needed by the {name} data source are not defined")
            sys.exit(1)
        if "array_shape" not in extra_parameters:
            log.error(f"Entry 'array_shape' is not defined for data source {name}")
            sys.exit(1)
        if "array_dtype" not in extra_parameters:
            log.error(f"Entry 'array_dtype' is not defined for data source {name}")
            sys.exit(1)

        try:
            self._array_shape: tuple[int, ...] = tuple(
                int(x) for x in extra_parameters["array_shape"].split(",")
            )
        except ValueError:
            log.error(f"Parameter 'array_dtype' for data source {name} is malformed")
            sys.exit(1)
        try:
            self._array_dtype: numpy.dtype[numpy.int_ | numpy.float64] = numpy.dtype(
                extra_parameters["array_dtype"]
            )
        except TypeError:
            log.error(
                f"Dtype {extra_parameters['array_dtype']} is not available in numpy"
            )
            sys.exit(1)

    def get_data(self, event: Any) -> NDArray[numpy.float64 | numpy.int_]:
        """
        Retrieves an array of int of float random numbers

        Arguments:

            event: A psana1 event

        Returns:

            random: an array of the type and size requested by the user, containing
            random data (either of integer or floating type)
        """
        del event
        if numpy.issubdtype(self._array_dtype, numpy.integer):
            return numpy.random.randint(low=0, high=255, size=self._array_shape).astype(
                self._array_dtype
            )
        elif numpy.issubdtype(self._array_dtype, numpy.floating):
            return numpy.random.random(self._array_shape).astype(self._array_dtype)
        else:
            log.error(
                "Only random arrays of integer of floating types are currently "
                "supported"
            )
            sys.exit(1)


class GenericRandomTimestamp(DataSourceProtocol):
    """
    A data source that generates random timestamp values.
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
        additional_info: dict[str, Any],
    ):
        """
        Initializes a Generic Random Timestamp data source.

        Arguments:
            name: An identifier for the data source
            parameters: The configuration parameters
        """
        del name
        del parameters
        del additional_info

    def get_data(self, event: Any) -> NDArray[numpy.float64]:
        """
        Retrieves a random timestamp value

        Arguments:
            event: An event (ignored for random data)

        Returns:
            timestamp: a 1D numpy array containing a random timestamp
        """
        del event
        # Generate a random timestamp (Unix epoch time in seconds)
        random_timestamp = numpy.random.uniform(1600000000, 1700000000)  # ~2020-2023 range
        return numpy.array(random_timestamp, dtype=numpy.float64)


class GenericRandomWavelength(DataSourceProtocol):
    """
    A data source that generates random wavelength values.
    """

    def __init__(
        self,
        name: str,
        parameters: DataSourceParameters,
        additional_info: dict[str, Any],
    ):
        """
        Initializes a Generic Random Wavelength data source.

        Arguments:
            name: An identifier for the data source
            parameters: The configuration parameters
        """
        del name
        del parameters
        del additional_info

    def get_data(self, event: Any) -> NDArray[numpy.float64]:
        """
        Retrieves a random wavelength value

        Arguments:
            event: An event (ignored for random data)

        Returns:
            wavelength: a 1D numpy array containing a random wavelength value
        """
        del event
        # Generate a random wavelength in typical X-ray range (0.1 to 10 Angstroms)
        random_wavelength = numpy.random.uniform(0.1, 10.0)
        return numpy.array(random_wavelength, dtype=numpy.float64)


class SourceIdentifier(DataSourceProtocol):
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
        Initializes a Generic Random Numpy Array data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
        del name
        del parameters
        self._source_identifier: NDArray[numpy.str_] = numpy.array(
            additional_info["source_identifier"]
        )

    def get_data(self, event: Any) -> NDArray[numpy.str_]:
        """
        Retrieves an array of int of float random numbers

        Arguments:

            event: A psana1 event

        Returns:

            random: an array of the type and size requested by the user, containing
            random data (either of integer or floating type)
        """
        return self._source_identifier
