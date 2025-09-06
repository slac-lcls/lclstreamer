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
  data_serializer: Hdf5BinarySerializer
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
    Hdf5BinarySerializer:
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

### Distributed Streaming

LCLStreamer supports distributed streaming architectures where data processing is split across specialized computing resources:

- **Source nodes**: Run CPU-intensive psana applications with MPI parallelization for high-throughput data reading and preprocessing
- **Sink nodes**: Execute downstream processing tasks (e.g., machine learning inference) optimized for different hardware (GPUs, specialized accelerators)

This architecture enables real-time producer-consumer data processing pipelines, where psana applications stream processed data directly to downstream consumers without intermediate file I/O. The approach eliminates Python environment dependencies between source and sink nodes while providing GPU-friendly data delivery for accelerated computing workloads.

**Configuration**: Use `BinaryDataStreamingDataHandler` with `role: client` for MPI ranks to connect to external sink nodes. Update the sink node URL in your configuration file based on the node allocated by SLURM.

**Example setup**:
```bash
# 1. Start sink node first (server - auto-detects hostname, uses default port)
python examples/psana_pull_script.py

# 2. Update configuration file with actual sink node hostname and port
# Edit examples/lclstreamer-psana1-to-sdfada.yaml:
# BinaryDataStreamingDataHandler:
#   url: tcp://your-allocated-node:your-port-number

# 3. Start source node (multiple MPI ranks connecting to sink)
pixi run --environment psana1 mpirun -n 8 lclstreamer --config examples/lclstreamer-psana1-to-sdfada.yaml
```

**Note**: When using SLURM, update the sink node URL in your configuration file to match the hostname of the node allocated for your sink job. Both hostname and port can be customized using `--hostname` and `--port` options if needed.

The pull script (`examples/psana_pull_script.py`) auto-detects the hostname and provides comprehensive data inspection with configurable network endpoints for flexible deployment across heterogeneous computing environments.

### Deployment

LCLStreamer uses [pixi](https://pixi.sh/latest/) for deployment, due to the mixture of
conda and PyPI packages used in the environment.

In order to deploy LCLStreamer, install `pixi`, then run the following command from the
top level of the GitHub repository:

```
pixi install --environment psana1
```

or, to install within a psana2 environment,

```
pixi install --environment psana2
```

or, to install both side-by-side

```
pixi install --all
```

LCLStreamer is currently designed to run exclusively using the MPI protocol. After
deployment, it can be launched using the `pixi run` command. For example:

```
pixi run --environment psana1 mpirun -n 8 lclstreamer
```

LCLStreamer will look for a configuration file called `lclstreamer.yaml` in the current
working directory. Alternatively, the path to the configuration file can be passed to
the `lclstreamer` executable using the `--config` option:

```
pixi run --environment psana1 mpirun -n 8 lclstreamer --config examples/lclstreamer-psana1.yaml
```

For psana2:

```
pixi run --environment psana2 mpirun -n 8 lclstreamer --config examples/lclstreamer-psana2-tmo.yaml
```

### Development

During development, you'll want to run type checking and testing.
This can be accomplished within the test1 or test2 environments,

```
pixi run --environment test1 mypy src
```
