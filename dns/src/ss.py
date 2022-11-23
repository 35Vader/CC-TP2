import socket
import parser
import sys
import utils

def getDataBase(sp,serialNum):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((sp['value'], 6000))
    print(f"Estou conectado a {sp['value']}:{6000}")

    msg=f"SOASERIAL;{sp['domain']}."
    s.sendall(msg.encode('utf-8'))

    msgAux=utils.reciveMensage(s).split(';')

    if serialNum != int(msgAux[0]):
        
        s.sendall(str(msgAux[1]).encode('utf-8'))
        infoDataBase=[]
        for i in range(0,int(msgAux[1])):
            msg = utils.reciveMensage(s)
            infoDataBase.append(msg)
            s.sendall("ACK".encode('utf-8'))

    s.close()
    return parser.parserDataBaseSS(infoDataBase)
        




def main(configFile):
    config = parser.parserConfig(configFile)
    dataBase = getDataBase(config['SP'][0], -1)
    

    #utils.showTable(config)
    utils.showTable(dataBase)
    #print(dataBase)
    #print(content)



if __name__ == "__main__":
    if len(sys.argv) > 1:
        configFile = sys.argv[1]
    else:
        configFile = 'dns/dnsFiles/configSS.txt'
    main(configFile)

