import random
import time
from datetime import datetime

ROUTER = "router1"
INTERFACE = "wlan0"

TOTAL_DEVICES = 200

def generate_mac():
    return ":".join(
        f"{random.randint(0,255):02x}"
        for _ in range(6)
    )

device_pool = [generate_mac() for _ in range(TOTAL_DEVICES)]
connected = set()

def timestamp():
    return datetime.now().strftime("%b %d %H:%M:%S")

def association(mac):
    return (
        f"<14>{timestamp()} {ROUTER} hostapd: "
        f"{INTERFACE}: STA {mac} IEEE 802.11: associated"
    )

def disassociation(mac):
    return (
        f"<14>{timestamp()} {ROUTER} hostapd: "
        f"{INTERFACE}: STA {mac} IEEE 802.11: disassociated"
    )

while True:

    if len(connected) < 10:
        action = "connect"

    elif len(connected) > 100:
        action = "disconnect"

    else:
        action = random.choice(["connect", "disconnect"])

    if action == "connect":
        available = list(set(device_pool) - connected)

        if available:
            mac = random.choice(available)
            connected.add(mac)
            print(association(mac))

    else:
        if connected:
            mac = random.choice(list(connected))
            connected.remove(mac)
            print(disassociation(mac))

    time.sleep(random.uniform(0.2, 2.0))
