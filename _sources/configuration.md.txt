# Configuration



## Configuring the LCLStreamer Application

The behavior of the LCLStreamer application is fully determined by the content of its
configuration file. This file determines which implementation of the different
workflow components should be used, how each component is configured, and which data
elements should be retrieved and processed by the application. Additionally, it
specifies where the data should come from.

LCLStreamer reads each section of the configuration file to determine which
implementation of each component it should use. Each section identifies, via the `type`
entry, which specific instance of the component LCLStreamer should use (providing the name
of a Python class that implements the component). For example:

``` yaml
event_source:
    type: Psana1EventSource

processing_pipeline:
    type: BatchProcessingPipeline
    ...

data_serializer:
    type: HDF5BinarySerializer
    ...

data_handlers:

    - type: BinaryFileWritingDataHandler
      ...

    - type: BinaryDataStreamingDataHandler
      ...

data_sources:
    timestamp:
        type: Psana1Timestamp
    ...
```

With these configuration options, LCLStreamer reads psana1 data (`Psana1EventSource`),
batches the retrieved data (`BatchProcessingPipeline`), serializes the data as a binary
blob with the internal structure of an HDF5 file (`HDF5BinarySerializer`), and finally
hands the binary blob to two data handlers: one that saves it as a file
(`BinaryFileWritingDataHandler`) and one that streams it through a network socket
(`BinaryDataStreamingDataHandler`).

In addition to the `type` entry, each section in the configuration file contains
entries for other parameters needed to configure the corresponding component (see below).

Some configuration parameters don't apply to a specific component, but to the entirety of
LCLStreamer; for example: the label that identifies the source of the data (a specific
experiment, file, or data-producing socket), or the strategy that LCLStreamer should apply
when encountering corrupted data events. These parameters can be provided at the top of the
configuration file, outside of the various component sections. For example:

``` yaml
source_identifier: exp=xpptut15:run=430
skip_incomplete_events: false

event_source:
    type: Psana1EventSource

processing_pipeline:
    type: BatchProcessingPipeline
    ...

data_serializer:
    type: HDF5BinarySerializer
```


## Configuring LCLStreamer's components

In addition to the `type` entry, which defines the nature of the component, other
entries in each section can be used to provide parameters for each of the Python
classes that implement the LCLStreamer components. For example:

``` yaml
data_serializer:
    type: HDF5BinarySerializer
    compression_level: 3
    compression: fzp
    fields:
        timestamp: /data/timestamp
        detector_data: /data/data
        random: /data/random
        photon_wavelength: /data/wavelength
```

In this section, the provided parameters specify that the Data Serializer component is
implemented by the `HDF5BinarySerializer` Python class. The serializer compresses the
data using the zfp algorithm, with a compression level of 3. The `fields` entry
describes the internal HDF5 path where each data item should be saved.


## Configuring the data sources

The `data_sources` section of the configuration file defines the data that LCLStreamer
extracts from every data event it processes. If a piece of information is part of a
data event but is not included in the `data_sources` section, LCLStreamer ignores it.

The `data_sources` section of the configuration file consists of a dictionary of data
sources. Each entry has a key, which acts as a name that identifies the extracted data
throughout the whole LCLStreamer data workflow, and a value, which is itself a
dictionary. This inner dictionary defines the nature of the data source (via the
usual mandatory `type` entry) and any other parameters needed to configure it. As above,
the `type` of a data source is the name of the Python class that implements it.
For example:

``` yaml
data_sources:
    timestamp:
        type: Psana1Timestamp

    detector_data:
        type: Psana1DetectorInterface
        psana_name: Jungfrau1M
        psana_fields: calib
```

This snippet of the configuration file defines two data sources, one called
`timestamp` and one called `detector_data`. The `timestamp` data source is of type
`Psana1Timestamp`. This means that a Python class of the same name determines how this
type of data is extracted from a data event. The `detector_data` source is instead of
type `Psana1DetectorInterface`. The configuration parameter `psana_name` is passed to
the Python class `Psana1DetectorInterface` that defines how this type of data is
retrieved.


# Configuration Options

```{toctree}
:maxdepth: 2
:caption: Available Components

configuration_event_sources.md
configuration_processing_pipelines.md
configuration_data_serializers.md
configuration_data_handlers.md
configuration_data_sources.md
```
