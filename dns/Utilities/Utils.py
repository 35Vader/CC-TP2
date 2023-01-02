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


class Utils:
    @staticmethod
    def showTable(d:dict):
        for dom in d.keys():
            sDom = printL(dom,18) 
            for typeQ in dict(d[dom]).keys():
                sType = printL(typeQ,12)
                try:
                    for listval in d[dom][typeQ]:
                        s3 = ""
                        for n in listval.values():
                            s3 += printL(n,20)
                        print(sDom + sType + s3)
                except:
                    s3 =  '|' + sDom + sType
                    s3 += printL(d[dom][typeQ]['RESPONSE_CODE'],5)
                    s3 += printL(d[dom][typeQ]['timestamp'],7) + "\n|"
                    s3 += printL(d[dom][typeQ]['N_VALUES'],5)
                    s3 += str(d[dom][typeQ]['RESPONSE_VALUES']) + "\n|"
                    s3 += printL(d[dom][typeQ]['N_EXTRA_VALUES'],5)
                    s3 += str(d[dom][typeQ]['AUTHORITIES_VALUES']) + "\n|"
                    s3 += printL(d[dom][typeQ]['N_AUTHORITIES'],5)
                    s3 += str(d[dom][typeQ]['EXTRA_VALUES']) + "\n"
                    print(s3)

    @staticmethod
    def reciveMensageTCP(soc:socket.socket, logs, address, errorStr, mode):
        try:
            msg = soc.recv(2048)
            if not msg:
                return None
            else:
                ms = msg.decode('utf-8')
                return ms
        except socket.timeout:
            Utils.writeInLogFiles(logs, f"TO {address[0]}:{address[1]} {errorStr}", mode)
                    
    @staticmethod
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

                print(f"{printL2(filePath,15,True)} {str(datetime.datetime.now())[:-3]} {msg}\n")
            
            for log in nextlog:
                f.write(f"{str(datetime.datetime.now())[:-3]} {log}\n")
                if mode:
                    print(f"{printL2(filePath,15,True)} {str(datetime.datetime.now())[:-3]} {log}\n")

            f.close()

    @staticmethod
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
        s.settimeout(0)    
        try:    
            # doesn't even have to be reachable    
            s.connect(('254.254.254.254', 1))                                       
            IP = s.getsockname()[0]                                                
        except Exception:                                                          
            IP = '127.0.0.1'                                                       
        finally:                                                                   
            s.close()                                                              
        return IP

    @staticmethod
    def compactQuery(mensagem):
        msg = mensagem[:-1].split(';')
        print(msg[0] + ';' + msg[1] + ';')
        m0 = msg[0].split(',')
        i = 2
        if int(m0[3]) > 0:
            print(str(msg[i]).replace(',',',\n') + ';')
            i+=1
        if int(m0[4]) > 0:
            print(str(msg[i]).replace(',',',\n') + ';')
            i+=1
        if int(m0[5]) > 0:
            print(str(msg[i]).replace(',',',\n') + ';')

    @staticmethod
    def printQuery(mensagem):
        if type(mensagem) != str:
            mensagem = Utils.encodeQuery(mensagem)
        msg = mensagem[:-1].split(';')
        s = ""

        m0 = msg[0].split(',')
        m1 = msg[1].split(',')

        s += "\n---------------------------------------------------------\n# Header\n"
        s += f"MESSAGE-ID = {m0[0]}, FLAGS = {m0[1]}, RESPONSE-CODE = {m0[2]},\n"
        s += f"N-VALUES = {m0[3]}, N-AUTHORITIES = {m0[4]}, N-EXTRA-VALUES = {m0[5]};\n"
        s += f"# Data: Query Info\n"
        s += f"QUERY-INFO.NAME = {m1[0]}, QUERY-INFO.TYPE = {m1[1]};\n"
        s += f"# Data: List of Response, Authorities and Extra Values\n"

        i = 2
        if int(m0[3]) > 0:
            for m2 in msg[i].split(','):
                s += f"RESPONSE-VALUES = {m2},\n"
            s = s[:-2] + ';\n'
            i += 1
        if int(m0[4]) > 0:
            for m3 in msg[i].split(','):
                s += f"AUTHORITIES-VALUES = {m3},\n"
            s = s[:-2] + ';\n'
            i += 1
        if int(m0[5]) > 0:
            for m4 in msg[i].split(','):
                s += f"EXTRA-VALUES = {m4},\n"
            s = s[:-2] + ';\n'
        print(s + "---------------------------------------------------------\n")

    @staticmethod
    def decodeQuery(msg):
        input_divided = []
        for m in msg.split(';')[:-1]:
            input_divided.append(m.split(','))


        dic = {}
        dic['MESSAGE_ID'] = int(input_divided[0][0])
        dic['FLAGS'] = str(input_divided[0][1]).split('+')
        dic['RESPONSE_CODE'] = int(input_divided[0][2])
        dic['N_VALUES'] = int(input_divided[0][3])
        dic['N_AUTHORITIES'] = int(input_divided[0][4])
        dic['N_EXTRA_VALUES'] = int(input_divided[0][5])
        dic['QUERY_INFO_NAME'] = input_divided[1][0]
        dic['QUERY_INFO_TYPE'] = input_divided[1][1]
        
        dic['RESPONSE_VALUES'] = []
        dic['AUTHORITIES_VALUES'] = []
        dic['EXTRA_VALUES'] = []

        i = 2
        if dic['N_VALUES'] > 0:
            for entry in input_divided[i]:
                dic['RESPONSE_VALUES'] += [entry]
            i += 1
        if dic['N_AUTHORITIES'] > 0:
            for entry in input_divided[i]:
                dic['AUTHORITIES_VALUES'] += [entry]
            i += 1
        if dic['N_EXTRA_VALUES'] > 0:
            for entry in input_divided[i]:
                dic['EXTRA_VALUES'] += [entry]
            i += 1

        return dic

    @staticmethod
    def encodeQuery(dic):
        s = str(dic['MESSAGE_ID']) + ','
        s += str('+'.join(dic['FLAGS'])) + ','
        s += str(dic['RESPONSE_CODE']) + ','
        s += str(dic['N_VALUES']) + ','
        s += str(dic['N_AUTHORITIES']) + ','
        s += str(dic['N_EXTRA_VALUES']) + ';'
        s += str(dic['QUERY_INFO_NAME']) + ','
        s += str(dic['QUERY_INFO_TYPE']) + ';'
        
        if dic['N_VALUES'] > 0: 
            for msg in dic['RESPONSE_VALUES']:
                s += msg + ','
        s = s[:-1] + ';'
        
        if dic['N_AUTHORITIES'] > 0: 
            for msg in dic['AUTHORITIES_VALUES']:
                s += msg + ','
        s = s[:-1] + ';'
        
        if dic['N_EXTRA_VALUES'] > 0: 
            for msg in dic['EXTRA_VALUES']:
                s += msg + ','
        s = s[:-1] + ';'
        
        return s
