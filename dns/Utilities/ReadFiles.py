

def readFiles(s):
    f = open(s, "r")
    doc = f.read()
    f.close()

    content = []

    for line in doc.split("\n"):
        text = line.split("#")[0].split(" ")
        i = 0
        while i < len(text):
            if text[i] == '':
                text.pop(i)
                i-=1
            i+=1
        if len(text) >= 1:
            content.append(text)
    return content

class ReadFiles:

    @staticmethod
    def readFileRootServers(s):
        r = []
        for line in readFiles(s):
            r += line
        return r

    @staticmethod
    def readFileDataBase(s):
        content = readFiles(s)

        dAt = ""

        for i in range(len(content)):
            if content[0][1] == "DEFAULT" and content[0][0] == "@":
                dAt = str(content[0][2])
                content = content[1:]
            elif content[0][1] == "DEFAULT" and content[0][0] == "TTL":
                dTTL = int(content[0][2])
                content = content[1:]
            else:
                break

        dataBase = {}

        for op in content:
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
                elif op[3].isnumeric():
                    ttl = int(op[3])
                else:
                    return "decoding-error--TTL-not-defined"

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

    @staticmethod
    def readFileConfig(s):
        content = readFiles(s)
        config = {}

        try:
            for op in content:
                dom = op[0]
                type = op[1]
                if dom[-1] != '.':
                    dom = dom + '.'

                if dom not in config:
                    for key in config.keys():
                        if str(key).endswith(dom) or str(dom).endswith(key):
                            for typeQ in config[key].keys():
                                if typeQ not in ['DD', 'LG'] and type not in ['DD', 'LG']:
                                    return None

                if type in ["SS", "SP", "DD"]:
                    aux = op[2].split(':')
                    value = aux[0]
                    if len(aux) == 2:
                        port = int(aux[1])
                    else:
                        port = -1
                else:
                    value = op[2]
                
                if type in ["SS", "SP", "DD"]: 
                    v = {"value":value,"port":port}
                else: 
                    v = {"value":value}

                if dom in config:
                    if type in config[dom]:
                        config[dom][type].append(v)
                    else:
                        config[dom][type] = [v]
                else:
                    config[dom] = {type : [v]}
            return config
        except:
            return None

    @staticmethod
    def getDataBaseSS(content):
        if type(content) != list:
            return content

        dataBase = {}

        for line in content:
            op = line.split(",")
            dom = op[0]
            t = op[1]

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
                if t in dataBase[dom]:
                    dataBase[dom][t].append({"value":value,"ttl":ttl,"priority":priority})
                else:
                    dataBase[dom][t] = [{"value":value,"ttl":ttl,"priority":priority}]
            else:
                dataBase[dom] = {t : [{"value":value,"ttl":ttl,"priority":priority}]}

        return dataBase