

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

    print("@ = " + dAt)
    print("ttl = " + str(dTTL))


    for op in content[2:]:
        par = str(op[0]).replace("@",dAt)
        if par[-1] != ".":
            par = par + "." + dAt

        type = str(op[1])
        value = str(op[2])
        ttl = 0
        priority = 0

        if len(op) > 3:
            if op[3] == "TTL": ttl = dTTL 

            if len(op) > 4: priority = int(op[4])

        if type in dataBase:
            dataBase[type].append({"name":par,"value":value,"ttl":ttl,"priority":priority})
        else:
            dataBase[type]= [{"name":par,"value":value,"ttl":ttl,"priority":priority}]

    print(dataBase)
    return dataBase


def parserConfig(s):
    content = parser(s)

parserConfig("src/dnsFiles/config.txt")
parserDataBase("src/dnsFiles/DataBase.txt")

