import socket
import threading
import os
import operator


ip = '192.168.199.211'
listen_port = 16330
command_port = 16440
exitFlag = 0
lock=threading.Lock()

Routing_Table = {}
Graph_Table={}
Routing_Table[ip]={"Next_Node":ip,"Distance":0}
'''
Graph_Table {route:distance}
'''


# Route = {
#     'Distance' : '''总距离（字符串）''',
#     'Next_Node' : '''下一节点（字符串）''',
# }

#自动生成路由表
#def makeRoutingTable():

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def showRoutingTable():
    '''获取路由表'''
    #global Routing_Table
    print("Destination        Distance        Next Node\n")
    for router_ip, route in Routing_Table.items():
        print(router_ip ,route['Distance'] ,route['Next_Node'])

def LS():
	global ip
    #拓扑图的点集
	N=set()
    #当前路由器到其他路由器的距离
	D={}
    #初始化
	for neihbour , distance in Graph_Table[ip].items():
		temp={}
		temp["Distance"]=distance
		temp["Next_Node"]=neihbour
		Routing_Table[neihbour]=temp
	for route in Graph_Table.keys():
		N.add(route)
		D[route]=99999
	for neihbour , distance in Graph_Table[ip].items():
		D[neihbour]=distance
	D[ip]=0
	N.remove(ip)
	lock.acquire()
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
		for neihbour in Graph_Table[next_route].keys():
			Routing_Table[neihbour]["Next_Node"]=Routing_Table[next_route]["Next_Node"] if D[next_route]+Graph_Table[next_route][neihbour]<D[neihbour] else Routing_Table[neihbour]["Next_Node"]
			D[neihbour]=D[next_route]+Graph_Table[next_route][neihbour] if D[next_route]+Graph_Table[next_route][neihbour]<D[neihbour] else D[neihbour]
	for route in Routing_Table.keys():
		Routing_Table[route]["Distance"]=D[route]
	lock.release()
	showRoutingTable()
 	#新的route_table生成完成		

def addNeighbour(Nei_ip, distance):
	'''添加邻居'''
	global ip
	#print(Nei_ip)
	distance=int(distance)
	Nei=(Nei_ip,listen_port)
	s=socket.socket()
	s.connect(Nei)
	lock.acquire()
	Graph_Table[ip][Nei_ip]=distance
	print("hello1")
	lock.release()
	s.send(("ADD "+str(Graph_Table[ip])).encode())
	print("hello")
	response=eval(s.recv(1024).decode().lstrip("ADDR "))
	s.close()
    # 根据新邻居返回的拓扑图，更新自己的拓扑图
	for route_ip ,route_neihbour in response.items():
		if route_ip!= ip:
			Graph_Table[route_ip]=route_neihbour
	print(Graph_Table)
    #广播最新的拓扑图
	for neihbour in Graph_Table[ip].keys():
		s=socket.socket()
		Nei=(neihbour,listen_port)
		s.connect(Nei)
		s.send(("Update "+str(Graph_Table)).encode())
		s.close()
	    #更新路由表 
	LS()

def ADDR(Graph,addr,coon):
	global ip
	Graph=eval(Graph)
	Graph_Table[addr]=Graph
	Graph_Table[ip][addr]=Graph[ip]
	coon.send(("ADDR "+str(Graph_Table)).encode())
	LS()

#更新并广播
def Update(Graph,addr):
	global ip
	global Graph_Table
	lock.acquire()
	new_Graph=eval(Graph)
	print(Graph_Table== new_Graph)
	if Graph_Table== new_Graph:
		lock.release()
		return
	Graph_Table=new_Graph
	lock.release()
	for neihbour in Graph_Table[ip].keys():
		if neihbour!=addr:
			s=socket.socket()
			Nei=(neihbour,listen_port)
			s.connect(Nei)
			s.send(("Update "+str(Graph_Table)).encode())
			s.close()
	LS()



def traceRoute(destination):
    '''打印当前ip并调用下一路由器的该函数'''
    print(ip + '->')
    s = socket.socket()
    # s.bind((ip, command_port))
    router_ip = Routing_Table[destination][Next_Node]
    s.connect(router_ip)
    s.send(("traceroute" + destination).encode())

def leave_request(Graph,addr):
	Update(Graph,addr)


def leave():
    '''该路由器离开网络'''
    global ip
    for neihbour in Graph_Table[ip].keys():
    	Graph_Table[neihbour][ip]=99999
    for neihbour in Graph_Table[ip].keys():
    	s=socket.socket()
    	Nei=(neihbour,listen_port)
    	s.connect(Nei)
    	s.send(("LEAVE "+str(Graph_Table)).encode())
    	s.close()


def commandMain():
    '''获取本地命令操作'''
    while True:
        command = input("Please input your command:")
        command = command.split()
        if command[0] == "add":
            '''格式例：add 192.168.199.143 8'''
            '''这里需要算法自动执行程序更新路由表'''
            addNeighbour(command[1], command[2])
        elif command[0] == "show":
            showRoutingTable()
        elif command[0] == "traceroute":
            '''格式例：traceroute 192.168.199.143'''
            destination = command[1]
            traceRoute(destination)
        elif command[0] == "leave":
            '''该路由器离开（损坏）'''
            '''这里需要算法自动执行程序更新路由表'''
            leave()
            os._exit(0)
        else:
            print("Invalid input!")


def listenMain():
    '''监听获取其他路由器传来的信息'''
    s = socket.socket()
    s.bind((ip, listen_port))
    s.listen(5)
    while True:
        coon, addr = s.accept()
        request = coon.recv(1024).decode()
        print(request)
        if request.split()[0] == "traceroute":
            '''继续上一级的traceroute()继续寻路'''
            destination = request[1]
            traceRoute(destination)
        elif request.split()[0] == "LEAVE":
            leave_request(request.lstrip("LEAVE "), addr[0])
        elif request.split()[0]=="ADD":
        	ADDR(request.lstrip("ADD "),addr[0],coon)
        elif request.split()[0]=="Update":
        	Update(request.lstrip("Update "),addr[0])
        coon.close()

def main():
    #global Routing_Table
    Graph_Table[ip]={}
    cm = threading.Thread(target = commandMain, args = ())
    cm.start()
    lm = threading.Thread(target = listenMain, args = ())
    lm.start()

ip=get_host_ip()
if __name__ == "__main__":
    main()