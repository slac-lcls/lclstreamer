# Introduction

LCLStreamer is application that reads LCLS data in parallel as fast as possible. After
some rapid calibration and/or pre-processing, the data is serialized, accumulated and
finally passed to one or more handlers that transfer it to external applications.

LCLStreamer has several components:

- An event source (that generates the data)
- A processing pipeline (for data reduction, pre-processing, etc.)
- A serializer (that turns the data into a binary blob of bytes)
- One or more handlers (that writes the bytes to files, sends them out  through
  sockets, etc)

The data flows through all the componets in the following way:

``` mermaid
stateDiagram-v2
    direction LR
    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
    C --> G
    A: Source
    B: Processing Pipeline
    C: Serializer
    D: Handler 1
    E: Handler 2
    F: ...
    G: ...
```

LCLStreamer can be run using different implementations of all its components, depending
on the data source, the type of preprocessing that is peformed on the data, and the
format and final destination (a file, a network socket) of the processed data.

* Please see how to install and run LCLStreamer here:
  [Installation / Running](installation_running.md)

* Please see how to configure LCLStreamer here: [Configuration](configuration.md)

* For an in-depth discussion of the data flow through the LCLStreamer application, please
  see here: [LCLStreamer Data Workflow](lclstreamer_data_workflow.md)
