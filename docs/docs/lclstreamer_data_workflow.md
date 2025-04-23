# LCLStreamer Data Workflow

The LCLStreamer application extracts data from events retrieved from an Event Source.

The application retrieves a single event from the Event Source, and extracts all the
required data from the event (Call to the `get_events` method of a `DataSource` class.)
Only data entries listed in the `data_sources` section of the configuration file are
retrieved from each event. Any other data is simply discared. The data retrieved for
each event has the format of a Python dictionary. Each key in the dictionary
corresponds to a data source. The value associated with the key is instead the
information retrieved from the data source for the event being processed.

The operations of a Processing Pipeline are then applied to the data retrieved from
each event (Call to the `process_data` method of a `ProcessingPipeline` class). The
results of processing several consecutive events are accumulated internally, until a
number of events matching the batch size parameter is reached. At that point, the
accumulated data is returned in bulk (Call to the `collect_data` method of a
`ProcessingPipeline` class). The data still has the format of a python dictionary,
which each key representing a data entry, and the corresponding value storing the
accumulated data.

The data is then serialized into a binary form (Call to the `serialize_data` function of
a `DataSerializer` class. After being serialized, the data has the format of a binary
blob.

Finally, the data is passed to one or more Data Handlers, that can foward the data to
the filesystem or other external applications. If multiple Data Handlers are present,
they handle the same binary blob in sequence (Call to the `handle_data` function of a
`DataHandler` class): the binary data is not modified at all as it flows through the
Data Handlers.
