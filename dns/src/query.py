import socket
import sys
import threading
import utils


def compactQuery(mensagem):
    msg = mensagem[:-1].split(';')
    print(msg[0] + ';' + msg[1] + ';')
    m0 = msg[0].split(',')
    if int(m0[3]) > 0:
        for m2 in msg[2].split(','):
            print(f"{m2},")
    if int(m0[4]) > 0:
        for m3 in msg[3].split(','):
            print(f"{m3},")
    if int(m0[5]) > 0:
        for m4 in msg[4].split(','):
            print(f"{m4},")

def printQuery(mensagem):
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

    if int(m0[3]) > 0:
        for m2 in msg[2].split(','):
            s += f"RESPONSE-VALUES = {m2},\n"
        s = s[:-2] + ';\n'
    if int(m0[4]) > 0:
        for m3 in msg[3].split(','):
            s += f"AUTHORITIES-VALUES = {m3},\n"
        s = s[:-2] + ';\n'
    if int(m0[5]) > 0:
        for m4 in msg[4].split(','):
            s += f"EXTRA-VALUES = {m4},\n"
        s = s[:-2] + ';\n'
    print(s + "---------------------------------------------------------\n")


def decodeQuery(connection):
    msg = connection.decode('utf-8')
    input_divided = []
    for m in msg.split(';')[:-1]:
        input_divided += m.split(',')


    dic = {}
    dic['MESSAGE_ID'] = input_divided[0]
    dic['FLAGS'] = input_divided[1]
    dic['RESPONSE_CODE'] = int(input_divided[2])
    dic['N_VALUES'] = int(input_divided[3])
    dic['N_AUTHORITIES'] = int(input_divided[4])
    dic['N_EXTRA_VALUES'] = int(input_divided[5])
    dic['QUERY_INFO_NAME'] = input_divided[6]
    dic['QUERY_INFO_TYPE'] = input_divided[7]

    return dic

def encodeQuery(dic):
    s = dic['MESSAGE_ID'] + ','
    s += dic['FLAGS'] + ','
    s += str(dic['RESPONSE_CODE']) + ','
    s += str(dic['N_VALUES']) + ','
    s += str(dic['N_AUTHORITIES']) + ','
    s += str(dic['N_EXTRA_VALUES']) + ';'
    s += dic['QUERY_INFO_NAME'] + ','
    s += dic['QUERY_INFO_TYPE'] + ';'
    
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
    
    return s.encode('utf-8')


def getValues(typeQ, domain, dataBase):
    rv = []
    names = []
    for entry in dataBase[domain][typeQ]:
        s = domain + ' '
        s += typeQ + ' '
        s += str(entry['value']) + ' '
        s += str(entry['ttl'])
        if int(entry['priority']) != 0:
            s += ' ' + str(entry['priority'])

        rv.append(s)

        if str(entry['value'])[-1] == '.':
            names.append(str(entry['value']))

    return (rv,names)

def getAuthorities(domain, dataBase):
    av = []
    names = []
    for dom in dataBase.keys():
        if (domain == "" or domain == dom) and 'NS' in dataBase[dom].keys():
            for entry in dataBase[dom]['NS']:
                s = dom + ' NS '
                s += str(entry['value']) + ' '
                s += str(entry['ttl'])
                if int(entry['priority']) != 0:
                    s += ' ' + str(entry['priority'])

                av.append(s)

                if str(entry['value'])[-1] == '.':
                    names.append(str(entry['value']))

    return (av,names)

def getExtra(namesA, namesR, type, domain, dataBase):
    if type == 'A':
        listNames = namesA
        try:
            listNames.remove(domain)
        except:
            pass
    else:
        listNames = namesA + namesR

    rv = []
    for dom in dataBase.keys():
        if dom in listNames and 'A' in dataBase[dom].keys():
            for entry in dataBase[dom]['A']:
                s = dom + ' A '
                s += str(entry['value']) + ' '
                s += str(entry['ttl'])
                if int(entry['priority']) != 0:
                    s += ' ' + str(entry['priority'])
                rv.append(s)
    return rv




def processQuery(connection, addressTup, dataBase, logFiles, mode):
    
    try:
        dic = decodeQuery(connection)
    except:
        dic['RESPONSE_CODE'] = 3
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(encodeQuery(dic), addressTup)
        s.close()
        return
    
    domain = dic['QUERY_INFO_NAME']
    typeQ = dic['QUERY_INFO_TYPE']
    if typeQ in ['A', 'CNAME']:
        domAuth = '.'.join(domain.split('.')[1:])
    else:
        domAuth = domain
    namesR = []
    if domain in dataBase.keys():
        if typeQ in dataBase[domain].keys():
            (rv, namesR) = getValues(typeQ, domain, dataBase)
            dic['RESPONSE_VALUES'] = rv
            dic['N_VALUES'] = len(rv)
        else:
            dic['RESPONSE_CODE'] = 1

        (av, namesA) = getAuthorities(domAuth, dataBase)
        dic['AUTHORITIES_VALUES'] = av
        dic['N_AUTHORITIES'] = len(av)

    else:
        dic['RESPONSE_CODE'] = 2
        (av, namesA) = getAuthorities("", dataBase)
        dic['AUTHORITIES_VALUES'] = av
        dic['N_AUTHORITIES'] = len(av)

    ex = getExtra(namesA, namesR, typeQ, domain, dataBase)
    dic['EXTRA_VALUES'] = ex
    dic['N_EXTRA_VALUES'] = len(ex)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(encodeQuery(dic), addressTup)
    s.close()


def querysResolver (dataBase, logFiles, mode):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.bind(('', 3000))
        (address, port) = s.getsockname()
    except:
        print(f"Couldnt bind to {address}:{port}")
        sys.exit()

    if mode:
        utils.writeInLogFiles(logFiles, f"ST {address} {port} debug", mode)
    else:
        utils.writeInLogFiles(logFiles, f"ST {address} {port} shy", mode)

    while True:
        connection, addressTup = s.recvfrom(1024)
        threading.Thread(target=(processQuery),args=(connection, addressTup, dataBase, logFiles, mode)).start()

    s.close()
