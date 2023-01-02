import socket
from Utilities.Utils import Utils


class Client:
    @staticmethod
    def run(address, dom, typeQ, flags):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg=f"3001,{flags},0,0,0,0;{dom},{typeQ};"
        s.sendto(msg.encode('utf-8'), (address, 3000))
        con, add = s.recvfrom(1024)
        msg = con.decode('utf-8')
        Utils.printQuery(msg)
        return 0
