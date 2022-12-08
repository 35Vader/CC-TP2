import utils

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


def parserDataBaseSP(s):
    content = parser(s)

    dAt = None

    for i in range(len(content)):
        if content[0][1] == "DEFAULT" and content[0][0] == "@":
            dAt = str(content[0][2])
            content = content[1:]
        elif content[0][1] == "DEFAULT" and content[0][0] == "TTL":
            dTTL = int(content[0][2])
            content = content[1:]
        elif content[0][1] == "SOASP":
            dAt = '.'.join(str(content[0][2]).split('.')[1:])
        else:
            break

    if dAt == None:
        return None

    dataBase = {}

    for op in content[2:]:
        dom = str(op[0]).replace("@",dAt)
        if dom[-1] != ".":
            dom = dom + "." + dAt

        type = str(op[1])
        if op[2].isnumeric(): 
            value = int(op[2])
        else:
            value = str(op[2])
        if type == "CNAME" and value[-1] != ".":
            value = value + "." + dAt

        if len(op) > 3:
            if op[3] == "TTL" and dTTL != None: 
                ttl = dTTL
            elif op[3].isnumeric:
                ttl = int(op[3])
            else:
                return None

            if len(op) > 4: 
                priority = int(op[4])
            else:
                priority = 0
        
        if dom in dataBase:
            if type in dataBase[dom]:
                dataBase[dom][type].append({"value":value,"ttl":ttl,"priority":priority})
            else:
                dataBase[dom][type] = [{"value":value,"ttl":ttl,"priority":priority}]
        else:
            dataBase[dom] = {type : [{"value":value,"ttl":ttl,"priority":priority}]}

    return dataBase


def parserConfig(s):
    content = parser(s)
    config = {}

    for op in content:
        dom = op[0]
        if dom[-1] != '.':
            dom = dom + '.'
        type = op[1]
        if type in ["SS", "SP", "DD"]:
            aux = op[2].split(':')
            value = aux[0]
            if len(aux) == 2:
                port = int(aux[1])
            else:
                port = -1
        else:
            value = op[2]
        
        if type in config:
            if type in ["SS", "SP", "DD"]: config[type].append({"domain":dom,"value":value,"port":port})
            else: config[type].append({"domain":dom,"value":value})
        else:
            if type in ["SS", "SP", "DD"]: config[type] = [{"domain":dom,"value":value,"port":port}]
            else: config[type] = [{"domain":dom,"value":value}]
    
    return config


def parserDataBaseSS(content):
    dataBase = {}

    for line in content:
        op = line.split(";")
        dom = op[0]
        type = op[1]

        if op[2].isnumeric(): 
            value = int(op[2])
        else:
            value = str(op[2])

        ttl = 0
        priority = 0

        if len(op) > 3:
            ttl = int(op[3])
            if len(op) > 4:
                priority = int(op[4])

        if dom in dataBase:
            if type in dataBase[dom]:
                dataBase[dom][type].append({"value":value,"ttl":ttl,"priority":priority})
            else:
                dataBase[dom][type] = [{"value":value,"ttl":ttl,"priority":priority}]
        else:
            dataBase[dom] = {type : [{"value":value,"ttl":ttl,"priority":priority}]}
    return dataBase