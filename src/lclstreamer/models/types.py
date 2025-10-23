from typing import Dict
from typing_extensions import TypeAlias

import numpy
from numpy.typing import NDArray


StrFloatIntNDArray: TypeAlias = NDArray[numpy.str_ | numpy.float64 | numpy.int_]

LossyEvent = Dict[str, StrFloatIntNDArray | None]

Event = Dict[str, StrFloatIntNDArray]
