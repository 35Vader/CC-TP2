import sys

from Server.Server import Server
from Server.Client import Client

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("!!! Invalid arguments !!!")
        print("CLIENT           -> run.py c [address] [domain] [type] [flags]")
        print("PRIMARY SERVER   -> run.py sp [domain(short)]")
        print("SECONDARY SERVER -> run.py ss [domain(short)]")
        exit(0)

    configFile = 'dnsFiles/'
    debug = False
    if sys.argv[1] == "c":
        Client.run(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        configFile = f"dnsFiles/{sys.argv[2]}-conf/"
        if sys.argv[1] == "sp":
            configFile += "configSP.db"
        elif sys.argv[1] == "ss":
            configFile += "configSS.db"
        elif sys.argv[1] == "sr":
            configFile += "configSR.db"
        elif sys.argv[1] == "s":
            configFile += "configS.db"
        else:
            exit(1)

        if len(sys.argv) == 4 and sys.argv[3] == "-d":
            debug = True

        server = Server(configFile, debug)
        server.run()