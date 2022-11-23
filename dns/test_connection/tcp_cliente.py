import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(('10.0.2.10', 3000))

msg = "Adoro Redes :)"
s.send(msg.encode('utf-8'))


msg = s.recv(1024)

if not msg:
    print("IJGWUGRHJG ODEIO REDES GJEWGUJWRGJWRUG")
else:
    print(msg.decode('utf-8'))
    
s.close()