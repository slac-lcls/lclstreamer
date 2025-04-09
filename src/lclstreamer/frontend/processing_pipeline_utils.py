from dataclasses import dataclass, field
from typing import Optional

import numpy
from numpy.typing import DTypeLike

from ..protocols.backend import StrFloatIntNDArray


@dataclass
class DataContainer:
    data: list[StrFloatIntNDArray] = field(default_factory=list)
    dtype: Optional[DTypeLike] = None
    shape: Optional[tuple[int, ...]] = None


class DataStorage:

    def __init__(self) -> None:

        self._data_containers: dict[str, DataContainer] = {}

    def add_data(self, data: dict[str, StrFloatIntNDArray]) -> None:

        if len(self._data_containers) == 0:
            data_source_name: str
            for data_source_name in data:
                data_container = DataContainer(
                    data=[data[data_source_name]],
                    dtype=data[data_source_name].dtype,
                    shape=data[data_source_name].shape,
                )
                self._data_containers[data_source_name] = data_container
        else:
            if len(data) != len(self._data_containers):
                raise RuntimeError(
                    "The number of data entries in the current event does not match "
                    "the number of data entries originally fed to the data container"
                )
            for data_source_name in data:
                data_container = self._data_containers[data_source_name]
                if data[data_source_name].dtype != data_container.dtype:
                    raise RuntimeError(
                        f"The type of data entry {data_source_name} in the current "
                        "event does not match the type with which the data entry with "
                        "that name was originally fed to the data container"
                    )
                if data[data_source_name].shape != data_container.shape:
                    raise RuntimeError(
                        f"The shape of data entry {data_source_name} in the current "
                        "event does not match the shape with which the data entry with "
                        "that name was originally fed to the data container"
                    )
                data_container.data.append(data[data_source_name])

    def retrieve_stored_data(self) -> dict[str, StrFloatIntNDArray]:

        stored_data: dict[str, StrFloatIntNDArray] = {}

        data_source_name: str
        for data_source_name in self._data_containers:
            stored_data[data_source_name] = numpy.stack(
                self._data_containers[data_source_name].data,
                dtype=self._data_containers[data_source_name].dtype,
            )

        return stored_data

    def reset_data_storage(self) -> None:

        self._data_containers = {}
