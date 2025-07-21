# Configuration: Data Sources

## Psana1AreaDetector

This Data Source class retrieves a detector data frame from a psana1 data event.

* This Data Source is compatible with the following Event Source classes:
  `Psana1EventSource`

* The data frame is returned as a 2d numpy array of type `int` (when the data is not
  calibrated) or `float` (when the data is calibrated)

#### Configuration parameters for Psana1AreaDetector

* `psana_name` (str): The name (or alias) of the area detector in the psana1 framework

* `calibration` (bool): When the value of this parameter is `True`, the Data Source
  class retrieves calibrated data frames. When the value is instead `False`, the
  data is retrieved in raw form.



## Psana1AssmebledAreaDetector

This Data Source class retrieves a detector data frame from a psana1 data event, in
calibrated form, and with geometry information already applied to it. This is the
closest approximation to the physical appearance of the area detector.

* This Data Source is compatible with the following Event Source classes:
  `Psana1EventSource`

* The data frame is returned as a 2d numpy array of type `float`

#### Configuration parameters for Psana1AssmebledAreaDetector

* `psana_name` (str): The name (or alias) of the area detector in the psana1 framework



## Psana1PV

This Data Source class retrieves the value of an Epics variable from a psana1 data
event.

* This Data Source is compatible with the following Event Source classes:
  `Psana1EventSource`

* The variable value is returned in the form of an numpy array of type `int`, `float` or
  `str` type, depending on the value of the Epics variable

#### Configuration parameters for Psana1PV

* `psana_name` (str): The name (or alias) of the Epics variable in the psana1
  framework



## Psana1BbmonDetectorTotalIntensity

This Data Source class retrieves the total intensity recorded by a BBmon detector from
a psana1 data event.

* This Data Source is compatible with the following Event Source classes:
  `Psana1EventSource`

* The variable value is returned in the form of an numpy array of type `float`

#### Configuration parameters for Psana1BbmonDetectorTotalIntensity

* `psana_name` (str): The name (or alias) of the BBmon detector in the psana1 framework



## Psana1IpmDetector

This Data Source class retrieves IPM detector data from a psana1 data event.

* This Data Source is compatible with the following Event Source classes:
  `Psana1EventSource`

* The data frame is returned as an array of type `float`

#### Configuration parameters for Psana1IpmDetecto

* `psana_name` (str): The name (or alias) of the IPM detector in the psana1 framework

* `psana_function` (str): The name of the psana1 function used to recover data from
  the IPM detector. Currently supported values are:

    - `channel`: this function returns channel information from the detector in a 2d
      array. The first axis of the array represents the channel number, while the
      data points from each channel are encoded along the second axis



## Psana1UsdUsbDetector

This Data Source class retrieves UsdUsb detector data from a psana1 data event.

* This Data Source is compatible with the following Event Source classes:
  `Psana1EventSource`

* The data frame is returned as an array of type `float`

#### Configuration parameters for Psana1UsdUsbDetector

* `psana_name` (str): The name (or alias) of the UsbUsd detector in the psana1 framework

* `psana_function` (str): The name of the psana1 function used to recover data from
  the UsbUsd detector. Currently supported values are:

    - `values`: this function returns the values read by the detector as an array of
      type `float` 



## Psana1EvrCodes

This Data Source class retrieves EVR event code data from a psana1 data event.

* This Data Source is compatible with the following Event Source classes:
  `Psana1EventSource`

* The data frame is returned as an array of type `int`. The 1d array has always size 
  256, since that's the maximum number of EVR codes that can be theoretically
  associated with an event. The EVR codes associated with the psana1 event are stored
  at the beginning of the array. Any remaining space is filled with the integer value
  0 

#### Configuration parameters for Psana1EvrCodes

* `psana_name` (str): The name (or alias) of the EVR data source in the psana1
  framework



## Psana1Timestamp

This Data Source class retrieves timestamp information from a psana1 data event.

* This Data Source is compatible with the following Event Source classes:
  `Psana1EventSource`

* The timestamp information is returned as a numpy array of type `float64`



## GenericRandomNumpyArray

This Data Source class generates a random numerical array of size and type chosen by
the user.

* This Data Source is compatible with the following Event Source classes:
  `Psana1EventSource`

* The random array has size and type chosen by the user

#### Configuration parameters for Psana1EvrCodes

* `array_shape` (list of int): the shape of the generated array, with components that
  follow the same format as numpy's `shape` obejcts

* `array_dtype` (str): the numerical type of the generated array, in the same format
  as numpy's numerical `dtypes`



