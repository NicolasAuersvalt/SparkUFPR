import random
import socket
import time
from datetime import datetime

SYSLOG_HOST = "127.0.0.1"
SYSLOG_PORT = 514

INTERFACE = "wlan0"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ROUTERS = [
    "router1",
    "router2",
    "router3",
    "router4"
]

def generate_mac():
    return ":".join(
        f"{random.randint(0,255):02x}"
        for _ in range(6)
    )

# população fixa
DEVICE_POOL = [
    generate_mac()
    for _ in range(50)
]

def timestamp():
    return datetime.now().strftime("%b %d %H:%M:%S")

def send_syslog(message):
    sock.sendto(
        message.encode(),
        (SYSLOG_HOST, SYSLOG_PORT)
    )

while True:

    mac = random.choice(DEVICE_POOL)

    router = random.choice(ROUTERS)

    msg = (
        f"<14>{timestamp()} "
        f"{router} hostapd: "
        f"{INTERFACE}: STA {mac} "
        f"IEEE 802.11: associated"
    )

    send_syslog(msg)

    print(msg)

    time.sleep(1)