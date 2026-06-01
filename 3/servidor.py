import socket
import re
import hashlib
from datetime import datetime

PATTERN = re.compile(
    r"<\d+>"
    r"(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+"
    r"(?P<router>\S+).*?"
    r"STA\s+"
    r"(?P<mac>(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})"
)

def anonymize_mac(mac):
    daily_salt = datetime.now().strftime("%Y-%m-%d")

    return hashlib.sha256(
        f"{mac}{daily_salt}".encode()
    ).hexdigest()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 514))

while True:

    data, _ = sock.recvfrom(4096)

    log = data.decode("utf-8", errors="ignore")

    match = PATTERN.search(log)

    if not match:
        continue

    timestamp = match.group("timestamp")
    router = match.group("router")

    # MAC real existe apenas nesta linha
    mac = match.group("mac")

    # Identificador anonimizado
    device_id = anonymize_mac(mac)

    # A partir daqui o MAC não é mais usado
    del mac

    print({
        "timestamp": timestamp,
        "router": router,
        "device_id": device_id
    })
