import socket 
import threading

def processamento (connection:socket, address):
    while True:
        msg = connection.recv(1024)

        if not msg:
            print("out")
            break
        
        print(f"Recebi uma ligação do cliente {address} com o conteudo:\n\n  -> {msg.decode('utf-8')}\n")

        msg = " devolta a ti"
        connection.send(msg.encode('utf-8'))

    connection.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    endereco = '10.0.2.10'
    porta = 3000
    s.bind(('10.0.2.10', 3000))


    s.listen()
    print(f"Estou à escuta no {endereco}:{porta}")

    while True:
        connection, address = s.accept()

        threading.Thread(target=processamento,args=(connection, address)).start()

if __name__ == "__main__":
    main()