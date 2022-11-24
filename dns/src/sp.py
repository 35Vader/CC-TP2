import socket
import sys 
import threading
import utils
import parser
import query

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

def processZT (connection:socket.socket, addressTup, config, dataBase, logFiles, dom, mode):
    (address, port) = addressTup
    for entry in config['SS']:
        if address == entry['value']:
            msg = utils.reciveMensageTCP(connection)
            msgAux = msg.split(';')

            if msgAux[0] == 'SOASERIAL' and msgAux[1] == dom:
                c = str(countEntrys(dataBase))
                msg = f"{dataBase['SOASERIAL'][0]['value']};{c}"
                connection.sendall(msg.encode('utf-8'))

                msg = utils.reciveMensageTCP(connection)
                if (msg == c):
                    for line in sendDB(dataBase):
                        connection.sendall(line.encode('utf-8'))
                        msg = utils.reciveMensageTCP(connection)
                        if msg != "ACK":
                            utils.writeInLogFiles(logFiles, f"EZ {address}:{port} SP", dom, mode)
                            connection.close()
                            return
                
                utils.writeInLogFiles(logFiles, f"ZT {address}:{port} SP", dom, mode)
                connection.close()
                return

    utils.writeInLogFiles(logFiles, f"EZ {address}:{port} SP", dom, mode)
    connection.close()

def getSP(dataBase):
    sp = dataBase['SOASP'][0]['value']
    for a in dataBase['A']:
        if a['name'] == sp:
            endereco = a['value']
    return endereco

def zoneTransferResolver (config, dataBase, logFiles, dom, mode):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    endereco = getSP(dataBase)
    port = 6000
    s.bind((endereco, port))

    s.listen()
    utils.writeInLogFiles(logFiles, f"ST {endereco} {port}", dom, mode)

    while True:
        connection, addressTup = s.accept()
        threading.Thread(target=processZT,args=(connection, addressTup, config, dataBase, logFiles, dom, mode)).start()

    s.close()

def querysResolver (dataBase, logFiles, dom, mode):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    endereco = getSP(dataBase)
    port = 3000

    s.bind((endereco, port))
    utils.writeInLogFiles(logFiles, f"ST {endereco} {port}", dom, mode)

    while True:
        msg, add = s.recvfrom(1024)
        threading.Thread(target=(query.processQuery),args=(msg, add, dataBase, logFiles, mode)).start()
    s.close()


def main(configFile, mode):
    config = parser.parserConfig(configFile)

    logFiles = config['LG']
    dom = config['DB'][0]['domain']
    utils.writeInLogFiles(logFiles, f"EV {dom} conf-file-read {configFile}", dom, mode)

    dataBaseFile = config['DB'][0]['value']
    dataBase = parser.parserDataBaseSP(dataBaseFile)
    utils.writeInLogFiles(logFiles, f"EV {dom} db-file-read {dataBaseFile}", dom, mode)

    
    threading.Thread(target=zoneTransferResolver,args=(config, dataBase, logFiles, dom, mode)).start()

    threading.Thread(target=querysResolver,args=(dataBase, logFiles, dom, mode)).start()

    #utils.writeInLogFiles(logFiles, ["log1","log2","log3"], 'cc.tp.', mode)
    #utils.showTable(config)
    #utils.showTable(dataBase)
    #print(dataBase)
    #print(content)



if __name__ == "__main__":
    if len(sys.argv) > 1:
        configFile = sys.argv[1]
    else:
        configFile = 'dns/dnsFiles/configSP.txt'
    main(configFile, True)





