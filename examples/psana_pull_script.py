import sys
from io import BytesIO

import h5py  # type: ignore
from pynng import Pull0  # type: ignore

socket = Pull0(listen="tcp://127.0.0.1:12321")
count = 0
while True:
    msg = socket.recv()
    fh = h5py.File(BytesIO(msg))
    content = fh[fh["/"].keys()[0]][:].shape[0]
    fh.close()
    count += content
    print(f"Received {count} messages")
    sys.stdout.flush()
