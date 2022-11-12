#import sys
#sys.path.append("src/utils")
#from utils import showTable
from utils import showTable

def parser(s):
    f = open(s, "r")
    doc = f.read()
    f.close()

    content = []

    for line in doc.split("\n"):
        text = line.split("#")[0].split(" ")
        if len(text) >= 3:
            content.append(text)
    return content


def parserDataBase(s):
    content = parser(s)

    dAt = content[0][2]
    dTTL = int(content[1][2])
    dataBase = {}


    for op in content[2:]:
        par = str(op[0]).replace("@",dAt)
        if par[-1] != ".":
            par = par + "." + dAt

        type = str(op[1])
        value = str(op[2])
        if type == "CNAME" and value[-1] != ".":
            value = value + "." + dAt
        ttl = 0
        priority = 0

        if len(op) > 3:
            if op[3] == "TTL": ttl = dTTL 

            if len(op) > 4: priority = int(op[4])

        if type in dataBase:
            dataBase[type].append({"name":par,"value":value,"ttl":ttl,"priority":priority})
        else:
            dataBase[type]= [{"name":par,"value":value,"ttl":ttl,"priority":priority}]

    return dataBase


def parserConfig(s):
    content = parser(s)
    config = {}

    for op in content:
        dom = str(op[0])
        type = str(op[1])
        if type in ["SS", "SP", "DD"]:
            aux = str(op[2]).split(':')
            value = aux[0]
            if len(aux) == 2:
                port = int(aux[1])
            else:
                port = -1
        else:
            value = str(op[2])
        
        if type in config:
            if type in ["SS", "SP", "DD"]: config[type].append({"domain":dom,"value":value,"port":port})
            else: config[type].append({"domain":dom,"value":value})
        else:
            if type in ["SS", "SP", "DD"]: config[type] = [{"domain":dom,"value":value,"port":port}]
            else: config[type] = [{"domain":dom,"value":value}]
    
    return config







config = parserConfig("src/dnsFiles/config.txt")
dataBase = parserDataBase("src/dnsFiles/DataBase.txt")

showTable(config)
#showTable(dataBase)


