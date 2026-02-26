import argparse
import socket
import sys
from io import BytesIO
from typing import cast

import hdf5plugin  # pyright: ignore[reportUnusedImport]  # noqa: F401
from h5py import Dataset, File, Group
from zmq import PULL, Context, Socket

# Parse command line arguments
parser = argparse.ArgumentParser(
    description="Pull HDF5 data from LCLStreamer data source clients"
)
parser.add_argument(
    "--hostname",
    default=socket.gethostname(),
    help="Hostname to listen on (default: auto-detect)",
)
parser.add_argument(
    "--port", type=int, default=12321, help="Port to listen on (default: 12321)"
)
args = parser.parse_args()

# Listen as server to receive data from multiple MPI clients
context: Context[Socket[bytes]] = Context()
pull_socket: Socket[bytes] = context.socket(PULL)
pull_socket.bind("tcp://127.0.0.1:12321")

count: int = 0
print("Listening....")
while True:
    msg: bytes = pull_socket.recv()
    fh: File = File(BytesIO(msg))  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType,reportArgumentType]

    # Print available datasets in the HDF5 structure
    print(f"Available datasets: {list(fh.keys())}")

    # Access the data based on the configured HDF5 field mapping
    if "/data/data" in fh:  # detector_data
        dataset: Dataset = cast(Dataset, fh["/data/data"])
        print(
            f"Dataset info: compression={dataset.compression},"  # type: ignore[attr-defined]  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]  # ty: ignore[unresolved-attribute]
            f"shape={dataset.shape}"
        )
        try:
            detector_shape: tuple[int] = dataset[:].shape
            print(f"Detector data shape: {detector_shape}")
        except OSError as e:
            print(f"Error reading data: {e}")
            print("Trying to read without loading full array...")
            print(f"Dataset shape: {dataset.shape}, dtype: {dataset.dtype}")

    if "/data/wavelength" in fh:  # photon_wavelength
        wavelength = cast(Dataset, fh["/data/wavelength"])[:]
        print(f"Photon wavelength: {wavelength}")

    if "/data/timestamp" in fh:  # timestamp
        timestamp = cast(Dataset, fh["/data/timestamp"])[:]
        print(f"Timestamp: {timestamp}")

    if "/data/random" in fh:  # random array
        random_shape = cast(Dataset, fh["/data/random"])[:].shape
        print(f"Random array shape: {random_shape}")

    # Fallback to original logic for other data structures
    if "/data/data" not in fh and cast(Group, fh["/"]).keys():
        first_key: str = list(fh.keys())[0]
        content: int = cast(Dataset, fh[first_key])[:].shape[0]
        count += content
        print(f"Received {count} messages from dataset: {first_key}")

    fh.close()
    count += 1
    print(f"Received {count} data packets")
    print("-" * 40)
    sys.stdout.flush()
