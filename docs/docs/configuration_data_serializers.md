# Configuration: Data Serializers

## Hdf5DataSerializer

This Data Serializer class turns the Data accumulated by LCLStreamer into a binary blob
with the internal structure of an HDF5 file.

### Configuration Parameters for Hdf5BinarySerializer

* `compression` (str): This parameter is optional. If present, the HDF5 Data Serializer
  compresses the data with the specified algorithm during serialization. Possible values
  are: `gzip`, `gzip_with_shuffle` (byteshuffle is performed before gzip compression is
  applied) `bitshuffle_with_lz4`, `bitshuffle_with_zstd` (bitshuffle is peformed before
  LZ4 or Zstd comnpressionis applied), and `zfp`. If this parameter is not specified,
  or is set to `null`, no compression is applied during serialization. The default value
  of this parameter is `null`. Example: `gzip`

* `compression_level` (int): This parameter is optional. If the compression algorithm
  specified by the `compression` configuration parameter supports compression levels,
  this parameter specfies the compression level applied during serialization. The
  default value of this parameter is 3. Example: `5`

* `fields` (dict of str): this entry is a dictionary that specified where each data
  source will be stored in the internal structure of the HDF5 file. Each key in the dictionary is the
  name of a data source, and each value is the internal path where the data source is
  stored. If a data source is not present in the dictionary, it is excluded from the
  serialization process and does not appear in the binary blob containing the serialized
  data. Example:

  ```yaml
  fields:
    detector_data: /data/data           # Main image data from detector
    timestamp: /data/timestamp          # Event timestamp
    photon_wavelength: /data/wavelength # Photon wavelength/energy
  ```
