import threading
import time
from Utilities.ResponseServer import ResponseServer
from Utilities.ZoneTransfer import ZoneTransfer
from Utilities.ReadFiles import ReadFiles
from Utilities.Utils import Utils


def startSPServer(configServer, domain, mode, logFiles):
    dataBaseFile = configServer[domain]['DB'][0]['value']
    dataBase = ReadFiles.readFileDataBase(dataBaseFile)

    if type(dataBase) == str:
        Utils.writeInLogFiles(logFiles, f"FL @ db-file-not-read {dataBase} {dataBaseFile} ", mode)
        exit(-1)

    Utils.writeInLogFiles(logFiles, f"EV @ db-file-read {dataBaseFile}", mode)
    
    return dataBase

def startSServer(configServer, domain, mode, logFiles, serialNumb = -1):
    spAddress = configServer[domain]['SP'][0]['value']
    dataBase = ReadFiles.getDataBaseSS(ZoneTransfer.ZoneTransferRequest(spAddress, serialNumb, domain, logFiles, mode))
    if dataBase == None:
        Utils.writeInLogFiles(logFiles, f"EZ {spAddress}:{6000} SS", mode)
    else:
        Utils.writeInLogFiles(logFiles, f"ZT {spAddress}:{6000} SS", mode)
    return dataBase


class Server:

    configFile = ""
    mode = False
    logFiles = []
    serverDataBase = {}
    configServer = None
    responseServer = None

    def __init__(self, configFile, mode):
        self.configFile = configFile
        self.mode = mode

    def testSS(self):
        timestamp = self.responseServer.cache.timestamp
        removeDomainList = []
        for domain in self.serverDataBase.keys():
            if (not self.serverDataBase[domain]["isSP"]) and timestamp >= self.serverDataBase[domain]["refresh"]:
                data = startSServer(
                    self.configServer,
                    domain,
                    self.mode,
                    self.serverDataBase[domain]["domainLog"] + self.logFiles,
                    self.serverDataBase[domain]["serialNum"]
                )
                if data == None and timestamp <= self.serverDataBase[domain]["expire"]:
                    self.responseServer.cache.loadDataBaseSS(self.serverDataBase[domain]["data"], self.serverDataBase[domain]["domainLog"] + self.logFiles)
                    self.serverDataBase[domain]["refresh"] += self.serverDataBase[domain]["data"][domain]["SOARETRY"][0]["value"]
                elif data == 0:
                    self.responseServer.cache.loadDataBaseSS(self.serverDataBase[domain]["data"], self.serverDataBase[domain]["domainLog"] + self.logFiles)
                    self.serverDataBase[domain]["refresh"] = timestamp + self.serverDataBase[domain]["data"][domain]["SOAREFRESH"][0]["value"]
                    self.serverDataBase[domain]["expire"] = timestamp + self.serverDataBase[domain]["data"][domain]["SOAEXPIRE"][0]["value"]
                elif type(data) == dict:
                    self.responseServer.cache.loadDataBaseSS(self.serverDataBase[domain]["data"], self.serverDataBase[domain]["domainLog"] + self.logFiles)
                    self.serverDataBase[domain]["data"] = data
                    self.serverDataBase[domain]["refresh"] = data[domain]["SOAREFRESH"][0]["value"] + timestamp
                    self.serverDataBase[domain]["expire"] = data[domain]["SOAEXPIRE"][0]["value"] + timestamp
                    self.serverDataBase[domain]["serialNum"] = data[domain]["SOASERIAL"][0]["value"]
                else:
                    removeDomainList.append(domain)

        for domain in removeDomainList:
            self.serverDataBase.pop(domain)
            print("Dominio retirado: ", domain)
            Utils.showTable(self.responseServer.cache.serverCache)


    def run(self):
        self.configServer = ReadFiles.readFileConfig(self.configFile)

        if self.configServer == None:
            print("ConfigFile cannot be interpreted")
            exit(-1)

        self.logFiles = self.configServer['all.']['LG']
        Utils.writeInLogFiles(self.logFiles, f"EV @ conf-file-read {self.configFile}", self.mode)
        
        hasPrimaryServer = False
        for domain in self.configServer.keys():
            if domain != 'all.' and domain != 'root.':
                domainKeys = self.configServer[domain].keys()
                if 'DD' in domainKeys and 'DB' in domainKeys and 'SP' not in domainKeys:
                    # servidor primario deste dominio
                    lg = []
                    if 'LG' in self.configServer[domain].keys():
                        lg = self.configServer[domain]['LG']
                    data = startSPServer(self.configServer, domain, self.mode, lg + self.logFiles)
                    self.serverDataBase[domain] = {
                        "data" : data,
                        "domainLog" : lg,
                        "isSP" : True
                    }
                    hasPrimaryServer = True

                elif 'DD' in domainKeys and 'SP' in domainKeys and 'DB' not in domainKeys and 'SS' not in domainKeys:
                    # servidor secundario deste dominio
                    lg = []
                    if 'LG' in self.configServer[domain].keys():
                        lg = self.configServer[domain]['LG']
                    data = startSServer(self.configServer, domain, self.mode, lg + self.logFiles)
                    if data == None:
                        exit(-1)
                    self.serverDataBase[domain] = {
                        "data" : data,
                        "domainLog" : lg,
                        "isSP" : False,
                        "refresh" : data[domain]["SOAREFRESH"][0]["value"],
                        "expire" : data[domain]["SOAEXPIRE"][0]["value"],
                        "serialNum" : data[domain]["SOASERIAL"][0]["value"]
                    }
                elif 'DD' in domainKeys and 'DB' not in domainKeys and 'SS' not in domainKeys and 'SP' not in domainKeys:
                    pass
                else:
                    Utils.writeInLogFiles(self.logFiles, f"FL @ parameters-inconsistency domain-'{domain}' {self.configFile} ", self.mode)
                    exit(-1)

                for dd in self.configServer[domain]['DD']:
                    if dd['value'] == "127.0.0.1" and len(self.configServer[domain]['DD']) != 1:
                        Utils.writeInLogFiles(self.logFiles, f"FL @ parameters-inconsistency domain-'{domain}' {self.configFile} ", self.mode)
                        exit(-1)

        if hasPrimaryServer:
            threading.Thread(
                target=ZoneTransfer.zoneTransferResolver,
                args=(self.configServer, self.serverDataBase, self.logFiles, self.mode),
                daemon=True
            ).start()

        self.responseServer = ResponseServer(self.configServer, self.serverDataBase, self.logFiles, self.mode)
        
        threading.Thread(
            target=self.responseServer.run,
            daemon=True
        ).start()

        while(True):
            time.sleep(1)
            self.testSS()
            self.responseServer.cache.incTimeStamp()
