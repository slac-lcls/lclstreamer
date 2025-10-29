import sys
from io import BytesIO
from typing import Any

from cbor import loads
from pynng import Pull0  # type: ignore

socket = Pull0(listen="tcp://127.0.0.1:12321")
count = 0
while True:
    msg: bytes = socket.recv()
    header: str = chr(msg[0])
    content: dict[str, Any] = loads(msg[1:])
    print("Message Received:")
    print(f"  Header: {header}")
    print(f'  Timestamp: {content["timestamp"]}')
    print(f'  Type: {content["type"]}')
    sys.stdout.flush()
