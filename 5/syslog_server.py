import sqlite3
import socket
import re
import hashlib
from datetime import timedelta
from datetime import datetime

# =========================
# REGEX DOS LOGS SYSLOG
# =========================

PATTERN = re.compile(
    r"<\d+>"
    r"(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+"
    r"(?P<router>\S+).*?"
    r"STA\s+"
    r"(?P<mac>(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}).*?"
    r"(?P<event>associated|disassociated)"
)

# =========================
# APs/ROTEADORES
# =========================

routers = {
    "router1": 0,
    "router2": 1,
    "router3": 2,
    "router4": 3
}

N = len(routers)

# =========================
# MATRIZ DE ADJACÊNCIA
# =========================

adj_matrix = [
    [0 for _ in range(N)]
    for _ in range(N)
]

# =========================
# ÚLTIMO AP VISTO
# =========================

last_seen = {}

# =========================
# SESSÕES ATIVAS
# =========================

active_sessions = {}

# =========================
# SQLITE
# =========================

conn = sqlite3.connect("crowd_sensing.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    router TEXT,
    device_id TEXT,
    event TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stay_times (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    router TEXT,
    entry_time TEXT,
    exit_time TEXT,
    duration_minutes REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    device_id TEXT,
    from_router TEXT,
    to_router TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS active_devices (
    device_id TEXT PRIMARY KEY,
    router TEXT,
    last_seen TEXT
)
""")

conn.commit()

# =========================
# HASH DO MAC
# =========================

def cleanup_stale_devices():

    limit = (
        datetime.now() -
        timedelta(minutes=15)
    )

    cursor.execute("""
    DELETE FROM active_devices
    WHERE last_seen < ?
    """, (
        limit.isoformat(),
    ))

def update_active_devices(
    device_id,
    router,
    event_time,
    event
):

    if event == "associated":

        cursor.execute("""
        INSERT OR REPLACE INTO active_devices (
            device_id,
            router,
            last_seen
        )
        VALUES (?, ?, ?)
        """, (
            device_id,
            router,
            event_time.isoformat()
        ))

    elif event == "disassociated":

        cursor.execute("""
        DELETE FROM active_devices
        WHERE device_id = ?
        """, (
            device_id,
        ))

def anonymize_mac(mac):
    daily_salt = datetime.now().strftime("%Y-%m-%d")

    return hashlib.sha256(
        f"{mac}{daily_salt}".encode()
    ).hexdigest()

# =========================
# PARSE TIMESTAMP
# =========================

def parse_timestamp(ts):

    current_year = datetime.now().year

    return datetime.strptime(
        f"{current_year} {ts}",
        "%Y %b %d %H:%M:%S"
    )

# =========================
# ATUALIZA TRANSIÇÕES
# =========================

def update_transition(
    device_id,
    current_router,
    event_time
):

    previous_router = last_seen.get(device_id)

    if previous_router is not None:

        if (
            previous_router in routers
            and current_router in routers
            and previous_router != current_router
        ):

            origem = routers[previous_router]
            destino = routers[current_router]

            # Matriz em memória
            adj_matrix[origem][destino] += 1

            # Persistência da transição
            cursor.execute("""
            INSERT INTO transitions (
                timestamp,
                device_id,
                from_router,
                to_router
            )
            VALUES (?, ?, ?, ?)
            """, (
                event_time.isoformat(),
                device_id,
                previous_router,
                current_router
            ))

            #conn.commit()

            print(
                f"TRANSIÇÃO: "
                f"{previous_router} -> {current_router}"
            )

    last_seen[device_id] = current_router

# =========================
# TEMPO DE PERMANÊNCIA
# =========================

def process_session(
    device_id,
    router,
    event,
    event_time
):

    if event == "associated":

        active_sessions[device_id] = {
            "router": router,
            "start": event_time
        }

    elif event == "disassociated":

        if device_id in active_sessions:

            session = active_sessions[device_id]

            duration = (
                event_time - session["start"]
            )

            minutes = (
                duration.total_seconds() / 60
            )

            print(
                f"\nPERMANÊNCIA:"
                f"\nDevice: {device_id[:8]}"
                f"\nRouter: {session['router']}"
                f"\nTempo: {minutes:.2f} min\n"
            )

            cursor.execute("""
            INSERT INTO stay_times (
                device_id,
                router,
                entry_time,
                exit_time,
                duration_minutes
            )
            VALUES (?, ?, ?, ?, ?)
            """, (
                device_id,
                session["router"],
                session["start"].isoformat(),
                event_time.isoformat(),
                minutes
            ))

            #conn.commit()

            del active_sessions[device_id]

# =========================
# EXIBE MATRIZ
# =========================

def print_matrix():

    router_names = list(routers.keys())

    print("\n=== MATRIZ DE ADJACÊNCIA ===")

    print("        ", end="")

    for r in router_names:
        print(f"{r:>8}", end="")

    print()

    for i, row in enumerate(adj_matrix):

        print(f"{router_names[i]:>8}", end="")

        for value in row:
            print(f"{value:>8}", end="")

        print()

# =========================
# SERVIDOR UDP
# =========================

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sock.bind(("0.0.0.0", 514))

print("Servidor Syslog iniciado na porta 514")

# =========================
# LOOP PRINCIPAL
# =========================

event_counter = 0


try:

    while True:

        data, addr = sock.recvfrom(4096)

        log = data.decode(
            "utf-8",
            errors="ignore"
        )

        match = PATTERN.search(log)

        if not match:
            continue

        timestamp = match.group("timestamp")
        router = match.group("router")
        mac = match.group("mac")
        event = match.group("event")

        event_time = parse_timestamp(
            timestamp
        )

        device_id = anonymize_mac(mac)

        update_active_devices(
            device_id,
            router,
            event_time,
            event
        )

        cursor.execute("""
        INSERT INTO events (
            timestamp,
            router,
            device_id,
            event
        )
        VALUES (?, ?, ?, ?)
        """, (
            event_time.isoformat(),
            router,
            device_id,
            event
        ))

        event_counter += 1

        if event_counter % 100 == 0:
            cleanup_stale_devices()

        if event == "associated":

            update_transition(
                device_id,
                router,
                event_time
            )

        process_session(
            device_id,
            router,
            event,
            event_time
        )
        conn.commit()
        

        del mac

        print({
            "timestamp": timestamp,
            "router": router,
            "event": event,
            "device_id": device_id[:16] + "..."
        })

        print_matrix()

except KeyboardInterrupt:

    print("\nEncerrando servidor...")

    #conn.commit()
    conn.close()
    sock.close()