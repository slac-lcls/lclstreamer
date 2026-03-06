# Advanced Topics


## The LCLStreamer Data Workflow

The LCLStreamer application extracts data from events retrieved from an Event Source.

Each LCLStreamer worker retrieves a single event from the Event Source, and extracts all the
required data from the event (via the `get_events` method of a `DataSource` class).
Only data entries listed in the `data_sources` section of the configuration file are
retrieved from each event. Any other data is simply discarded. Within LCLStreamer, the
data retrieved for each event has the format of a Python dictionary. Each key in the
dictionary corresponds to a data source. The value associated with the key is instead
the information retrieved from the data source for the event being processed.

The operations of a Processing Pipeline are then applied to the data retrieved from
each event (via the `__call__` method of a `ProcessingPipeline` class). When leaving
the Processing pipeline, the data still has the format of a Python dictionary,
with each key representing a data entry, and the corresponding value storing the
processed data.

The data is then serialized into a binary form (via the `__call__` method of
a `DataSerializer` class). After being serialized, the data has the format of a binary
blob.

Finally, the data is passed to one or more Data Handlers, that can forward the data to
the filesystem or other external applications. If multiple Data Handlers are present,
they handle the same binary blob in sequence (each calling the `__call__` method of a
`DataHandler` class with the same binary blob): the binary data is not modified at all as
it flows through the Data Handlers.
