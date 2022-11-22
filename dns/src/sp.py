from parser import *
import socket 
import threading

def sendMensage(s, address, port, msg):
    if s == None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))
    s.sendall(msg.encode('utf-8'))

def reciveMensage(connection:socket):
    msg = connection.recv(1024)
    if not msg:
        print("!!!!!  NAO RECEBEU NADA  !!!!!")
    else:
        return msg.decode('utf-8')


def sendDB(dataBase):
    content = []
    for type in dataBase.keys():
        for entry in dataBase[type]:
            line = entry['name'] + ';' 
            line += type + ';'
            line += entry['value'] + ';'
            line += str(entry['ttl']) + ';'
            line += str(entry['priority'])
            content.append(line)
    return content

def processZT (connection:socket, address, config, dataBase):
    for entry in config['SS']:
        if address == entry['value']:
            msg = reciveMensage(connection)
            msgAux = msg.split(';')
            print(f"Recebi uma ligação do cliente {address}")

            if msgAux[0] == 'SOASERIAL' and msgAux[1] == 'example.com.':
                msg = str(dataBase['SOASERIAL'][0]['value'])
                connection.sendall(msg.encode('utf-8'))

                sendDB(address, dataBase)

    



def zoneTransferResolver (config, dataBase):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    endereco = '10.0.0.10'
    porta = 6000
    s.bind((endereco, porta ))
    s.listen()
    print(f"Estou à escuta no {endereco}:{porta}")

    while True:
        connection, address = s.accept()
        threading.Thread(target=processZT,args=(connection, address, config, dataBase)).start()
    
    s.close()



def main():
    configFile = ""#input()
    if configFile == "":
        configFile = "dns/dnsFiles/config.txt"

    config = parserConfig(configFile)
    dataBase = parserDataBaseSP(config['DB'][0]['value'])


    threading.Thread(target=zoneTransferResolver,args=(config, dataBase)).start()
    

    #showTable(config)
    #showTable(dataBase)
    #print(dataBase)
    #print(content)



if __name__ == "__main__":
    main()





