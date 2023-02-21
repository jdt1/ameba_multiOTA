from datetime import datetime, timedelta
from time import sleep
import socket
import logging
import os

UDP_IP = ""
OTA_ANNOUNCE_PORT = 8081
OTA_UPDATE_PORT = 8082

BPARTY_IDENTIFIER = b"bparty"
INT_MAX_VALUE = 2**32 - 1

DEFAULT_TIMEOUT = 2  # seconds

logger = logging.getLogger(__name__)


class Robot:
    def __init__(self, ip_address, message):
        self.ip_address = ip_address
        self.ID = ip_address[0].split(".")[-1]
        self.last_message = None
        self.last_seen = datetime.now()

    def update(self, message):
        self.last_message = message
        self.last_seen = datetime.now()

    def was_seen_recently(self, seconds=DEFAULT_TIMEOUT):
        return datetime.now() - self.last_seen < timedelta(seconds=seconds)

    def perform_ota(self, header: bytes, firmware: bytes):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip_address, OTA_UPDATE_PORT))
            s.send(header)
            s.send(firmware)

    def __eq__(self, other):
        return self.ID == other.ID

    def __repr__(self):
        return f"Robot {self.ID} last seen at {self.last_seen}"


class AmebaParty:
    def __init__(self, callback=None):
        self.robots = []
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.settimeout(0.1)
        self._callback = callback

    def listen_blocking(self, ip=UDP_IP, port=OTA_ANNOUNCE_PORT):
        self._sock.bind((ip, port))
        logging.debug(f"Listening for UDP messages on port {port}")
        while True:
            try:
                data, addr = self._sock.recvfrom(1024)
                if (
                    len(data) >= len(BPARTY_IDENTIFIER)
                    and data[: len(BPARTY_IDENTIFIER)] == BPARTY_IDENTIFIER
                ):
                    r = Robot(addr, data)
                    if r not in self.robots:
                        self.add(r)
                    else:
                        self.update(r.ID, data)
                    logging.debug(
                        f'Incoming message from {addr} ({str(r)}): {data.decode("utf-8")}'
                    )
                else:
                    logging.debug(
                        f'Incoming message from {addr} (not recognized): {data.decode("utf-8")}'
                    )

            except socket.timeout:
                pass
            if self._callback:
                self._callback(self.count())

            sleep(1)

    def add(self, robot):
        self.robots.append(robot)

    def update(self, ID, message):
        for robot in self.robots:
            if robot.ID == ID:
                robot.update(message)
                return
        self.add(Robot(ID, message))

    def get_active_robots(self, seconds=DEFAULT_TIMEOUT):
        return [robot for robot in self.robots if robot.was_seen_recently(seconds)]

    def get_ip_addresses(self, seconds=DEFAULT_TIMEOUT):
        return [robot.ID for robot in self.get_active_robots(seconds)]

    def count(self, seconds=DEFAULT_TIMEOUT):
        return len(self.get_active_robots(seconds))

    def perform_ota(self, filename):
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

        logger.debug("Checksum: " + hex(checksum))
        logger.debug("Length: " + str(length))

        header = bytearray()
        header = header + checksum.to_bytes(4, "little")
        header = header + empty.to_bytes(4, "little")
        header = header + length.to_bytes(4, "little")

        with open(filename, "rb") as f:
            firmware = f.read()

            for robot in self.get_active_robots():
                logger.info(f"Performing OTA on {str(robot)}")
                robot.perform_ota(header, firmware)
