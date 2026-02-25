from collections.abc import Iterator
from time import time
from typing import Any, cast

import numpy
from bitshuffle import (  # pyright: ignore[reportMissingTypeStubs]
    compress_lz4,  # pyright: ignore[reportUnknownVariableType]
)
from cbor import (  # pyright: ignore[reportMissingTypeStubs]
    dumps,  # pyright: ignore[reportUnknownVariableType]
)
from mpi4py import MPI
from numpy.typing import NDArray

from ...models.parameters import (
    SimplonBinarySerializerParameters,
)
from ...utils.logging import log_error_and_exit, log_info
from ...utils.protocols import DataSerializerProtocol
from ...utils.typing import StrFloatIntNDArray


class SimplonBinarySerializer(DataSerializerProtocol):
    def __init__(self, parameters: SimplonBinarySerializerParameters) -> None:
        """
        Initializes a Simplon data serializer

        This serializers turns a dictionary of numpy arrays into a binary with an
        internal structure of a Simplon message. This serializer follows the 1.8
        version of the Simplon specification (published by Dectris)

        Arguments:

            parameters: The configuration parameters
        """
        if parameters.type != "SimplonBinarySerializer":
            log_error_and_exit(
                "Data serializer parameters do not match the expected type"
            )
        self._data_source_to_serialize: str = parameters.data_source_to_serialize
        self._polarization: dict[str, Any] = {
            "polarization_fraction": parameters.polarization_fraction,
            "polarization_axis": parameters.polarization_axis,
        }
        self._data_rate: str = parameters.data_collection_rate
        self._detector_name: str = parameters.detector_name
        self._detector_type: str = parameters.detector_type
        self._node_rank: int = MPI.COMM_WORLD.Get_rank()
        self._node_pool_size: int = MPI.COMM_WORLD.Get_size()
        self._rank_message_count: int = 1

    def __call__(
        self, stream: Iterator[dict[str, StrFloatIntNDArray | None]]
    ) -> Iterator[bytes]:
        """
        Serializes data to a binary blob with an internal Simplon message structure

        Arguments:

            source: A stream of Event information (dictionary storing numpy arrays)

        Yields:

            byte_block: A binary blob (a bytes object)
        """

        must_send_first_message: bool = False
        if self._node_rank == self._node_pool_size - 1:
            must_send_first_message = True
        run_number: int = 0

        data: dict[str, StrFloatIntNDArray | None]
        for data in stream:
            try:
                if (data_block := data[self._data_source_to_serialize]) is not None:
                    array: StrFloatIntNDArray = data_block[-1]
                else:
                    continue
            except KeyError:
                log_error_and_exit(
                    f"The {self._data_source_to_serialize} data source, that the "
                    "SimplonBinarySerializer is supposed to serialize, cannot be found in"
                    "the data"
                )

            if not (
                numpy.issubdtype(array.dtype, numpy.int_)
                or numpy.issubdtype(array.dtype, numpy.float64)
            ):
                log_error_and_exit(
                    f"The {self._data_source_to_serialize} data source is not of type int "
                    "or float, as required by the SimplonBinarySerializer"
                )

            experiment_data: NDArray[numpy.str_] = cast(
                NDArray[numpy.str_], data["run_info"]
            )[-1]
            run_number = experiment_data[2]

            if self._node_rank == self._node_pool_size - 1:
                if must_send_first_message:
                    detector_geometry: NDArray[numpy.str_] = cast(
                        NDArray[numpy.str_], data["detector_geometry"]
                    )[-1]

                    yield b"".join(
                        (
                            b"c",
                            cast(
                                bytes,
                                dumps(
                                    {
                                        "type": "start",
                                        "run_number": run_number,
                                        "start_time": experiment_data[1],
                                        "duration": "N/A",
                                        "beamline": experiment_data[3][4:7].upper(),
                                        "experiment": experiment_data[0],
                                        "beam_type": "X-ray",
                                        "polarization": {
                                            "fraction": self._polarization.get(
                                                "polarization_fraction", 0
                                            ),
                                            "axis": self._polarization.get(
                                                "polarization_axis", [0.0, 0.0, 0.0]
                                            ),
                                        },
                                        "data_collection_rate": self._data_rate,
                                        "datatype": str(array.dtype),
                                        "shape": "x".join(map(str, array.shape)),
                                        "algorithm": "bitshuffle-lz4",
                                        "detector": {
                                            "name": self._detector_name,
                                            "id": detector_geometry[0],
                                            "type": self._detector_type,
                                            "geometry": detector_geometry[1],
                                            "pixel_coords": numpy.array(
                                                detector_geometry[2]
                                            ).tobytes()
                                            if len(detector_geometry) > 2
                                            else "",
                                            "material": "???",
                                            "thickness": "???",
                                        },
                                        "message_id": self._node_rank * 10000
                                        + self._rank_message_count,
                                        "timestamp": time(),
                                    }
                                ),
                            ),
                        ),
                    )

            must_send_first_message = False

            array_sum: float | int = array.sum()

            compressed_data: NDArray[numpy.uint8] = cast(
                NDArray[numpy.uint8], compress_lz4(array, block_size=2**12)
            )

            beam_data_dict: dict[str, Any] = {}
            try:
                beam_data: NDArray[numpy.floating[Any]] = cast(
                    NDArray[numpy.floating[Any]], data["beam_data"]
                )[-1]
                beam_data_dict = {
                    "beam_direction": {
                        "angle_x": beam_data[0],
                        "angle_y": beam_data[1],
                        "position_x": beam_data[2],
                        "position_y": beam_data[3],
                    },
                    "photon_energy": beam_data[4],
                    "photon_wavelength": 0,  # data["photon_wavelength"][-1]
                }
            except KeyError as e:
                log_info(f"Field: {e.args[0]} not found in data_sources. Skipping.")

            message: dict[str, Any] = {
                "type": "image",
                "run": run_number,
                "compressed_data": compressed_data.tobytes(),
                **beam_data_dict,
                "dtype": str(array.dtype),
                "sum": array_sum,
                "message_id": self._node_rank * 10000 + self._rank_message_count,
                "timestamp": cast(NDArray[numpy.str_], data["timestamp"])[-1],
            }
            yield b"".join((b"m", cast(bytes, dumps(message))))

        if self._node_rank == self._node_pool_size - 1:
            yield b"".join(
                (
                    b"c",
                    cast(
                        bytes,
                        dumps(
                            {
                                "type": "stop",
                                "run": run_number,
                                "timestamp": time(),
                            }
                        ),
                    ),
                ),
            )
