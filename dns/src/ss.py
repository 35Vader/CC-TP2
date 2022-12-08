import socket
import parser
import sys
import threading
import utils
import query


def getDataBase(address, serialNum, dom):
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

    s.close()
    return parser.parserDataBaseSS(infoDataBase)
        




def main(configFile, mode):
    config = parser.parserConfig(configFile)

    logFiles = config['LG']
    dom = config['SP'][0]['domain']
    utils.writeInLogFiles(logFiles, f"EV {dom} conf-file-read {configFile}", dom, mode)

    dataBase = getDataBase(config['SP'][0]['value'], -1, dom)
    if dataBase == None:
        utils.writeInLogFiles(logFiles, f"EZ {config['SP'][0]['value']}:{6000} SS", dom, mode)
        exit(-1)
    else:
        utils.writeInLogFiles(logFiles, f"ZT {config['SP'][0]['value']}:{6000} SS", dom, mode)
    
    # query.querysResolver(dataBase, logFiles, dom, mode)

    #utils.showTable(config)
    utils.showTable(dataBase)
    #print(dataBase)
    #print(content)



if __name__ == "__main__":
    debug = False
    configFile = 'dns/dnsFiles/configSS.txt'
    if len(sys.argv) > 1:
        if sys.argv[1] != "-d":
            configFile = sys.argv[1]
            if len(sys.argv) > 2 and sys.argv[2] == "-d":
                debug = True
        else:
            debug = True
            if len(sys.argv) > 2 and sys.argv[2] != "-d":
                configFile = sys.argv[2]
    main(configFile, debug)

