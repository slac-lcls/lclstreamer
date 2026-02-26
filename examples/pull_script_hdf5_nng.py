import sys
from io import BytesIO
from typing import cast

import hdf5plugin  # pyright: ignore[reportUnusedImport]  # noqa: F401
from h5py import Dataset, File
from pynng import (  # type: ignore[import-untyped]  # pyright: ignore[reportMissingTypeStubs]  # ty: ignore[unused-ignore-comment]
    Pull0,
)

socket: Pull0 = Pull0(listen="tcp://127.0.0.1:12321")
count: int = 0
print("Listening....")
while True:
    msg: bytes = cast(bytes, socket.recv())
    fh: File = File(BytesIO(msg))  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType,reportArgumentType]
    dataset: Dataset = cast(Dataset, fh[list(fh.keys())[0]])
    content: int = dataset[:].shape[0]
    fh.close()
    count += content
    print(f"Received {count} messages")
    sys.stdout.flush()
