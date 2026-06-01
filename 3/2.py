import random
import socket
import time
from datetime import datetime

SYSLOG_HOST = "127.0.0.1"
SYSLOG_PORT = 514

ROUTER = "router1"
INTERFACE = "wlan0"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

connected = set()

def random_mac():
    return ":".join(
        f"{random.randint(0,255):02x}"
        for _ in range(6)
    )

def timestamp():
    return datetime.now().strftime("%b %d %H:%M:%S")

def send_syslog(message):
    sock.sendto(
        message.encode("utf-8"),
        (SYSLOG_HOST, SYSLOG_PORT)
    )

def association(mac):
    return (
        f"<14>{timestamp()} "
        f"{ROUTER} hostapd: "
        f"{INTERFACE}: STA {mac} "
        f"IEEE 802.11: associated"
    )

def disassociation(mac):
    return (
        f"<14>{timestamp()} "
        f"{ROUTER} hostapd: "
        f"{INTERFACE}: STA {mac} "
        f"IEEE 802.11: disassociated"
    )

while True:

    if not connected or random.random() < 0.6:
        mac = random_mac()
        connected.add(mac)

        msg = association(mac)

    else:
        mac = random.choice(list(connected))
        connected.remove(mac)

        msg = disassociation(mac)

    send_syslog(msg)

    print(f"ENVIADO: {msg}")

    time.sleep(random.uniform(0.5, 2))
