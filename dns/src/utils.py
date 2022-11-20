def printL (text,lenght):
    t = str(text)
    aux = lenght-len(t)
    if aux%2 == 0:
        aux2 = int(aux/2)
        return ' '*aux2 + t + ' '*aux2 + '|'
    else:
        aux2 = int(aux/2)
        return ' '*aux2 + t + ' '*aux2 + ' |'


def showTable(d:dict):
    for type in d:
        value = d[type]
        s = printL(type,12)
        if list(value):
            for v in value:
                s2 = ""
                for n in v:
                    s2 += printL(v[n],25)
                print(s+s2)
        else:
            s2 = ""
            for n in value:
                s2 += printL(value[n],25)
            print(s+s2)
        s = ""