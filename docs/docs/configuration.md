# Configuration

## Configuring LCLStreamer

The behavior of the LCLStreamer application is fully determined by the content of its
configuration file. This file determines which implementation of the different
workflow components should be used, how each component is configured, and which data
elements should be retrieved and processed by the application. Additonally, it
specifies where the data should come from.

LCLStreamer reads the `lclstreamer` section of the configuration files to determine
which implementation of each component it should use. Each component entry in this
section identifies a python class that implements the operations required by the
component. For example:

``` yaml
lclstreamer:
  [...]
  event_source: Psana1EventSource
  processing_pipeline: NoOpProcessingPipeline
  data_serializer: Hdf5Serializer
  data_handlers:
    - BinaryFileWritingDataHandler
    - BinaryDataStreamingDataHandler
```

With this configuration options, LCLStreamer reads psana1 data (`Psana1EventSource`),
does not perform any processing of the data (`NoOpProcessingPipeline`), serializes the
data in a binary blob with the internal structure of an HDF5 file (`Hdf5Serializer`)
and finally hands the binary blob to two data handlers: one that saves it as a file
(`BinaryFileWritingDataHandler`) and one that streams it through a network socket
(`BinaryDataStreamingDataHandler`)


## Configuring LCLStreamer's components

Configuration options can be provided for each of the Python classes that implement the
LCLStreamer components. The configuration options for a specific class are defined in an
entry with the same name as the class located in a specific section of the configuration
file (`event source`, `processing_pipeline`, `data_serializer`, or `data_handlers`
depending on the component that the class implements)

For example, the configuration parameters for the `Hdf5Serializer` class, which
implements the `data serializer` component, are defined by the `Hdf5Serializer` entry
in the `data_serializer` section of the configuration file:

``` yaml
data_serializer:
    Hdf5Serializer:
        compression_level: 3
        compression: zfp
        fields:
            timestamp: /data/timestamp
            detector_data: /data/data
```

A configuration entry for each of the classes mentioned in the `lclstreamer` section
must be present somewhere in the configuration file (in the relevant section). The
entry must be present even if the class takes no configuration options at all. In that
case, the following syntax must be used:

``` yaml
processing_pipeline:
    NoOpProcessingPipeline: {}
```


## Configuring the data sources

The `data_sources` section of the configuration file defines the data that LCLStreamer
extracts from every data event it processes. If a piece of information is part of the
data event, but not included in the `data_sources` section, LCLStreamer justs ignores it.

The `data sources` section of the configuration file consists of a dictionary of data
sources. Each entry has a key, which acts as a name that identifies the extracted data
throughout the whole LCLStreamer data workflow, and a value, which is itelf a
dictionary. This inner dictionary defines the nature of the data source (via the
mandatory `type` entry) and any other parameters needed to configure it. The `type` of
a data source is the name of the Python class that implements it. For example:

``` yaml
data_sources:
    timestamp:
        type: Psana1Timestamp

    detector_data:
        type: Psana1AreaDetector
        psana_name: Jungfrau1M
        calibration: true
```

This snippet of the configuration files defines two data sources, one called
`timestamp` and one called `detector_data`.  The `timestamp` data class is of type
`Psana1Timestamp`. This means that a Python class of the same name determines how this
type of data is extracted from a data event. The `detector_data` class is instead of
type `Psana1AreaDetector`. The two configuration parameters `psana_name` and
`calibration` are passed to the Python class `Psana1AreaDetector` that defines how this
type of data is retrieved.


## Available Event Sources, Processing Pipelines, Data Handlers and Data Sources

* For a list of all available Event Source python classes, and their configuration
  parameters, see here: [Configuration: Event Sources](configuration_event_sources.md)

* For a list of all available Processing Pipeline classes, and their configuration
  parameters, see here:
  [Configuration: Processing Pipelines](configuration_processing_pipelines.md)

* For a list of all available Serializer classes, and their configuration
  parameters, see here:
  [Configuration: Data Serializers](configuration_data_serializers.md)

* For a list of all available Data Handler classes, and their configuration
  parameters, see here: [Configuration: Data Handlers](configuration_data_handlers.md)

* For a list of all available Data Source classes, and their configuration parameters,
  see here: [Configuration: Data Sources](configuration_data_sources.md)
