import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

msg = "Adoro Redes :)"

s.sendto(msg.encode('utf-8'), ('10.0.2.10', 3000))