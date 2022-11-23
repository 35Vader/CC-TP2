import socket
import sys 
import threading
import time
import utils
import parser

def countEntrys(dataBase):
    i=0
    for type in dataBase.keys():
        for entry in dataBase[type]:
            i+=1
    return i

def sendDB(dataBase):
    content = []
    for type in dataBase.keys():
        for entry in dataBase[type]:
            line = str(entry['name']) + ';' 
            line += str(type) + ';'
            line += str(entry['value']) + ';'
            line += str(entry['ttl']) + ';'
            line += str(entry['priority'])
            content.append(line)
    return content

def processZT (connection:socket.socket, addressTup, config, dataBase):
    (address, port) = addressTup
    for entry in config['SS']:
        if address == entry['value']:
            msg = utils.reciveMensage(connection)
            msgAux = msg.split(';')
            print(f"Recebi uma ligação do cliente {address}")

            if msgAux[0] == 'SOASERIAL' and msgAux[1] == dataBase['SOASP'][0]['name']:
                c = str(countEntrys(dataBase))
                msg = f"{dataBase['SOASERIAL'][0]['value']};{c}"
                connection.sendall(msg.encode('utf-8'))

                msg = utils.reciveMensage(connection)
                if (msg == c):
                    for line in sendDB(dataBase):
                        connection.sendall(line.encode('utf-8'))
                        msg = utils.reciveMensage(connection)
                        if msg != "ACK":
                            print("Base de dados não enviada")
                            exit()
                    print("Base de dados enviada com sucesso")
                    utils.showTable(dataBase)
                else:
                    print("Base de dados atualizada")

    connection.close()

def getSP(dataBase):
    sp = dataBase['SOASP'][0]['value']
    for a in dataBase['A']:
        if a['name'] == sp:
            endereco = a['value']
    return endereco

def zoneTransferResolver (config, dataBase):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    endereco = getSP(dataBase)
    porta = 6000
    s.bind((endereco, porta))

    s.listen()
    print(f"Estou à escuta no {endereco}:{porta}")

    while True:
        connection, addressTup = s.accept()
        threading.Thread(target=processZT,args=(connection, addressTup, config, dataBase)).start()

    s.close()


def main(configFile):
    config = parser.parserConfig(configFile)
    dataBase = parser.parserDataBaseSP(config['DB'][0]['value'])


    threading.Thread(target=zoneTransferResolver,args=(config, dataBase)).start()

    #utils.showTable(config)
    #utils.showTable(dataBase)
    #print(dataBase)
    #print(content)



if __name__ == "__main__":
    if len(sys.argv) > 1:
        configFile = sys.argv[1]
    else:
        configFile = 'dns/dnsFiles/configSP.txt'
    main(configFile)





