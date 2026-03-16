---
html_theme.sidebar_secondary.remove: true
---

# Introduction

LCLStreamer is an application that reads LCLS data in parallel as fast as possible. After
some rapid calibration and/or pre-processing (and possibly batching), the data is serialized,
and finally passed to one or more handlers that transfer it to external applications.

LCLStreamer has several components:

- An *event source* (that retrieves the data from a data source)
- A *processing pipeline* (for data reduction, pre-processing, etc.)
- A *serializer* (that turns the data into a binary blob of bytes)
- One or more *handlers* (that write the bytes to files, send them through network
  sockets, etc)

The data flows through all the components in the following way:

```{mermaid}
flowchart LR
    A[Source] --> B[Processing Pipeline]
    B --> C[Serializer]
    C --> D[Handler 1]
    C --> E[Handler 2]
    C --> F[...]

    classDef source   fill:lightsteelblue,stroke:slategray,color:black
    classDef pipeline fill:peachpuff,stroke:sandybrown,color:black
    classDef serial   fill:honeydew,stroke:mediumseagreen,color:black
    classDef handler  fill:thistle,stroke:mediumorchid,color:black

    class A source
    class B pipeline
    class C serial
    class D,E,F handler
```

LCLStreamer can be run using different implementations of all its components, depending
on the data source, the type of preprocessing that is performed on the data, and the
format and final destination of the processed data (a file, a network socket).


# Documentation Contents

```{toctree}
:maxdepth: 2
:caption: User Guide

installation
usage
configuration
advanced
```
