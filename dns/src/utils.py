import socket
import datetime


def printL (text,lenght):
    if isinstance(text, str):
        t = "'" + str(text) + "'"
    else:
        t = str(text)
    aux = lenght-len(t)
    if aux%2 == 0:
        aux2 = int(aux/2)
        return ' '*aux2 + t + ' '*aux2 + '|'
    else:
        aux2 = int(aux/2)
        return ' '*aux2 + t + ' '*aux2 + ' |'

def printL2 (text,lenght,b):
    t = "[" + str(text).split('/')[-1] + "]"
    return t + ' '*(lenght-len(t)) + '|'

def showTable(d:dict):
    for dom in d.keys():
        s = printL(dom,25) 
        for type in dict(d[dom]).keys():
            s2 = printL(type,12)
            for listval in d[dom][type]:
                s3 = ""
                for n in listval.values():
                    s3 += printL(n,22)
                print(s + s2 + s3)

def reciveMensageTCP(socket:socket.socket):
    msg = socket.recv(2048)
    if not msg:
        return None
    else:
        ms = msg.decode('utf-8')
        return ms

def writeInLogFiles (logFiles, msg, mode):
    nextlog = []

    for file in logFiles:
        filePath = file['value']
        try:
            f = open(filePath, "x")
            nextlog.append(f"EV @ log-file-create {filePath}")
        except:
            f = open(filePath, "a")

        f.write(f"{str(datetime.datetime.now())[:-3]} {msg}\n")
        if mode:

            print(f"{printL2(filePath,15,True)} {str(datetime.datetime.now())[:-3]} {msg}")
        
        for log in nextlog:
            f.write(f"{str(datetime.datetime.now())[:-3]} {log}\n")
            if mode:
                print(f"{printL2(filePath,15,True)} {str(datetime.datetime.now())[:-3]} {log}")

        f.close()

