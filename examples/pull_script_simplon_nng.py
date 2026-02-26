import sys
from typing import Any, cast

from cbor import (  # type: ignore[import-untyped]  # pyright: ignore[reportMissingTypeStubs] # ty: ignore[unused-ignore-comment]
    loads,  # pyright: ignore[reportUnknownVariableType]
)
from pynng import (  # type: ignore[import-untyped]  # pyright: ignore[reportMissingTypeStubs]# ty: ignore[unused-ignore-comment]
    Pull0,
)

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
