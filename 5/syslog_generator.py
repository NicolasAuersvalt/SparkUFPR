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
# dispositivos fantasmas
GHOST_DEVICES = [
    generate_mac()
    for _ in range(5)
]

def timestamp():
    return datetime.now().strftime("%b %d %H:%M:%S")

def send_syslog(message):
    sock.sendto(
        message.encode(),
        (SYSLOG_HOST, SYSLOG_PORT)
    )

while True:

    # ======================
    # Tráfego normal
    # ======================

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

    # ======================
    # Simular Saídas (Desassociação)
    # ======================
    if random.random() < 0.2:  # 20% de chance de alguém ir embora
        mac_out = random.choice(DEVICE_POOL)
        router_out = random.choice(ROUTERS)
        
        msg_out = (
            f"<14>{timestamp()} "
            f"{router_out} hostapd: "
            f"{INTERFACE}: STA {mac_out} "
            f"IEEE 802.11: disassociated"
        )
        send_syslog(msg_out)
        print(f"[SAÍDA] {mac_out} foi embora de {router_out}")

    # ======================
    # Fantasmas (5%)
    # ======================

    if random.random() < 0.5:

        ghost = random.choice(GHOST_DEVICES)

        ghost_router = random.choice(ROUTERS)

        ghost_msg = (
            f"<14>{timestamp()} "
            f"{ghost_router} hostapd: "
            f"{INTERFACE}: STA {ghost} "
            f"IEEE 802.11: associated"
        )

        send_syslog(ghost_msg)

        print(
            f"[GHOST] {ghost} entrou em {ghost_router}"
        )

    time.sleep(1)