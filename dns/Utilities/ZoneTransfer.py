import socket
import sys
import threading
import time
from Utilities.Utils import Utils



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
                line = str(domain) + ','
                line += str(type) + ','
                line += str(entry['value']) + ','
                line += str(entry['ttl']) + ','
                line += str(entry['priority']) + ';'
                content.append(line)
    return content

def processZT (connection:socket.socket, addressTup, config, dataBase, logFiles, mode):
    (address, port) = addressTup
    msg = connection.recv(2048)
    if not msg:
        return None
    else:
        msg = msg.decode('utf-8')

    msgAux = msg.split(';')
    dom = msgAux[1]

    if len(msgAux) == 2 and msgAux[0] == 'SOASERIAL' and dom in dataBase.keys():
        if not dataBase[dom]["isSP"]:
            connection.close()
            return


        for validAddress in config[dom]['SS']:
            if address == validAddress['value']:

                data = dataBase[dom]["data"]
                lg = logFiles + dataBase[dom]["domainLog"]

                cEntrys = str(countEntrys(data))
                soaSerial = data[dom]['SOASERIAL'][0]['value']
                msg = f"{soaSerial};{cEntrys}"
                connection.sendall(msg.encode('utf-8'))
                connection.settimeout(10)
                msg = Utils.reciveMensageTCP(connection, lg, addressTup, "zone-transfer SP serial-number", mode)

                if (msg == cEntrys):
                    for line in sendDB(data):
                        connection.sendall(line.encode('utf-8'))

                    msg = Utils.reciveMensageTCP(connection, lg, addressTup, "zone-transfer SP confirmation", mode)
                    if msg != "ACK":
                        # algo correu mal a enviar as mensagens
                        Utils.writeInLogFiles(lg, f"EZ {address}:{port} SP", mode)
                        connection.close()
                        return

                # transferencia de zona executada com sucesso
                Utils.writeInLogFiles(lg, f"ZT {address}:{port} SP", mode)
                connection.close()
                return

        # dominio existe mas o pedido nao é valido
        Utils.writeInLogFiles(logFiles, f"EZ {address}:{port} SP", mode)
        connection.close()
        return

    # dominio nao existe
    Utils.writeInLogFiles(logFiles, f"EZ {address}:{port} SP", mode)
    connection.close()


class ZoneTransfer:
    isActive = True
    config = None
    dataBase = None
    logFiles = None
    mode = False

    def __init__(self, config, dataBase, logFiles, mode):
        self.config = config
        self.dataBase = dataBase
        self.logFiles = logFiles
        self.mode = mode

    def closeServer(self):
        self.isActive = False

    def zoneTransferResolver (self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.settimeout(1)

        try:
            address = Utils.get_ip()
            port = 6000
            soc.bind((address, port))
            (address, port) = soc.getsockname()
        except:
            print(f"Couldnt bind to localhost:6000")
            sys.exit()

        lg = []
        for dom in self.dataBase.keys():
            if self.dataBase[dom]["isSP"]:
                lg += self.dataBase[dom]["domainLog"]

        soc.listen()

        if self.mode:
            Utils.writeInLogFiles(lg + self.logFiles, f"ST {address} {port} debug", self.mode)
        else:
            Utils.writeInLogFiles(lg + self.logFiles, f"ST {address} {port} shy", self.mode)

        while self.isActive:
            try:
                connection, addressTup = soc.accept()
                threading.Thread(
                    target=processZT,
                    args=(connection, addressTup, self.config, self.dataBase, self.logFiles, self.mode),
                    daemon=True
                ).start()
            except:
                pass

        Utils.writeInLogFiles(lg + self.logFiles, f"SP {address} {port} zone-transfer close-request", self.mode)
        soc.close()

    @staticmethod
    def ZoneTransferRequest(address, serialNum, dom, logFiles, mode):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        try:
            s.connect((address, 6000))
        except:
            print(f"Couldnt bind to {address}:{6000}")
            return None

        msg=f"SOASERIAL;{dom}"
        s.sendall(msg.encode('utf-8'))

        msg=Utils.reciveMensageTCP(s, logFiles, (address, 6000), "zone-transfer SS acceptance-of-the-request", mode)
        if msg == None:
            s.close()
            return None
        else:
            msgAux = msg.split(';')

        if serialNum != int(msgAux[0]):
            s.sendall(str(msgAux[1]).encode('utf-8'))
            infoDataBase = []
            lines = int(msgAux[1])
            while len(infoDataBase) < lines:
                msg = Utils.reciveMensageTCP(s, logFiles, (address, 6000), "zone-transfer SS database-information", mode)
                if msg == None:
                    s.close()
                    return None
                for m in msg.split(';'):
                    if m != "":
                        infoDataBase.append(m)
        else:
            s.sendall("ACK".encode('utf-8'))
            return 0
        s.sendall("ACK".encode('utf-8'))
        s.close()
        return infoDataBase