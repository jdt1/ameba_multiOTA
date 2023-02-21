import socket
import os

INT_MAX_VALUE = 2**32 - 1


def push_update(filename, host, port):
    f = open(filename, "rb")
    checksum = 0
    length = os.stat(filename).st_size
    empty = 0

    byte = f.read(1)
    while byte != b"":
        checksum = checksum + int.from_bytes(byte, "big")
        byte = f.read(1)
    checksum = checksum % INT_MAX_VALUE
    f.close()

    print("Checksum: " + hex(checksum))
    print("Length: " + str(length))

    bytes = bytearray()
    bytes = bytes + checksum.to_bytes(4, "little")
    bytes = bytes + empty.to_bytes(4, "little")
    bytes = bytes + length.to_bytes(4, "little")

    f = open(filename, "rb")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.send(bytes)
        s.send(f.read())

    print("sent everything")

    f.close()
