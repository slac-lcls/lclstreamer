# Event Sources



## Psana1EventSource

This Event Source class retrieves data events from the psana1 software framework in use
at the LCLS-I facility.

* The `source_identifier` for this event source is a text string that identifies a run
  within a specific LCLS experiment in the psana1 framework. The string has the form
  `exp=<experiment>:run=<run_number>` (e.g.: `exp=xpptut15:run=430`). 

* The following Data Source classes are compatible with this Event Source:
  `Psana1Timestamp`, `Psana1DetectorInterface`, `GenericRandomNumpyArray`,
  `FloatValue`, `IntValue`, `SourceIdentifier`

### *Configuration Parameters for Psana1EventSource*

This Event Source does not require any configuration parameters beyond the mandatory
`type` entry.



## Psana2EventSource

This Event Source class retrieves data events from the psana2 software framework in use
at the LCLS-II facility.

* The `source_identifier` for this event source is a comma-separated string of
  `key=value` pairs identifying the data source. Supported keys are:

    - `exp`: the experiment name (e.g.: `exp=mfxp1002221`)
    - `run`: the run number (e.g.: `run=5`)
    - `files`: path to directory containing the data files (used only if the files are
      in a non-standard psana2 folder (e.g.: `files=/path/to/xtc2_dir`)
    - `max_events`: maximum number of events to process

  Example: `exp=mfxp1002221,run=5`

* The following Data Source classes are compatible with this Event Source:
  `Psana2Timestamp`, `Psana2DetectorInterface`, `Psana2RunInfo`,
  `GenericRandomNumpyArray`,  `FloatValue`, `IntValue`, `SourceIdentifier`

### *Configuration Parameters for Psana2EventSource*

This Event Source does not require any configuration parameters beyond the mandatory
`type` entry.



## InternalEventSource

This Event Source class generates synthetic data events entirely within LCLStreamer,
without relying on any external data-acquisition framework. It is intended mainly
for testing and development purposes.

* The `source_identifier` string is passed through to the configured data sources as
  contextual information but is not used by the event source itself to open any
  external data stream.

* The following Data Source classes are compatible with this Event Source:
  `GenericRandomNumpyArray`, `FloatValue`, `IntValue`, `SourceIdentifier`

### *Configuration Parameters for InternalEventSource*

* `number_of_events_to_generate` (int): The total number of synthetic events that the
  Event Source will produce before the stream is exhausted. Example: `1000`
