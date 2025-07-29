import sys
from dataclasses import dataclass, field

import numpy
from numpy.typing import DTypeLike

from ...protocols.backend import StrFloatIntNDArray
from ...utils.logging_utils import log


@dataclass
class DataContainer:
    """
    Dataclass used to store accumulated numpy arrays
    """

    data: list[StrFloatIntNDArray] = field(default_factory=list)
    dtype: DTypeLike | None = None
    shape: tuple[int, ...] | None = None


class DataStorage:
    """
    See documentation of the `__init__` function.
    """

    def __init__(self) -> None:
        """
        Initializes a Data Storage object

        Data Storage objects are containers that can store numpy arrays and allow
        bulk retrieval of the stored data.
        """

        self._data_containers: dict[str, DataContainer] = {}

    def add_data(self, data: dict[str, StrFloatIntNDArray | None]) -> None:
        """
        Adds data to the Data Storage object

        The function takes a dictionary storing numpy arrays, each identified
        by a dictionary key label. When called for the first time, it uses
        the incoming data to determine labels and dtypes of the numpy arrays to
        accumulate. All subsequent calls of the function will only accept data arrays
        with the same labels and dtypes as the initial call, or data whose value is
        None. If the data value is None, this function will the fill the missing data
        with appropriate null values (numpy.NaN for float data, the number -999 for int
        data, and the string "None" for str data)

        Arguments:

            data: a dictionary storing numpy arrays.
        """
        if len(self._data_containers) == 0:
            data_source_name: str
            for data_source_name in data:
                data_value: StrFloatIntNDArray | None = data[data_source_name]
                if data_value is None:
                    log.error(
                        f"Data entry {data_source_name} was none in the first "
                        "event. Impossible to determine data size"
                    )
                    sys.exit(1)
                else:
                    data_container = DataContainer(
                        data=[data_value],
                        dtype=data_value.dtype,
                        shape=data_value.shape,
                    )
                    self._data_containers[data_source_name] = data_container
        else:
            if sorted(data.keys()) != sorted(self._data_containers.keys()):
                log.error(
                    "The data labels in the current event do not match the labels "
                    "used to initialize the Data Storage container"
                )
                sys.exit(1)
            for data_source_name in data:
                data_value = data[data_source_name]
                data_container = self._data_containers[data_source_name]
                if data_value is None:
                    if data_container.shape is not None:
                        if data_container.dtype == numpy.int_:
                            data_container.data.append(
                                numpy.full(data_container.shape, "-999")
                            )
                            continue
                        elif data_container.dtype == numpy.float_:
                            data_container.data.append(
                                numpy.full(data_container.shape, numpy.NaN)
                            )
                            continue
                        else:
                            data_container.data.append(
                                numpy.full(data_container.shape, "None")
                            )
                            continue
                else:
                    if data_value.dtype != data_container.dtype:
                        log.error(
                            f"The dtype of the data entry {data_source_name} in the "
                            "current event does not match the dtype of the data "
                            "with which this label was originally initialized"
                        )
                        sys.exit(1)
                    if data_value.shape != data_container.shape:
                        log.error(
                            f"The shape of the data entry {data_source_name} in the "
                            "current event does not match the shape of the data "
                            "with which this label was originally initialized"
                        )
                        sys.exit(1)
                    data_container.data.append(data_value)

    def retrieve_stored_data(self) -> dict[str, StrFloatIntNDArray]:
        """
        Retuns the data stored in the Data Storage container object

        The data is returned as dictionary of numpy arrays. The keys of the
        dictionary match the labels of the stored data. The array associated
        with each label stores the accumulated data, with the fist axis
        representing each subsequent data addition, and the rest of the axes
        representing the data.

        Returns:

            stored_data: A dictionary containing the data accumulated by the
                Data Storage container
        """
        stored_data: dict[str, StrFloatIntNDArray] = {}

        data_source_name: str
        for data_source_name in self._data_containers:
            stored_data[data_source_name] = numpy.stack(
                self._data_containers[data_source_name].data,
            )

        return stored_data

    def reset_data_storage(self) -> None:
        "Resets the Data Storage container"

        data_source_name: str
        for data_source_name in self._data_containers:
            self._data_containers[data_source_name].data = []
