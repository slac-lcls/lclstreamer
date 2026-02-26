import sys
from io import BytesIO
from typing import cast

import hdf5plugin  # pyright: ignore[reportUnusedImport]  # noqa: F401
from h5py import Dataset, File
from zmq import PULL, Context, Socket

context: Context[Socket[bytes]] = Context()
socket: Socket[bytes] = context.socket(PULL)
socket.bind("tcp://127.0.0.1:12321")
count = 0
print("Listening....")
while True:
    msg = socket.recv()
    fh: File = File(BytesIO(msg))  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]
    dataset: Dataset = cast(Dataset, fh[list(fh.keys())[0]])
    content: int = dataset[:].shape[0]
    fh.close()
    count += content
    print(f"Received {count} messages")
    sys.stdout.flush()
