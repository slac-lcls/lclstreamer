from typer.testing import CliRunner

from lclstreamer.cmd.lclstreamer import app

runner = CliRunner()

template = """
lclstreamer:
    source_identifier: "none"
    event_source: GenericEventSource
    processing_pipeline: BatchProcessingPipeline
    data_serializer: Hdf5Serializer
    skip_incomplete_events: false
    data_handlers:
        - BinaryFileWritingDataHandler

data_sources:
    random:
        type: GenericRandomNumpyArray
        array_shape: 20,2
        array_dtype: float32

event_source:
    GenericEventSource:
        events: 1000

processing_pipeline:
    BatchProcessingPipeline:
        batch_size: 10

data_serializer:
    Hdf5Serializer:
        compression_level: 3
        compression: zfp
        fields:
            random: /data/random

data_handlers:
    BinaryFileWritingDataHandler:
        file_prefix: ""
        file_suffix: h5
        write_directory: {tmpdir}/output
"""

def test_app(tmpdir):
    cfg = tmpdir/"lclstreamer.yaml"
    cfg.write_text(
        template.format(tmpdir=str(tmpdir)),
        "utf-8"
    )

    result = runner.invoke(app, ["-c", str(cfg)])

    assert result.exit_code == 0
    print(result.stdout)
    print("---")
    print(result.output)
