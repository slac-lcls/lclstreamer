"""
Fast Binary Serializer for high-throughput numpy array streaming.

This serializer is optimized for low-latency, high-bandwidth streaming of numpy arrays.
It avoids the overhead of HDF5 by using a simple binary format with optional Blosc compression.

Performance comparison (67MB Jungfrau array):
- HDF5BinarySerializer: ~1000ms deserialization
- FastBinarySerializer (no compression): ~10-20ms deserialization
- FastBinarySerializer (blosc lz4): ~30-50ms deserialization

Binary format (version 1):
    Header:
        - 4 bytes: magic number (0x4E504159 = "NPAY")
        - 4 bytes: version (uint32)
        - 4 bytes: number of fields (uint32)

    Per field:
        - 4 bytes: field name length (uint32)
        - N bytes: field name (utf-8)
        - 4 bytes: dtype string length (uint32)
        - M bytes: dtype string (e.g., "<f4")
        - 4 bytes: number of dimensions (uint32)
        - ndim * 8 bytes: shape (int64 per dimension)
        - 1 byte: compression type (0=none, 1=lz4, 2=zstd)
        - 8 bytes: uncompressed size (uint64)
        - 8 bytes: compressed/actual size (uint64)
        - data_size bytes: array data (compressed or raw)
"""

import struct
from collections.abc import Iterator

import numpy as np

from ...models.parameters import FastBinarySerializerParameters
from ...utils.logging import log
from ...utils.protocols import DataSerializerProtocol
from ...utils.typing import StrFloatIntNDArray

# Optional blosc import
try:
    import blosc2

    BLOSC_AVAILABLE = True
except ImportError:
    try:
        import blosc

        BLOSC_AVAILABLE = True
    except ImportError:
        BLOSC_AVAILABLE = False
        blosc = None
        blosc2 = None

MAGIC = 0x4E504159  # "NPAY" in hex
VERSION = 1


class FastBinarySerializer(DataSerializerProtocol):
    """
    High-performance binary serializer for numpy arrays.

    Uses a simple binary format optimized for streaming:
    - Minimal overhead (no HDF5 metadata)
    - Optional Blosc compression (multi-threaded, SIMD-optimized)
    - Near zero-copy deserialization possible
    """

    def __init__(self, parameters: FastBinarySerializerParameters) -> None:
        """
        Initialize the fast binary serializer.

        Args:
            parameters: Configuration parameters
        """
        if parameters.type != "FastBinarySerializer":
            raise ValueError(
                "Data serializer parameters do not match the expected type"
            )

        self._fields: dict[str, str] = parameters.fields
        self._compression = parameters.compression
        self._compression_level = parameters.compression_level
        self._n_threads = parameters.n_threads

        # Compression type byte
        if self._compression is None or self._compression == "none":
            self._compression_byte = 0
        elif self._compression == "lz4":
            self._compression_byte = 1
            if not BLOSC_AVAILABLE:
                log.warning("Blosc not available, falling back to no compression")
                self._compression_byte = 0
        elif self._compression == "zstd":
            self._compression_byte = 2
            if not BLOSC_AVAILABLE:
                log.warning("Blosc not available, falling back to no compression")
                self._compression_byte = 0
        else:
            log.warning(f"Unknown compression '{self._compression}', using none")
            self._compression_byte = 0

        # Configure blosc if available
        if BLOSC_AVAILABLE and self._compression_byte > 0:
            if blosc2 is not None:
                # blosc2 configuration is per-call
                pass
            elif blosc is not None:
                blosc.set_nthreads(self._n_threads)

    def _compress(self, data: bytes) -> bytes:
        """Compress data using configured method."""
        if self._compression_byte == 0:
            return data

        cname = "lz4" if self._compression_byte == 1 else "zstd"

        if blosc2 is not None:
            return blosc2.compress(
                data,
                clevel=self._compression_level,
                cname=cname,
                nthreads=self._n_threads,
            )
        elif blosc is not None:
            return blosc.compress(
                data,
                clevel=self._compression_level,
                cname=cname,
                shuffle=blosc.BITSHUFFLE,
            )
        return data

    def _serialize_array(self, name: str, arr: np.ndarray) -> bytes:
        """Serialize a single numpy array to bytes."""
        parts = []

        # Field name
        name_bytes = name.encode("utf-8")
        parts.append(struct.pack("<I", len(name_bytes)))
        parts.append(name_bytes)

        # Dtype
        dtype_str = arr.dtype.str.encode("utf-8")
        parts.append(struct.pack("<I", len(dtype_str)))
        parts.append(dtype_str)

        # Shape
        parts.append(struct.pack("<I", arr.ndim))
        for dim in arr.shape:
            parts.append(struct.pack("<q", dim))

        # Data (ensure contiguous)
        if not arr.flags["C_CONTIGUOUS"]:
            arr = np.ascontiguousarray(arr)

        raw_data = arr.tobytes()
        uncompressed_size = len(raw_data)

        # Compress if enabled
        if self._compression_byte > 0:
            compressed_data = self._compress(raw_data)
        else:
            compressed_data = raw_data

        compressed_size = len(compressed_data)

        # Compression info and data
        parts.append(struct.pack("<B", self._compression_byte))
        parts.append(struct.pack("<Q", uncompressed_size))
        parts.append(struct.pack("<Q", compressed_size))
        parts.append(compressed_data)

        return b"".join(parts)

    def __call__(
        self, stream: Iterator[dict[str, StrFloatIntNDArray | None]]
    ) -> Iterator[bytes]:
        """
        Serialize events to fast binary format.

        Args:
            stream: Iterator of event data dictionaries

        Yields:
            Binary blob for each event
        """
        for data in stream:
            parts = []

            # Header
            parts.append(struct.pack("<I", MAGIC))
            parts.append(struct.pack("<I", VERSION))

            # Count valid fields
            valid_fields = [
                (name, hdf5_path)
                for name, hdf5_path in self._fields.items()
                if name in data and data[name] is not None
            ]
            parts.append(struct.pack("<I", len(valid_fields)))

            # Serialize each field
            for name, hdf5_path in valid_fields:
                arr = data[name]
                if isinstance(arr, np.ndarray):
                    # Use the HDF5 path as the field name (for compatibility)
                    parts.append(self._serialize_array(hdf5_path, arr))
                else:
                    # Wrap scalar in array
                    arr = np.array(arr)
                    parts.append(self._serialize_array(hdf5_path, arr))

            yield b"".join(parts)


