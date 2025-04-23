# Configuration: Data Sources

## Psana1AreaDetector

This Data source class retrieves a detector data frame from a psana1 data event.

* This Data Source is compatible with the following Event Source classes:
  `Psana1EventSource`

* The data frame is returned as a 2d numpy array of type `int` (when the data is not
  calibrated) or `float` (when the data is calibrated)

### Configuration parameters for Psana1AreaDetector

* `psana_name` (str): The name (or alias) of the area detector in the psana1 framework

* `calibration` (bool): When the value of this parameter is `True`, the Data Soure
  class retrieves calibrated data frames. When the value is instead `False`, the
  data is retrieved in raw form.


## Psana1Timestamp

This Data Source class retrieves timestamp information from a psana1 data event

* This Data Source is compatible with the following Event Source classes:
  `Psana1EventSource`

* The timestamp information is returned as a numpy array of type `float64`
