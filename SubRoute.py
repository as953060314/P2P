import socket
import threading
import os

ip = 'aaa'
listen_port = 20020
boss = ('127.0.0.1', 12306)


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

def addPath(dip, dis):
    s = socket.socket()
    s.connect(boss)
    s.send(("path "+dip+" "+str(dis)).encode())

def delPath(dip):
    addPath(dip, 99999)

def askPath(dip):
    s = socket.socket()
    s.connect(boss)
    s.send(("ask "+dip).encode())
    request = s.recv(1024).decode().lstrip("ans ").split()
    return request[0], int(request[1])

def showRoutingTable():
    s = socket.socket()
    s.connect(boss)
    s.send("all".encode())
    request = s.recv(1024).decode()
    request.lstrip("all ")
    route_table = eval(request)
    print("Destantion          Via                   Cost")
    for t in route_table.keys():
        if (route_table["Distance"]<99999):
            print( t + "      " + route_table["Next_Node"] + "       " + str(route_table["Distance"]))

def leave():
    s = socket.socket()
    s.connect(boss)
    s.send("all".encode())
    request = s.recv(1024).decode()
    request.lstrip("all ")
    route_table = eval(request)
    for t in route_table.keys():
        delPath(t)


def commandMain():
    while True:
        command = input()
        if command.startswith("add "):
            dip = command.lstrip("add ").split()[0]
            dis = command.lstrip("add ").split()[1]
            if dip==None or dis==None:
                print("Invalid input!")
                continue
            addPath(dip, dis)
        elif command.startswith("del "):
            dip = command.lstrip("del ").split()[0]
            if dip==None:
                print("Invalid input!")
                continue
            delPath(dip)
        elif command == "show":
            showRoutingTable()
        elif command == "leave":
            leave()
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
        print(str(addr)+" REQUEST: "+request)
        coon.close()


def main():
    global ip
    ip = get_host_ip()
    ip = '127.0.0.1'
    print("I'm "+ip)
    # n_table[ip] = 99999
    cm = threading.Thread(target = commandMain, args = ())
    cm.start()
    lm = threading.Thread(target = listenMain, args = ())
    lm.start()

if __name__ == "__main__":
    main()