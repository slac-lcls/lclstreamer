import argparse
import socket
import sys
from io import BytesIO

import h5py  # type: ignore
import hdf5plugin  # type: ignore
from pynng import Pull0  # type: ignore

# Parse command line arguments
parser = argparse.ArgumentParser(description="Pull HDF5 data from LCLStreamer data source clients")
parser.add_argument("--hostname", default=socket.gethostname(), 
                    help="Hostname to listen on (default: auto-detect)")
parser.add_argument("--port", type=int, default=12321,
                    help="Port to listen on (default: 12321)")
args = parser.parse_args()

# Listen as server to receive data from multiple MPI clients
listen_address = f"tcp://{args.hostname}:{args.port}"
print(f"Listening on {listen_address}")
pull_socket = Pull0(listen=listen_address)

count = 0
while True:
    msg = pull_socket.recv()
    fh = h5py.File(BytesIO(msg))

    # Print available datasets in the HDF5 structure
    print(f"Available datasets: {list(fh.keys())}")

    # Access the data based on the configured HDF5 field mapping
    if '/data/data' in fh:  # detector_data
        dataset = fh['/data/data']
        print(f"Dataset info: compression={dataset.compression}, shape={dataset.shape}")
        try:
            detector_shape = dataset[:].shape
            print(f"Detector data shape: {detector_shape}")
        except OSError as e:
            print(f"Error reading data: {e}")
            print("Trying to read without loading full array...")
            print(f"Dataset shape: {dataset.shape}, dtype: {dataset.dtype}")

    if '/data/wavelength' in fh:  # photon_wavelength
        wavelength = fh['/data/wavelength'][:]
        print(f"Photon wavelength: {wavelength}")

    if '/data/timestamp' in fh:  # timestamp
        timestamp = fh['/data/timestamp'][:]
        print(f"Timestamp: {timestamp}")

    if '/data/random' in fh:  # random array
        random_shape = fh['/data/random'][:].shape
        print(f"Random array shape: {random_shape}")

    # Fallback to original logic for other data structures
    if '/data/data' not in fh and fh["/"].keys():
        first_key = list(fh["/"].keys())[0]
        content = fh[first_key][:].shape[0]
        count += content
        print(f"Received {count} messages from dataset: {first_key}")

    fh.close()
    count += 1
    print(f"Received {count} data packets")
    print("-" * 40)
    sys.stdout.flush()