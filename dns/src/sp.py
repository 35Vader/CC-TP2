from parser import *



configFile = ""#input()
if configFile == "":
    configFile = "dns/dnsFiles/config.txt"

config = parserConfig(configFile)
dataBase = parserDataBase(config['DB'][0]['value'])

showTable(config)
showTable(dataBase)