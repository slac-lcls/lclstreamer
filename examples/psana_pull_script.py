from io import BytesIO

import h5py  # type: ignore
from pynng import Pull0  # type: ignore

socket = Pull0(listen="tcp://127.0.0.1:12321")
while True:
    msg = socket.recv()
    fh = h5py.File(BytesIO(msg))
    fh.close()
