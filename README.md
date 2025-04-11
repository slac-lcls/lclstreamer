# LCLStreamer

This application reads LCLS in parallel as fast as possible. After some rapid
calibration and/or reduction, the data is serialized, accumulated and finally
passed to one or more handlers that transfer it to external applications.

LCLStreamer has several components:

- An event source (that generates the data)
- A processing pipeline (for data reduction, pre-processing, etc.)
- A serializer (that turns the data into a binary blob of bytes)
- One or more handlers (that writes the bytes to files, sends them out  through
  sockets, etc)

Several options are available for each of the components. The application looks at the
`lclstreamer` section of the configuration files to figure our which option should be
used for each component. For example:

```
lclstreamer:
  [...]
  event_source: Psana1EventSource
  processing_pipeline: NoOpProcessingPipeline
  data_serializer: Hdf5Serializer
  data_handlers:
    - BinaryFileWritingDataHandler
    - BinaryDataStreamingDataHandler
```

Each entry in this section of the configuration files identifies a python class that
implements the operations required by the specific component.

Configuration options for each component can be specified in the
``event source``, ``processing_pipeline``, ```data_serializer```, and
```data_handlers``` sections of the configuration file. One entry per each of the
classes selected in the ```lclstreamer`` section must be present in the relevant
portion of the configuration file. For example:

```
data_serializer:
    Hdf5Serializer:
        compression_level: 3
        compression: zfp
        fields:
            timestamp: /data/timestamp
            detector_data: /data/data
```

The entry must be present even if the class takes no configuration options. In that
case, the entry can be empty. The following syntax should be used for an empy entry:

```
processing_pipeline:
    NoOpProcessingPipeline: {}
```

### Deployment

LCLStreamer uses [pixi](https://pixi.sh/latest/) for deployment, due to the mixture of
conda and PyPI packages used in the environment.

In order to deploy LCLStreamer, install `pixi`, then run the following command from the
top level of the GitHub repository:

```
pixi install
```

LCLStreamer is currently designed to run exclusively using the MPI protocol. After
deployment, it can be launched using the `pixi run` command. For example:

```
pixi run mpirun -n 8 lclstreamer
```

LCLStreamer will look for a configuration file called `lclstreamer.yaml` in the current
working directory. Alternatively, the path to the configuration file can be passed to
the `lclstreamer` executable using the `--config` option:

```
pixi run mpirun -n 8 lclstreamer --config examples/lclstreamer.yaml
```
