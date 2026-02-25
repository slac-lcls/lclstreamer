import sys
from typing import Any, cast

from cbor import (  # pyright: ignore[reportMissingTypeStubs]
    loads,  # pyright: ignore[reportUnknownVariableType]
)
from pynng import Pull0  # pyright: ignore[reportMissingTypeStubs]

socket: Pull0 = Pull0(listen="tcp://127.0.0.1:12321")
count: int = 0
print("Listening....")
while True:
    msg: bytes = cast(bytes, socket.recv())
    header: str = chr(msg[0])
    content: dict[str, Any] = cast(dict[str, Any], loads(msg[1:]))
    print("Message Received:")
    print(f"  Header: {header}")
    print(f"  Timestamp: {content['timestamp']}")
    print(f"  Type: {content['type']}")
    sys.stdout.flush()
