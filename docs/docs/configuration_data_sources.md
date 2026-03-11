# Configuration: Data Sources
## Psana1Timestamp
This Data Source class retrieves timestamp information from a psana1 data event.
* This Data Source is compatible with the following Event Source classes: `Psana1EventSource`.
* The timestamp information is returned as a numpy array of type `uint64`, where seconds are stored in the upper 32 bits and nanoseconds in the lower 32 bits.

## Psana2Timestamp
This Data Source class retrieves timestamp information from a psana2 data event.
* This Data Source is compatible with the following Event Source classes:
`Psana2EventSource`.
* The timestamp information is returned as a numpy array of type `uint64`, where seconds are stored in the upper 32 bits and nanoseconds in the lower 32 bits.
  
## GenericRandomNumpyArray
This Data Source class generates a random numerical array of size and type chosen by the user.
* This Data Source is compatible with the following Event Source classes:
`Psana1EventSource`
* The random array has size and type chosen by the user.

#### Configuration parameters for GenericRandomNumpyArray
*  `array_shape` (list of int): the shape of the generated array, with components that
follow the same format as numpy's `shape` objects.
*  `array_dtype` (str): the numerical type of the generated array, in the same format
as numpy's numerical `dtypes`.

## Psana1DetectorInterface
This Data Source class retrieves any detector data from a psana1 data event.
* This Data Source is compatible with the following Event Source classes:
`Psana1EventSource`.
* The data frame is returned as a 0d, 1d or 2d numpy array of type `int` or `float64`, depending on the source, but a custom dtype can be specified in the config file.

#### Configuration parameters for Psana1DetectorInterface
*  `psana_name` (str): The name (or alias) of the detector in the psana1 framework.
*  `psana_fields` (str or list[str]): A single or a list of fields to retrieve from the detector.
* `dtype` (str): Specific dtype to return the data as if not uint64 or float64, e.g. 'str' can be specified for geometry data.

## Psana2DetectorInterface
This Data Source class retrieves any detector data from a psana2 data event.
* This Data Source is compatible with the following Event Source classes:
`Psana2EventSource`
* The data frame is returned as a 0d, 1d or 2d numpy array of type `int` or `float64`, depending on the source, but a custom dtype can be specified in the config file.

#### Configuration parameters for Psana2DetectorInterface
*  `psana_name` (str): The name (or alias) of the detector in the psana1 framework.
*  `psana_fields` (str or list[str]): A single or a list of fields to retrieve from the detector.
* `dtype` (str): Specific dtype to return the data as if not uint64 or float64, e.g. 'str' can be specified for geometry data.

## Psana2RunInfo
This Data Source class retrieves information about the run, specifically the following information: Experiment's name, Run Timestamp, Run number, Source Identifier (e.g. "mfx123123,run=51").

#### Configuration parameters for Psana2RunInfo
*  `type` (str): Psana2RunInfo

## Examples:

#### Psana1EvrCodes
Use this to retrieve EVR event code data from a psana1 data event.
*  `type`: Psana1DetectorInterface
*  `psana_name`: "evr0"
*  `psana_fields`: eventCodes

The data frame is returned as an array of type `int`. The 1d array has always size 256, since that's the maximum number of EVR codes that can be theoretically associated with an event. The EVR codes associated with the psana1 event are stored at the beginning of the array. Any remaining space is filled with the integer value of 0.

#### Psana1 Calibrated image
To obtain a calibrated image use:
*  `type`: Psana1DetectorInterface
*  `psana_name`: "jungfrau1M"
*  `psana_fields`: calib

#### Psana1 Photon wavelength from PV
  To obtain a calibrated image use:
  *  `type`: Psana1DetectorInterface
*  `psana_name`: "SIOC:SYS0:ML00:AO192"




