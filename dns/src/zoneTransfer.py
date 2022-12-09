import socket
import sys 
import threading
import utils



def countEntrys(dataBase):
    i=0
    for domain in dataBase.keys():
        for type in dataBase[domain].keys():
            i += len(dataBase[domain][type])
    return i

def sendDB(dataBase):
    content = []
    for domain in dataBase.keys():
        for type in dataBase[domain].keys():
            for entry in dataBase[domain][type]:
                line = str(domain) + ';'
                line += str(type) + ';'
                line += str(entry['value']) + ';'
                line += str(entry['ttl']) + ';'
                line += str(entry['priority'])
                content.append(line)
    return content

def processZT (connection, addressTup, config, dataBase, logFiles, mode):
    (address, port) = addressTup
    msg = utils.reciveMensageTCP(connection)

    msgAux = msg.split(';')
    dom = msgAux[1]

    if len(msgAux) == 2 and msgAux[0] == 'SOASERIAL' and dom in config.keys():
        for validAddress in config[dom]['SS']:
            if address == validAddress['value']:
                cEntrys = str(countEntrys(dataBase))
                soaSerial = dataBase[dom]['SOASERIAL'][0]['value']
                msg = f"{soaSerial};{cEntrys}"
                connection.sendall(msg.encode('utf-8'))

                msg = utils.reciveMensageTCP(connection)
                
                if (msg == cEntrys):
                    for line in sendDB(dataBase):
                        connection.sendall(line.encode('utf-8'))
                        msg = utils.reciveMensageTCP(connection)
                        if msg != "ACK":
                            # algo correu mal a enviar as mensagens
                            utils.writeInLogFiles(logFiles, f"EZ {address}:{port} SP", mode)
                            connection.close()
                            return
                
                # transferencia de zona executada com sucesso
                utils.writeInLogFiles(logFiles, f"ZT {address}:{port} SP", mode)
                connection.close()
                return

        # dominio existe mas o endereco nao é valido
        utils.writeInLogFiles(logFiles, f"EZ {address}:{port} SP", mode)
        connection.close()
        return

    # dominio nao existe
    utils.writeInLogFiles(logFiles, f"EZ {address}:{port} SP", mode)
    connection.close()

def zoneTransferResolver (config, dataBase, logFiles, mode):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind(('', 6000))
        (address, port) = s.getsockname()
    except:
        print(f"Couldnt bind to localhost:{6000}")
        sys.exit()

    s.listen()

    if mode:
        utils.writeInLogFiles(logFiles, f"ST {address} {port} debug", mode)
    else:
        utils.writeInLogFiles(logFiles, f"ST {address} {port} shy", mode)

    while True:
        connection, addressTup = s.accept()
        threading.Thread(target=processZT,args=(connection, addressTup, config, dataBase, logFiles, mode)).start()

    s.close()



def zoneTransferRequest(address, serialNum, dom):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((address, 6000))
    except:
        print(f"Couldnt bind to {address}:{6000}")
        sys.exit()

    msg=f"SOASERIAL;{dom}"
    s.sendall(msg.encode('utf-8'))

    msg=utils.reciveMensageTCP(s)
    if msg == None:
        s.close()
        return None
    else:
        msgAux = msg.split(';')

    if serialNum != int(msgAux[0]):
        s.sendall(str(msgAux[1]).encode('utf-8'))
        infoDataBase=[]
        for i in range(0,int(msgAux[1])):
            msg = utils.reciveMensageTCP(s)
            if msg == None:
                s.close()
                return None
            infoDataBase.append(msg)
            s.sendall("ACK".encode('utf-8'))
    else:    
        s.sendall("ACK".encode('utf-8'))
        return None

    s.close()
    return infoDataBase