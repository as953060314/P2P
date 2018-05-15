import socket
import threading
import os


ip = 'aaa'
listen_port = 20020
exitFlag = 0

Routing_Table = {}

n_table ={}

lock = threading.Lock()

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def renewPath():
    addPk = "PATH "+str(Routing_Table)
    print(str(n_table))
    for t in n_table.keys():
        if n_table[t]<99999:
            print("ABCD---"+t)
            s = socket.socket()
            s.connect((t, listen_port))
            s.send(addPk.encode())


def addPath(nip, distance):
    Routing_Table[nip] = {"Distance": distance, "Next_Node": nip}
    n_table[nip] = distance
    renewPath()


def renewListener(sip, pk):
    flag = False
    pk = pk.lstrip("PATH ")
    nrt = eval(pk)
    print("RENEW--"+sip+"  "+str(nrt))
    dsip = nrt[ip]["Distance"]
    n_table[sip] = dsip
    if (not(sip in Routing_Table.keys())) or Routing_Table[sip]["Distance"]>dsip:
        Routing_Table[sip] = {"Distance": dsip, "Next_Node":sip}
        flag = True
    for t in nrt.keys():
        print(t)
        print("-----DSFD"+str(nrt[t]))
        print("Distance" in nrt[t].keys())
        print(nrt[t].keys())
        print("NRT--"+str(nrt[t]["Distance"]))
        if t==ip:
            continue
        elif (t in Routing_Table) and (nrt[t]["Distance"]+dsip < Routing_Table[t]["Distance"]):
            Routing_Table[t] = {"Distance": nrt[t]["Distance"]+dsip, "Next_Node": sip}
            flag = True
        elif t in Routing_Table:
            continue
        else:
            Routing_Table[t] = {"Distance": nrt[t]["Distance"]+dsip, "Next_Node": sip}
            flag = True
        
    if flag:
        renewPath()
    return

            

def newPath(nip, distance):
    addPath(nip, distance)


def leave():
    for t in n_table.keys():
        n_table[t] = 99999
        Routing_Table[t]["Distance"] = 99999
    renewPath()




def showRoutingTable():
    global Routing_Table
    print("Destination        Distance        Next Node\n")
    for router_ip in Routing_Table:
        print(router_ip + "        " + str(Routing_Table[router_ip]['Distance']) + "        " + Routing_Table[router_ip]['Next_Node'])


def commandMain():
    while True:
        command = input("Please input: ")
        command = command.split()
        if command[0] == "add" and len(command)==3:
            lock.acquire()
            addPath(command[1], int(command[2]))
            lock.release()
        elif command[0] == "show":
            showRoutingTable()
        elif command[0] == "leave":
            lock.acquire()
            leave()
            lock.release()
            os._exit(0)
        else:
            print("Invalid input!")


def listenMain():
    s = socket.socket()
    s.bind((ip, listen_port))
    s.listen(5)
    while True:
        coon, addr = s.accept()
        request = coon.recv(1024).decode()
        print(request)
        if request.startswith("PATH "):
            lock.acquire()
            renewListener(addr[0], request)
            lock.release()
        coon.close()


def main():
    global Routing_Table
    global ip
    ip = get_host_ip()
    print("I'm "+ip)
    # n_table[ip] = 99999
    cm = threading.Thread(target = commandMain, args = ())
    cm.start()
    lm = threading.Thread(target = listenMain, args = ())
    lm.start()

if __name__ == "__main__":
    main()