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
        run: Any,
    ):
        """
        Initializes a Generic Random Numpy Array data source.

        Arguments:

            name: An identifier for the data source

            parameters: The configuration parameters
        """
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
            self._array_dtype: numpy.dtype[numpy.int_ | numpy.float_] = numpy.dtype(
                extra_parameters["array_dtype"]
            )
        except TypeError:
            log.error(
                f"Dtype {extra_parameters['array_dtype']} is not available in numpy"
            )
            sys.exit(1)

    def get_data(self, event: Any) -> NDArray[numpy.float_ | numpy.int_]:
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