def fast_deserialize(data: bytes) -> dict[str, np.ndarray]:
    """
    Deserialize fast binary format to dict of numpy arrays.

    This function is designed for maximum speed:
    - Single pass through the data
    - Minimal memory copies
    - Multi-threaded decompression (if blosc available)

    Args:
        data: Binary blob from FastBinarySerializer

    Returns:
        Dictionary mapping field names to numpy arrays
    """
    offset = 0

    # Read header
    magic, version, n_fields = struct.unpack_from("<III", data, offset)
    offset += 12

    if magic != MAGIC:
        raise ValueError(f"Invalid magic number: {magic:#x}, expected {MAGIC:#x}")
    if version != VERSION:
        raise ValueError(f"Unsupported version: {version}, expected {VERSION}")

    result = {}

    for _ in range(n_fields):
        # Field name
        (name_len,) = struct.unpack_from("<I", data, offset)
        offset += 4
        name = data[offset : offset + name_len].decode("utf-8")
        offset += name_len

        # Dtype
        (dtype_len,) = struct.unpack_from("<I", data, offset)
        offset += 4
        dtype_str = data[offset : offset + dtype_len].decode("utf-8")
        offset += dtype_len
        dtype = np.dtype(dtype_str)

        # Shape
        (ndim,) = struct.unpack_from("<I", data, offset)
        offset += 4
        shape = struct.unpack_from(f"<{ndim}q", data, offset)
        offset += ndim * 8

        # Compression info
        (compression_type,) = struct.unpack_from("<B", data, offset)
        offset += 1
        uncompressed_size, compressed_size = struct.unpack_from("<QQ", data, offset)
        offset += 16

        # Read data
        compressed_data = data[offset : offset + compressed_size]
        offset += compressed_size

        # Decompress if needed
        if compression_type == 0:
            # No compression - use frombuffer for zero-copy when possible
            arr = np.frombuffer(compressed_data, dtype=dtype).reshape(shape)
            # Make a copy since frombuffer creates a view
            arr = arr.copy()
        else:
            # Decompress
            if blosc2 is not None:
                raw_data = blosc2.decompress(compressed_data)
            elif blosc is not None:
                raw_data = blosc.decompress(compressed_data)
            else:
                raise RuntimeError("Data is compressed but blosc is not available")

            arr = np.frombuffer(raw_data, dtype=dtype).reshape(shape)

        result[name] = arr

    return result
