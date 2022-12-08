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

def showTable(d:dict):
    for dom in d.keys():
        s = printL(dom,25) 
        for type in dict(d[dom]).keys():
            s2 = printL(type,12)
            for listval in d[dom][type]:
                s3 = ""
                for n in listval.values():
                    s3 += printL(n,25)
                print(s + s2 + s3)

def reciveMensageTCP(socket:socket.socket):
    msg = socket.recv(2048)
    if not msg:
        return None
    else:
        ms = msg.decode('utf-8')
        return ms

def writeInLogFiles (logFiles, msg, dom, mode):
    nextlog = ""
    for filePath in logFiles:
        domain = filePath['domain']
        if domain == dom or domain == 'all.':
            try:
                f = open(filePath['value'], "x")
                nextlog = nextlog + f"EV {dom} log-file-create {filePath['value']}"
            except:
                f = open(filePath['value'], "a")
            if type(msg) is list:
                for msgAux in msg:
                    f.write(f"{str(datetime.datetime.now())[:-3]} {msgAux}\n")
                    if domain !='all.' and mode:
                        print(f"{str(datetime.datetime.now())[:-3]} {msgAux}")
            else:
                f.write(f"{str(datetime.datetime.now())[:-3]} {msg}\n")
                if domain !='all.' and mode:
                    print(f"{str(datetime.datetime.now())[:-3]} {msg}")
            
            if domain !='all.' and nextlog != "":
                f.write(f"{str(datetime.datetime.now())[:-3]} {nextlog}\n")
                if mode:
                    print(f"{str(datetime.datetime.now())[:-3]} {nextlog}")

            f.close()



