import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 514))

print("Escutando Syslog...")

while True:
    data, addr = sock.recvfrom(4096)
    print(data.decode())
