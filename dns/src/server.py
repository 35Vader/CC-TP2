import threading
import zoneTransfer
import sys
import readFiles
import query
import utils





def startSServer(configServer, domain, mode, logFiles):
    spAddress = configServer[domain]['SP'][0]['value']
    dataBase = readFiles.getDataBaseSS(zoneTransfer.zoneTransferRequest(spAddress, -1, domain))
    if dataBase == None:
        utils.writeInLogFiles(logFiles, f"EZ {spAddress}:{6000} SS", mode)
        exit(-1)
    
    utils.writeInLogFiles(logFiles, f"ZT {spAddress}:{6000} SS", mode)
    utils.showTable(dataBase)
    query.querysResolver(dataBase, logFiles, mode)




def startSPServer(configServer, domain, mode, logFiles):
    dataBaseFile = configServer[domain]['DB'][0]['value']
    dataBase = readFiles.readFileDataBaseSP(dataBaseFile)

    if type(dataBase) == str:
        utils.writeInLogFiles(logFiles, f"FL @ db-file-not-read {dataBase} {dataBaseFile} ", mode)
        exit(-1)

    utils.writeInLogFiles(logFiles, f"EV @ db-file-read {dataBaseFile}", mode)
    threading.Thread(target=zoneTransfer.zoneTransferResolver,args=(configServer, dataBase, logFiles, mode)).start()

    query.querysResolver(dataBase, logFiles, mode)





def main(configFile, mode):

    configServer = readFiles.readFileConfig(configFile)

    if configServer == None:
        print("ConfigFile cannot be interpreted")
        exit(-1)

    logFiles = configServer['all.']['LG']
    utils.writeInLogFiles(logFiles, f"EV @ conf-file-read {configFile}", mode)

    for domain in configServer.keys():
        if domain != 'all.' and domain != 'root.':
            domainKeys = configServer[domain].keys()
            if 'DB' in domainKeys and 'SP' not in domainKeys:
                # servidor primario deste dominio
                startSPServer(configServer, domain, mode, logFiles + configServer[domain]['LG'])

            elif 'SP' in domainKeys and 'DB' not in domainKeys and 'SS' not in domainKeys:
                # servidor secundario deste dominio
                startSServer(configServer, domain, mode, logFiles + configServer[domain]['LG'])

            else:
                utils.writeInLogFiles(logFiles, f"FL @ parameters-inconsistency domain-'{domain}' {configFile} ", mode)
                exit(-1)


if __name__ == "__main__":
    debug = False
    configFile = 'dns/dnsFiles/'
    if len(sys.argv) > 1:
        if sys.argv[1] != "-d":
            configFile += sys.argv[1]
            if len(sys.argv) > 2 and sys.argv[2] == "-d":
                debug = True
            main(configFile, debug)
        else:
            debug = True
            if len(sys.argv) > 2 and sys.argv[2] != "-d":
                configFile += sys.argv[2]
                main(configFile, debug)
            else:
                print('Few arguments provided')
    else:
        print('Few arguments provided')

