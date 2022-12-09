import socket
import sys
import query

def main(address, dom, t, r, mode):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg=f"3001,{r},0,0,0,0;{dom},{t};"
    s.sendto(msg.encode('utf-8'), (address, 3000))
    con, add = s.recvfrom(1024)
    msg = con.decode('utf-8')
    if mode:
        query.compactQuery(msg)
        query.printQuery(msg)



if __name__ == "__main__":
    debug = False
    if len(sys.argv) == 6:
        if "-d" == sys.argv[5]: debug = True
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], debug)