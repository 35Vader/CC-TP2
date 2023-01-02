import socket
import sys
import threading

from Utilities.Utils import Utils
from Utilities.Cache import Cache
from Utilities.ReadFiles import ReadFiles


def getServers(dic, domain = None):
    listAuth = []
    listAddress = []
    for a in dic['AUTHORITIES_VALUES']:
        auth = a.split(' ')
        if domain == None or str(domain).endswith(auth[0]):
            listAuth.append(auth[2])

    for e in dic['EXTRA_VALUES']:
        extra = e.split(' ')
        if extra[0] in listAuth:
            listAddress.append(extra[2])

    return listAddress

def cleanList(mainL, dropL):
    r = []
    for elem in mainL:
        if elem not in dropL:
            r.append(elem)
    return r

class ResponseServer:

    cache = None
    mode = False
    st = []
    configSR = {}


    def __init__(self, configServer, serverDataBase, logFiles, mode):
        self.mode = mode
        self.cache = Cache(serverDataBase, logFiles, mode)

        if 'root.' in configServer:
            self.st = ReadFiles.readFileRootServers(configServer['root.']['ST'][0]['value'])

        for domain in configServer:
            lg = []
            if 'DD' in configServer[domain] and domain != 'all.' and domain != 'root.':
                if 'LG' in configServer[domain]:
                    lg += configServer[domain]['LG']
                self.configSR[domain] = configServer[domain]['DD']


    def handleQuery(self, connection, addressTup):
        try:
            msg = connection.decode('utf-8')
            dic = Utils.decodeQuery(msg)
            Utils.writeInLogFiles(self.cache.logFiles, f"QR {addressTup[0]}:3000\n{msg}", self.mode)
        except:
            Utils.writeInLogFiles(self.cache.logFiles, f"ER {addressTup[0]}:3000 message-cannot-be-decoded unknown-format", self.mode)
            return
        logs = None

# recursivo
        if 'R' in dic['FLAGS'] and 'Q' in dic['FLAGS']:
            if 'A' in dic['FLAGS']:
                dic['FLAGS'].remove('A')
            res = Utils.decodeQuery(Utils.encodeQuery(dic))
            (res, logs, a) = self.cache.processQuery(res)
            if a == 0 or a == 2:
                res['FLAGS'].append('A')
            listServer = []
            con = None
            clientS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            serverS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            serverS.settimeout(0.5)

            if res['RESPONSE_CODE'] == 3:
                Utils.writeInLogFiles(logs, f"ER {addressTup[0]}:3000 error-formulating-answer parameters-inconsistency", self.mode)
                return
            elif res['RESPONSE_CODE'] == 2:
                domain = dic['QUERY_INFO_NAME']
                for dom in self.configSR:
                    if str(domain).endswith(dom):
                        for i in self.configSR[dom]:
                            if i['value'] == "127.0.0.1":
                                listServer = self.st
                                break
                            listServer.append(i['value'])
                    else:
                        listServer = self.st
                if listServer == []:
                    listServer = getServers(res, domain)
            elif res['RESPONSE_CODE'] == 1:
                listServer = getServers(res)
            for server in listServer:
                try:
                    serverS.sendto(Utils.encodeQuery(dic).encode('utf-8'), (server,3000))
                    Utils.writeInLogFiles(logs, f"QE {server}:3000\n{Utils.encodeQuery(dic)}", self.mode)
                    con, add = serverS.recvfrom(1024)
                    Utils.writeInLogFiles(logs, f"RR {add[0]}:{add[1]}\n{con.decode('utf-8')}", self.mode)
                    break
                except socket.timeout:
                    pass
                except:
                    pass

            if con == None:
                res['FLAGS'].remove('Q')
                con = Utils.encodeQuery(res).encode('utf-8')

            clientS.sendto(con, addressTup)
            Utils.writeInLogFiles(logs, f"RP {addressTup[0]}:{addressTup[1]}\n{con.decode('utf-8')}", self.mode)
            if a == 0 or a == 1:
                self.cache.loadNewQuery(Utils.decodeQuery(con.decode('utf-8')))
            clientS.close()
            serverS.close()
            return

