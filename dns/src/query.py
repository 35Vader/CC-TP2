import socket
import utils


def decodeQuery(msgCod):
    msg = msgCod.decode('utf-8')
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


def getValues(type, dom, dataBase):
    rv = []
    names = []
    flag = False
    for entry in dataBase[type]:
        s = str(entry['name'])
        if dom == s or type == 'A':
            flag = True
            s += ' ' + type + ' '
            s += str(entry['value']) + ' '
            s += str(entry['ttl'])
            if int(entry['priority']) != 0:
                s += ' ' + str(entry['priority'])

            rv.append(s)

            if str(entry['value'])[-1] == '.':
                names.append(str(entry['value']))

    if flag and len(rv) > 0:
        return (rv,names)
    elif flag and len(rv) == 0:
        return ([],[])
    else:
        return (None,None)


def getExtra(listNames, type, dataBase):
    if type == 'A':
        return []
    rv = []
    for entry in dataBase['A']:
        s = str(entry['name'])
        if s in listNames:
            s += ' ' + 'A' + ' '
            s += str(entry['value']) + ' '
            s += str(entry['ttl'])
            if int(entry['priority']) != 0:
                s += ' ' + str(entry['priority'])

            rv.append(s)
    return rv




def processQuery(msgCod, add, dataBase, logFiles, mode):
    
    try:
        dic = decodeQuery(msgCod)
    except:
        dic['RESPONSE_CODE'] = 3

    if dic['QUERY_INFO_TYPE'] in dataBase.keys():
        (rv, namesR) = getValues(dic['QUERY_INFO_TYPE'], dic['QUERY_INFO_NAME'], dataBase)
        if rv == None:
             dic['RESPONSE_CODE'] = 2
        elif rv == []:
            dic['RESPONSE_CODE'] = 1
        else:
            dic['RESPONSE_VALUES'] = rv
            dic['N_VALUES'] = len(rv)

            (av, namesA) = getValues('NS', dic['QUERY_INFO_NAME'], dataBase)
            dic['AUTHORITIES_VALUES'] = av
            dic['N_AUTHORITIES'] = len(av)

            ex = getExtra(namesA + namesR, dic['QUERY_INFO_TYPE'], dataBase)
            dic['EXTRA_VALUES'] = ex
            dic['N_EXTRA_VALUES'] = len(ex)

    else:
        dic['RESPONSE_CODE'] = 1
    
    compactQuery(encodeQuery(dic).decode('utf-8'))
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(encodeQuery(dic), add)


def compactQuery(msg):
    m = msg[:-1].split(';')
    print(m[0] + ';' + m[1] + ';')
    if len(m) == 5:
        for m2 in m[2].split(','):
            print(f"{m2},")
        for m3 in m[3].split(','):
            print(f"{m3},")
        for m4 in m[4].split(','):
            print(f"{m4},")
    if len(m) == 4:
        for m2 in m[2].split(','):
            print(f"{m2},")
        for m3 in m[3].split(','):
            print(f"{m3},")
