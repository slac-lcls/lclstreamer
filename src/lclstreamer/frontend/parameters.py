import sys
from pathlib import Path
from typing import TextIO

from yaml import safe_load  # type:ignore
from yaml.parser import ParserError  # type:ignore

from ..models.parameters import Parameters
from ..protocols.backend import StrFloatIntNDArray
from ..utils.logging_utils import log

import os.path


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
    print(f"DEBUG: {filename}")
    print(f"DEBUG: {os.path.exists(filename)}")
    if not filename.exists():
        log.error(
            f"Cannot read the configuration file {filename}: The file does not exist"
        )
        sys.exit(1)
    try:
        open_file: TextIO
        with open(filename, "r") as open_file:
            yaml_parameters: dict[str, StrFloatIntNDArray] = safe_load(open_file)
    except OSError:
        log.error(
            f"Cannot read the configuration file {filename}: Cannot open the file"
        )
        sys.exit(1)
    except ParserError:
        log.error(
            f"Cannot read the configuration file {filename}: Cannot pare the file"
        )
        sys.exit(1)

    parameters: Parameters = Parameters.model_validate(yaml_parameters)

    return parameters
