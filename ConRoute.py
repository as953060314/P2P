import socket
import threading
import os

ip = 'aaa'
boss = ('127.0.0.1', 12306)
graph = {}
ALL_Routing_table={}
'''

DIJKSTRA
'''
def LS(ip):
    #拓扑图的点集
    Routing_Table={}
    Routing_Table[ip]={"Distance":0,"Next_Node":ip}
    N=set()
    #当前路由器到其他路由器的距离
    D={}
    #初始化
    for neihbour , distance in graph[ip].items():
    temp={}
        temp["Distance"]=distance
        temp["Next_Node"]=neihbour
        Routing_Table[neihbour]=temp
    for route in graph.keys():
        N.add(route)
        D[route]=99999
    for neihbour , distance in graph[ip].items():
        D[neihbour]=distance
    D[ip]=0
    N.remove(ip)
    #lock.acquire()
    while N :
        min_route=99999
        next_route=0
        for route in N:
            next_route=route if D[route]<min_route else next_route
            min_route=D[route] if D[route]<min_route else min_route
            #print(D[route],next_route,min_route,route)
        if next_route==0:
            break
        N.remove(next_route)
        Routing_Table[next_route]["Distance"]=min_route
        for neihbour in graph[next_route].keys():
            Routing_Table[neihbour]["Next_Node"]=Routing_Table[next_route]["Next_Node"] if D[next_route]+graph[next_route][neihbour]<D[neihbour] else Routing_Table[neihbour]["Next_Node"]
            D[neihbour]=D[next_route]+Graph_Table[next_route][neihbour] if D[next_route]+Graph_Table[next_route][neihbour]<D[neihbour] else D[neihbour]
    for route in Routing_Table.keys():
        Routing_Table[route]["Distance"]=D[route]
        if D[route]>=99999:
            del Routing_Table[route]
    ALL_Routing_table[ip]=Routing_Table
    #lock.release()
    
'''





'''
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def addPathGraph(x, y, val):
    global graph
    if x in graph:
            graph[x][y] = val
    else:
        graph[x] = {y: val}


def path(sip, dip, cost):
    addPathGraph(sip, dip, cost)
    addPathGraph(dip, sip, cost)
    killList = []
    for x in graph.keys():
        for y in graph[x].keys():
            if graph[x][y] >= 99999:
                killList.append((x, y))
    for death in killList:
        del graph[death[0]][death[1]]
    killList = []
    for x in graph.keys():
        if graph[x] == {}:
            killList.append(x)
    for death in killList:
        del graph[death]
    print(graph)
    for ip in graph.keys():
        LS(ip)

def ask(coon,addr, dip): #TODO
    if dip in ALL_Routing_table[addr]:
        via=ALL_Routing_table[addr]["Next_Node"]
        dis=ALL_Routing_table[addr]["Distance"]
    else:
        via="None"
        dis=99999
    coon.send(("ans "+via+" "+str(dis)).encode())

def allRoute(coon, sip):
    ar = {}
    if sip in ALL_Routing_table:
        ar=ALL_Routing_table[sip]
    coon.send(("all "+str(ar)).encode())


def listenMain():
    s = socket.socket()
    print(boss)
    s.bind(boss)
    s.listen(5)
    while True:
        coon, addr = s.accept()
        request = coon.recv(1024).decode()
        print(str(addr)+" REQUEST: "+request)
        if request.startswith("path "):
            dip = request.lstrip("path ").split()[0]
            dis = request.lstrip("path ").split()[1]
            path(addr[0], dip, int(dis))
        elif request.startswith("ask "):
            request = request.lstrip("ask ")
            ask(coon,addr[0], request)
        elif request == "all":
            allRoute(coon, addr[0])
        coon.close()


def main():
    global ip
    global boss
    ip = get_host_ip()
    ip = '127.0.0.1'
    print("I'm "+ip)
    boss = (ip, 12306)
    print(boss)
    listenMain()

if __name__ == "__main__":
    main()