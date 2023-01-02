import socket
import sys
import threading

from Utilities.Utils import Utils

class Cache:

    # Cache private variables
    serverCache = {}
    queryCache = {}
    allLog = []
    logFiles = []
    timestamp = 0
    mode = True

    # Cache init function
    def __init__(self, serverDataBase, logFiles, mode):
        self.mode = mode
        self.allLog += logFiles
        self.logFiles += logFiles
        for domain in serverDataBase.keys():
            lg = serverDataBase[domain]["domainLog"]
            self.allLog += lg
            if serverDataBase[domain]["isSP"]:
                self.loadDataBaseSP(serverDataBase[domain]["data"], lg + logFiles)
            else:
                self.loadDataBaseSS(serverDataBase[domain]["data"], lg + logFiles)

    def incTimeStamp(self):
        self.timestamp += 1

    def debug(self):
        while True:
            try:
                s = input()
                if s == "lg":
                    print('\n----------------')
                    print(f"logFiles -> {self.logFiles}\nallLog -> {self.allLog}")
                    print('----------------\n')
                elif s == "t":
                    print('\n----------------')
                    print(f"timestamp -> {self.timestamp}")
                    print('----------------\n')
                elif s == "sc":
                    print('\n---------------------------------------------------------\n')
                    Utils.showTable(self.serverCache)
                    print('---------------------------------------------------------\n')
                elif s == "qc":
                    print('\n---------------------------------------------------------\n')
                    Utils.showTable(self.queryCache)
                    print('---------------------------------------------------------\n')
                elif s == "test":
                    dic = Utils.decodeQuery("3001,R,0,3,3,3;cc.tp.,NS;tp. MX mx1.tp. 2,cc.tp. NS ns2.cc.tp. 86400,cc.tp. NS ns3.cc.tp. 86400;cc.tp. NS ns1.cc.tp. 86400,cc.tp. NS ns2.cc.tp. 86400,cc.tp. NS ns3.cc.tp. 86400;ns1.cc.tp. A 10.0.1.17 86400,ns2.cc.tp. A 10.0.15.10 86400,ns3.cc.tp. A 10.0.1.16 86400;")
                    self.loadNewQuery(dic)
            except:
                pass


    # Functions that handle cache entries
    def loadDataBaseSS(self, data:dict, logs):
        for domain in data.keys():
            for typeQ in data[domain].keys():
                for entry in data[domain][typeQ]:
                    self.put(
                        domain,
                        typeQ,
                        entry["value"],
                        entry["ttl"],
                        entry["priority"],
                        "SP",
                        logs
                    )

    def loadDataBaseSP(self, data:dict, logs):
        for domain in data.keys():
            for typeQ in data[domain].keys():
                for entry in data[domain][typeQ]:
                    if domain in self.serverCache:
                        if typeQ in self.serverCache[domain]:
                            # New entry
                            self.serverCache[domain][typeQ].append({"value": entry["value"], "ttl": entry["ttl"], "timestamp": 0, "priority": entry["priority"], "origin": "FILE"})
                        else:
                            # New entry
                            self.serverCache[domain][typeQ] = [{"value": entry["value"], "ttl": entry["ttl"], "timestamp": 0, "priority": entry["priority"], "origin": "FILE"}]
                    else:
                        # New entry
                        self.serverCache[domain] = {
                            "domainLog" : logs,
                            typeQ : [{
                                "value": entry["value"],
                                "ttl": entry["ttl"],
                                "timestamp": 0,
                                "priority": entry["priority"],
                                "origin":
                                "FILE"
                            }]
                        }

    def loadNewQuery(self, dic):
        minttl = -1
        for entry in dic['RESPONSE_VALUES'] + dic['AUTHORITIES_VALUES'] + dic['EXTRA_VALUES']:
            entryList = entry.split(' ')
            if len(entryList) == 4:
                self.put(
                    entryList[0],
                    entryList[1],
                    entryList[2],
                    int(entryList[3]),
                )
            else:
                self.put(
                    entryList[0],
                    entryList[1],
                    entryList[2],
                    int(entryList[3]),
                    int(entryList[4]),
                )
            if minttl == -1 or minttl > int(entryList[3]):
                minttl = int(entryList[3])
            Utils.writeInLogFiles(self.allLog, f"EV @ new-cache-entry server-cache", self.mode)
        self.putQueryCache(dic, minttl, False)

    def put (self, domain, typeQ, value, ttl:int, priority = 0, origin = "OTHERS", logs = None):
        if origin == "OTHERS":
            logs = self.allLog
        elif origin == "SP":
            pass
        else:
            # invalid origin
            return

        if domain in self.serverCache:
            if typeQ in self.serverCache[domain]:
                for i in range(len(self.serverCache[domain][typeQ])):
                    if self.serverCache[domain][typeQ][i]["value"] == value:
                        if self.serverCache[domain][typeQ][i]["origin"] != "FILE":
                            if origin == "OTHERS" and self.serverCache[domain][typeQ][i]["origin"] == "SP":
                                return
                            # Entry updated
                            self.serverCache[domain][typeQ][i]["ttl"] = ttl
                            self.serverCache[domain][typeQ][i]["timestamp"] = ttl + self.timestamp
                            self.serverCache[domain][typeQ][i]["priority"] = priority
                            self.serverCache[domain][typeQ][i]["origin"] = origin
                        else:
                            # invalid operation
                            pass
                        return
                # New entry
                self.serverCache[domain][typeQ].append({
                    "value": value,
                    "ttl": ttl,
                    "timestamp": ttl + self.timestamp,
                    "priority": priority,
                    "origin": origin
                })
            else:
                # New entry
                self.serverCache[domain][typeQ] = [{
                    "value": value,
                    "ttl": ttl,
                    "timestamp": ttl + self.timestamp,
                    "priority": priority,
                    "origin": origin
                }]
        else:
            # New entry
            self.serverCache[domain] = {
                "domainLog" : logs,
                typeQ : [{
                    "value": value,
                    "ttl": ttl,
                    "timestamp": ttl + self.timestamp,
                    "priority": priority,
                    "origin": origin
                }]
            }

    def get(self, domain, typeQ):
        a = True
        response = []
        domAuth = '.'.join(domain.split('.')[1:])
        if domain not in self.serverCache:
            # Domain does not exist
            if typeQ == 'A':
                if domAuth in self.serverCache:
                    return 1
                else:
                    return 2
            else:
                return 2

        dom = domain

        if typeQ not in self.serverCache[domain]:
            # Type does not exist
            if 'A' in self.serverCache[domain]:
                return 2
            elif 'CNAME' in self.serverCache[domain]:
                if (self.serverCache[domain]["CNAME"][0]["origin"] == "FILE") or (self.timestamp <= self.serverCache[domain]["CNAME"][0]["timestamp"]):
                    dom = self.serverCache[domain]["CNAME"][0]["value"]
                    if self.serverCache[domain]["CNAME"][0]["origin"] == "OTHERS":
                        a = False
                else:
                    self.serverCache[domain]["CNAME"].pop(0)
                    if len(self.serverCache[domain]["CNAME"]) == 0:
                        self.serverCache[domain].pop("CNAME")
                        if len(self.serverCache[domain]) == 1:
                            self.serverCache.pop(domain)
                    if typeQ == 'A':
                        if domAuth in self.serverCache:
                            return 1
                        else:
                            return 2
                    else:
                        return 2
            else:
                return 1

        removeListElem = set([])
        removeListDom = set([])
        for i in range(len(self.serverCache[dom][typeQ])):
            if (self.serverCache[dom][typeQ][i]["origin"] == "FILE") or (self.timestamp <= self.serverCache[dom][typeQ][i]["timestamp"]):
                if self.serverCache[domain][typeQ][0]["origin"] == "OTHERS":
                    a = False
                response.append({
                    "value": self.serverCache[dom][typeQ][i]["value"],
                    "ttl": self.serverCache[dom][typeQ][i]["ttl"],
                    "priority": self.serverCache[dom][typeQ][i]["priority"]
                })
            else:
                removeListElem.add((dom,i))
                removeListDom.add(dom)

        for elem in removeListElem:
            self.serverCache[elem[0]][typeQ].pop(elem[1])
        for dom in removeListDom:
            if len(self.serverCache[dom][typeQ]) == 0:
                self.serverCache[dom].pop(typeQ)
                if len(self.serverCache[dom]) == 1:
                    self.serverCache.pop(dom)

        return (response, a)

    def getResponse(self, typeQ, domain, data):
        rv = []
        names = []
        ttl = -1
        for entry in data:
            s = domain + ' '
            s += typeQ + ' '
            s += str(entry['value']) + ' '
            s += str(entry['ttl'])
            if int(entry['priority']) != 0:
                s += ' ' + str(entry['priority'])

            rv.append(s)

            if str(entry['value'])[-1] == '.':
                names.append(str(entry['value']))

            if ttl == -1 or ttl > entry["ttl"]:
                ttl = entry["ttl"]

        return (rv, names, ttl)

    def getAuthorities(self, domain):
        a = True
        av = []
        names = []
        removeListElem = set([])
        removeListDom = set([])
        ttl = -1
        for dom in self.serverCache.keys():
            if (domain == "" or domain == dom) and 'NS' in self.serverCache[dom].keys():
                for i in range(len(self.serverCache[dom]['NS'])):
                    entry = self.serverCache[dom]['NS'][i]
                    if (entry["origin"] == "FILE") or (self.timestamp <= entry["timestamp"]):
                        if entry["origin"] == "OTHERS":
                            a = False
                        s = dom + ' NS '
                        s += str(entry['value']) + ' '
                        s += str(entry['ttl'])
                        if int(entry['priority']) != 0:
                            s += ' ' + str(entry['priority'])
                        av.append(s)

                        if str(entry['value'])[-1] == '.':
                            names.append(str(entry['value']))

                        if ttl == -1 or ttl > entry["ttl"]:
                            ttl = entry["ttl"]
                    else:
                        removeListElem.add((dom,i))
                        removeListDom.add(dom)

        for elem in removeListElem:
            self.serverCache[elem[0]]["NS"].pop(elem[1])
        for dom in removeListDom:
            if len(self.serverCache[dom]["NS"]) == 0:
                self.serverCache[dom].pop("NS")
                if len(self.serverCache[dom]) == 1:
                    self.serverCache.pop(dom)

        return (av, names, ttl, a)

    def getExtra(self, namesA, namesR, typeQ, domain):
        a = True
        if typeQ == 'A':
            # (para querys do tipo A em que o domain é um NS)
            # retira a entrada se esta já está incluida nos RESPONSE_VALUES
            # e foi novamente adicionado pela getAuthorities
            listNames = list(namesA)
            try:
                listNames.remove(domain)
            except:
                pass
        else:
            listNames = list(namesA + namesR)

        rv = []
        ttl = -1
        removeListElem = set([])
        removeListDom = set([])

        for dom in self.serverCache.keys():
            if dom in listNames and 'A' in self.serverCache[dom].keys():
                for i in range(len(self.serverCache[dom]['A'])):
                    entry = self.serverCache[dom]['A'][i]
                    if (entry["origin"] == "FILE") or (self.timestamp <= entry["timestamp"]):
                        if entry["origin"] == "OTHERS":
                            a = False
                        s = dom + ' A '
                        s += str(entry['value']) + ' '
                        s += str(entry['ttl'])
                        if int(entry['priority']) != 0:
                            s += ' ' + str(entry['priority'])
                        rv.append(s)

                        if ttl == -1 or ttl > entry["ttl"]:
                            ttl = entry["ttl"]
                    else:
                        removeListElem.add((dom,i))
                        removeListDom.add(dom)

        for elem in removeListElem:
            self.serverCache[elem[0]]["A"].pop(elem[1])
        for dom in removeListDom:
            if len(self.serverCache[dom]["A"]) == 0:
                self.serverCache[dom].pop("A")
                if len(self.serverCache[dom]) == 1:
                    self.serverCache.pop(dom)

        return (rv, ttl, a)




    # Functions that handle cache queries
    def putQueryCache(self, dic, ttl, a:bool):
        domain = dic['QUERY_INFO_NAME']
        typeQ = dic['QUERY_INFO_TYPE']
        if domain in self.queryCache:
            if typeQ in self.queryCache[domain]:
                self.queryCache[domain][typeQ]["RESPONSE_CODE"] = dic["RESPONSE_CODE"]
                self.queryCache[domain][typeQ]["RESPONSE_VALUES"] = dic["RESPONSE_VALUES"]
                self.queryCache[domain][typeQ]["AUTHORITIES_VALUES"] = dic["AUTHORITIES_VALUES"]
                self.queryCache[domain][typeQ]["EXTRA_VALUES"] = dic["EXTRA_VALUES"]
                self.queryCache[domain][typeQ]["N_VALUES"] = dic["N_VALUES"]
                self.queryCache[domain][typeQ]["N_AUTHORITIES"] = dic["N_AUTHORITIES"]
                self.queryCache[domain][typeQ]["N_EXTRA_VALUES"] = dic["N_EXTRA_VALUES"]
                self.queryCache[domain][typeQ]["timestamp"] = ttl + self.timestamp
                self.queryCache[domain][typeQ]["a"] = a
            else:
                # New entry
                self.queryCache[domain][typeQ] = {
                    "RESPONSE_CODE": dic['RESPONSE_CODE'],
                    "RESPONSE_VALUES": dic['RESPONSE_VALUES'],
                    "AUTHORITIES_VALUES": dic['AUTHORITIES_VALUES'],
                    "EXTRA_VALUES": dic['EXTRA_VALUES'],
                    "N_VALUES": dic['N_VALUES'],
                    "N_AUTHORITIES": dic['N_AUTHORITIES'],
                    "N_EXTRA_VALUES": dic['N_EXTRA_VALUES'],
                    "timestamp": ttl + self.timestamp,
                    "a": a
                }
        else:
            # New entry
            self.queryCache[domain] = {
                typeQ : {
                    "RESPONSE_CODE": dic['RESPONSE_CODE'],
                    "RESPONSE_VALUES": dic['RESPONSE_VALUES'],
                    "AUTHORITIES_VALUES": dic['AUTHORITIES_VALUES'],
                    "EXTRA_VALUES": dic['EXTRA_VALUES'],
                    "N_VALUES": dic['N_VALUES'],
                    "N_AUTHORITIES": dic['N_AUTHORITIES'],
                    "N_EXTRA_VALUES": dic['N_EXTRA_VALUES'],
                    "timestamp": ttl + self.timestamp,
                    "a": a
                }
            }

    def getQueryCache(self, dic):
        domain = dic['QUERY_INFO_NAME']
        typeQ = dic['QUERY_INFO_TYPE']

        if domain in self.queryCache and typeQ in self.queryCache[domain]:
            if self.queryCache[domain][typeQ]['timestamp'] >= self.timestamp:
                dic['RESPONSE_CODE'] = self.queryCache[domain][typeQ]['RESPONSE_CODE']
                dic['RESPONSE_VALUES'] = self.queryCache[domain][typeQ]['RESPONSE_VALUES']
                dic['AUTHORITIES_VALUES'] = self.queryCache[domain][typeQ]['AUTHORITIES_VALUES']
                dic['EXTRA_VALUES'] = self.queryCache[domain][typeQ]['EXTRA_VALUES']
                dic['N_VALUES'] = self.queryCache[domain][typeQ]['N_VALUES']
                dic['N_AUTHORITIES'] = self.queryCache[domain][typeQ]['N_AUTHORITIES']
                dic['N_EXTRA_VALUES'] = self.queryCache[domain][typeQ]['N_EXTRA_VALUES']
                return (True, dic, self.queryCache[domain][typeQ]['a'])
            else:
                self.queryCache[domain].pop(typeQ)
                if len(self.queryCache[domain]) == 0:
                    self.queryCache.pop(domain)
        
        return (False, None, True)

    def processQuery(self, dic):
        a = 0
        try:
            domain = dic['QUERY_INFO_NAME']
            typeQ = dic['QUERY_INFO_TYPE']
            if typeQ in ['A', 'CNAME']:
                domAuth = '.'.join(domain.split('.')[1:])
            else:
                domAuth = domain

            namesR = []

            (queryCacheHit, dicAux, aAux) = self.getQueryCache(dic)
            
            if queryCacheHit:
                print("-> Query Cache Hit")
                dic = dicAux
                if not aAux:
                    a = 2
                else:
                    a = 3
            else:
                getR = self.get(domain, typeQ)
                minttl = -1

                if getR != 2:
                    if getR != 1:
                        (getResult, aAux) = getR
                        if not aAux:
                            a = 1
                        (rv, namesR, minttl) = self.getResponse(typeQ, domain, getResult)
                        dic['RESPONSE_VALUES'] = rv
                        dic['N_VALUES'] = len(rv)
                    else:
                        dic['RESPONSE_CODE'] = 1
                    (av, namesA, ttl, aAux) = self.getAuthorities(domAuth)
                    if not aAux:
                        a = 1
                    dic['AUTHORITIES_VALUES'] = av
                    dic['N_AUTHORITIES'] = len(av)
                    if minttl == -1 or minttl > ttl:
                        minttl = ttl
                else:
                    dic['RESPONSE_CODE'] = 2
                    (av, namesA, ttl, aAux) = self.getAuthorities("")
                    if not aAux:
                        a = 1
                    dic['AUTHORITIES_VALUES'] = av
                    dic['N_AUTHORITIES'] = len(av)
                    if minttl == -1 or minttl > ttl:
                        minttl = ttl
                (ex, ttl, aAux) = self.getExtra(namesA, namesR, typeQ, domain)
                if not aAux:
                    a = 1
                dic['EXTRA_VALUES'] = ex
                dic['N_EXTRA_VALUES'] = len(ex)
                if minttl == -1 or minttl > ttl:
                    minttl = ttl

                self.putQueryCache(dic, minttl, a == 0)
                if dic['RESPONSE_CODE'] == 2:
                    Utils.writeInLogFiles(self.allLog, f"EV @ new-cache-entry query-cache", self.mode)
                else:
                    Utils.writeInLogFiles(self.serverCache[domAuth]["domainLog"], f"EV @ new-cache-entry query-cache", self.mode)

        except:
            dic['RESPONSE_CODE'] = 3
            return (dic, self.allLog, 1)
        if dic['RESPONSE_CODE'] == 2:
            return (dic, self.allLog, a)
        else:
            return (dic, self.serverCache[domAuth]["domainLog"], a)

