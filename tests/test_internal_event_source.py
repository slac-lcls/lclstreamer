from pathlib import Path

from click.testing import Result
from typer.testing import CliRunner

from lclstreamer.cmd.lclstreamer import app

runner: CliRunner = CliRunner()

configuration: str = """
lclstreamer:
    source_identifier: ""
    event_source: InternalEventSource
    processing_pipeline: BatchProcessingPipeline
    data_serializer: Hdf5BinarySerializer
    skip_incomplete_events: false
    data_handlers:
        - BinaryFileWritingDataHandler

data_sources:
    random:
        type: GenericRandomNumpyArray
        array_shape: 20,2
        array_dtype: float32

event_source:
    InternalEventSource:
        number_of_events_to_generate: 1000

processing_pipeline:
    BatchProcessingPipeline:
        batch_size: 10

data_serializer:
    Hdf5BinarySerializer:
        compression_level: 3
        compression: zfp
        fields:
            random: /data/random

data_handlers:
    BinaryFileWritingDataHandler:
        file_prefix: ""
        file_suffix: h5
        write_directory: output
"""


def test_app() -> None:
    with runner.isolated_filesystem():
        current_directory: Path = Path.cwd()
        Path(current_directory / "output").mkdir()
        configuration_file_name: Path = current_directory / "lclstreamer.yaml"
        configuration_file_name.write_text(configuration, "utf-8")
        result: Result = runner.invoke(app, ["--config", str(configuration_file_name)])
        print("--- Output")
        print(result.output)
        if result.exception is not None:
            print("--- Exceptions")
            print(result.exception)
            print(result.exc_info)

        assert result.exit_code == 0
