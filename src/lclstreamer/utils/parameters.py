import sys
from pathlib import Path
from typing import TextIO

from yaml import safe_load
from yaml.parser import ParserError

from ..models.parameters import Parameters
from ..utils.logging import log_error_and_exit
from ..utils.typing import StrFloatIntNDArray


def load_configuration_parameters(
    filename: Path,
) -> Parameters:
    """
    Loads and validates configuration parameters

    Arguments:

        filename: Path to a file storing the configuration parameters

    Returns:

        parameters: The configuration parameters
    """
    if not filename.exists():
        log_error_and_exit(
            f"Cannot read the configuration file {filename}: The file does not exist"
        )
    try:
        open_file: TextIO
        with open(filename, "r") as open_file:
            yaml_parameters: dict[str, StrFloatIntNDArray] = safe_load(open_file)
    except OSError:
        log_error_and_exit(
            f"Cannot read the configuration file {filename}: Cannot open the file"
        )
    except ParserError:
        log_error_and_exit(
            f"Cannot read the configuration file {filename}: Cannot pare the file"
        )
        sys.exit(1)

    parameters: Parameters = Parameters.model_validate(yaml_parameters)

    return parameters
