from pathlib import Path
from typing import TextIO

from yaml import safe_load  # type:ignore
from yaml.parser import ParserError  # type:ignore

from ..models.parameters import Parameters
from ..protocols.backend import StrFloatIntNDArray


def load_configuration_parameters(
    filename: Path,
) -> Parameters:
    """
    Loads configuration parameters

    Arguments:

        filename: Name of the file to read
    """
    if not filename.exists():
        raise RuntimeError(
            f"Cannot read the configuration file {filename}: The file does not exist"
        )
    try:
        open_file: TextIO
        with open(filename, "r") as open_file:
            yaml_parameters: dict[str, StrFloatIntNDArray] = safe_load(open_file)
    except OSError:
        raise RuntimeError(
            f"Cannot read the configuration file {filename}: Cannot open the file"
        )
        # pyright: ignore[reportAttributeAccessIssue]
    except ParserError:
        raise RuntimeError(
            f"Cannot read the configuration file {filename}: Cannot pare the file"
        )

    parameters: Parameters = Parameters.model_validate(yaml_parameters)

    return parameters
