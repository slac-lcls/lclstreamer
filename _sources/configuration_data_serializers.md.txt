# Data Serializers



## HDF5BinarySerializer

This Data Serializer class turns the data into a binary blob with the internal structure
of an HDF5 file.

### *Configuration Parameters for HDF5BinarySerializer*

* `compression` (str): This parameter is optional. If present, the HDF5 Data Serializer
  compresses the data with the specified algorithm during serialization. Possible values
  are: `gzip`, `gzip_with_shuffle` (byteshuffle is performed before gzip compression is
  applied), `bitshuffle_with_lz4`, `bitshuffle_with_zstd` (bitshuffle is performed
  before LZ4 or Zstd compression is applied), and `zfp`. If this parameter is not
  specified, or is set to `null`, no compression is applied during serialization. The
  default value of this parameter is `null`. Example: `gzip`

* `compression_level` (int): This parameter is optional. If the compression algorithm
  specified by the `compression` configuration parameter supports compression levels,
  this parameter specifies the compression level applied during serialization. The
  default value of this parameter is `3`. Example: `5`

* `fields` (dict of str): This entry is a dictionary that specifies where each data
  source will be stored in the internal structure of the HDF5 file. Each key in the
  dictionary is the name of a data source, and each value is the internal HDF5 path
  where the data source is stored. If a data source is not present in the dictionary,
  it is excluded from the serialization process and does not appear in the binary blob
  containing the serialized data. Example:

  ```yaml
  fields:
    timestamp: /data/timestamp
    detector_data: /data/data
  ```


## SimplonBinarySerializer

This Data Serializer class turns the data accumulated by LCLStreamer into a binary blob
with the internal structure of a Simplon message. It follows version 1.8 of the Simplon
specification published by Dectris.

Each call to the serializer produces a Simplon image message (`m`-type) containing the
compressed detector frame for the latest event in the batch. When the last LCLStream
worker processes the first batch, it additionally emits a Simplon start message
(`c`-type) with run and detector metadata. At the end of the stream, the last worker
emits a Simplon stop message (`c`-type).

The serializer uses bitshuffle + LZ4 compression for the detector frame data.

* The following data sources must be present in the `data_sources` section of the
  configuration file when using this serializer: `timestamp`, `detector_data`,
  `detector_geometry`, and `run_info`.

### *Configuration Parameters for SimplonBinarySerializer*

* `data_source_to_serialize` (str): The name of the data source whose array is 
  compressed and embedded in each Simplon `m`-type message . This name must correspond
  to a key defined in the `data_sources` section of the configuration file.
  Example: `detector_data`

* `polarization_fraction` (float): The fraction of linear polarization of the X-ray
  beam, as a value between 0 and 1. This value is included in the Simplon start
  message. Example: `0.99`

* `polarization_axis` (list of float): A three-element list representing the
  polarization axis direction vector. This value is included in the Simplon start
  message. Example: `[0.0, 1.0, 0.0]`

* `data_collection_rate` (str): A human-readable string describing the nominal data
  collection rate of the detector. This value is included in the Simplon start message.
  Example: `120 Hz`

* `detector_name` (str): A human-readable name identifying the main detector that
  generates the data encoded in the Simplon `m`-type messages. This value is included
  in the Simplon start message. Example: `Jungfrau 1M`

* `detector_type` (str): A string identifying the model or type of the main detector
  that generates the data encoded in the Simplon `m`-type messages. This value is
  included in the Simplon start message. Example: `Jungfrau 1M`