# iterativo
        elif 'A' in dic['FLAGS'] and 'Q' in dic['FLAGS']:
            print("me2")
            dic['FLAGS'].remove('A')
            domain = dic['QUERY_INFO_NAME']
            res = Utils.decodeQuery(Utils.encodeQuery(dic))
            (res, logs, a) = self.cache.processQuery(res)
            if a == 0 or a == 2:
                res['FLAGS'].append('A')
            listServer = []
            it = 1
            serverS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            serverS.settimeout(0.5)
            if res['RESPONSE_CODE'] == 3:
                Utils.writeInLogFiles(logs, f"ER {addressTup[0]}:{addressTup[1]} error-formulating-answer parameters-inconsistency", self.mode)
                return

            while True:
                if res['RESPONSE_CODE'] == 0:
                    break

                if res['RESPONSE_CODE'] == 2:
                    if it == 1:
                        for dom in self.configSR:
                            if str(domain).endswith(dom):
                                for i in self.configSR[dom]:
                                    if i['value'] == "127.0.0.1":
                                        listServer = self.st
                                        it += 1
                                        break
                                    listServer.append(i['value'])
                                break
                        if listServer == []:
                            listServer = self.st
                            it += 1
                    elif it <= 2:
                        listServer = self.st
                    else:
                        listServerAux = getServers(res, domain)
                        if listServerAux == listServer:
                            break
                        else:
                            listServer = cleanList(listServerAux, listServer)
                elif res['RESPONSE_CODE'] == 1:
                    listServer = getServers(res, domain)

                it += 1
                hasNewResponse = False
                for server in listServer:
                    try:
                        serverS.sendto(Utils.encodeQuery(dic).encode('utf-8'), (server,3000))
                        Utils.writeInLogFiles(logs, f"QE {server}:3000\n{Utils.encodeQuery(dic)}", self.mode)
                        con, add = serverS.recvfrom(1024)
                        res = Utils.decodeQuery(con.decode('utf-8'))
                        hasNewResponse = True
                        Utils.writeInLogFiles(logs, f"RR {add[0]}:{add[1]}\n{con.decode('utf-8')}", self.mode)
                        break
                    except socket.timeout:
                        Utils.writeInLogFiles(logs, f"TO {server}:3000 query", self.mode)
                        pass
                    except:
                        pass
                if not hasNewResponse:
                    break

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(Utils.encodeQuery(res).encode('utf-8'), addressTup)
            if a == 0 or a == 1:
                self.cache.loadNewQuery(res)
            if logs == None:
                Utils.writeInLogFiles(self.cache.logFiles, f"RP {addressTup[0]}:{addressTup[1]}\n{Utils.encodeQuery(res)}", self.mode)
            else:
                Utils.writeInLogFiles(logs, f"RP {addressTup[0]}:{addressTup[1]}\n{Utils.encodeQuery(res)}", self.mode)
            s.close()
            return

# resposta apenas
        elif 'Q' in dic['FLAGS']:
            dic['FLAGS'].remove('Q')
            (dic, logs, a) = self.cache.processQuery(dic)
            if a == 0 or a == 2:
                dic['FLAGS'].append('A')
            if dic['RESPONSE_CODE'] == 3:
                Utils.writeInLogFiles(logs, f"ER {addressTup[0]}:{addressTup[1]} error-formulating-answer parameters-inconsistency", self.mode)
                return

            if logs == None:
                Utils.writeInLogFiles(self.cache.logFiles, f"RP {addressTup[0]}:{addressTup[1]}\n{Utils.encodeQuery(dic)}", self.mode)
            else:
                Utils.writeInLogFiles(logs, f"RP {addressTup[0]}:{addressTup[1]}\n{Utils.encodeQuery(dic)}", self.mode)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(Utils.encodeQuery(dic).encode('utf-8'), addressTup)
            s.close()

    def run(self):

        threading.Thread(
            target=self.cache.debug,
            daemon=True
        ).start()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            address = Utils.get_ip()
            port = 3000
            s.bind((address, port))
        except:
            print(f"Couldnt bind")
            sys.exit()

        if self.mode:
            Utils.writeInLogFiles(self.cache.allLog, f"ST {address}:{port} debug", self.mode)
        else:
            Utils.writeInLogFiles(self.cache.allLog, f"ST {address}:{port} shy", self.mode)

        while True:
            connection, addressTup = s.recvfrom(1024)
            threading.Thread(
                target=(self.handleQuery),
                args=(connection, addressTup),
                daemon=True
            ).start()

        s.close()