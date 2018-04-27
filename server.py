# 服务端程序
import socket
import os
import threading
import json
import math

fileList = {}  # {filename:{size:filesize, peers:[(,),(,)]}}
lock = threading.Lock()

def add_file(filename, filesize, addr):
    global fileList
    if(filename in fileList):
        if not(addr in fileList[filename]["peers"]):
            fileList[filename]["peers"].append(addr)
    else:
        fileList[filename] = {"size": filesize, "peers": [addr]}

def delete_peer(addr):
    delList = []
    for key in fileList.keys():
        if addr in fileList[key]["peers"]:
            fileList[key]["peers"].remove(addr)
        if len(fileList[key]["peers"])==0:
            delList.append(key)
    for key in delList:
        del fileList[key]

def echo(conn, addr):
    print(str(addr) + " connect")
    print("-----fileList---------: \n"+str(fileList)+"\n--------------------")
    request = conn.recv(1024).decode()
    print(str(addr) + request)
    # peer初始化
    if request.startswith("INIT"):
        request = request.lstrip("INIT ")
        data_port=int(request.split()[0])
        new_addr=(addr[0],data_port)
        request=request.lstrip(request.split()[0])
        request=request.lstrip()
        thisList = eval(request)
        for filename in thisList.keys():
            lock.acquire()
            try:
                add_file(filename, thisList[filename], new_addr)
            finally:
                lock.release()
        conn.send("INITACK".encode())

    # 请求文件
    elif request.startswith("GET"):
        filename = request.lstrip("GET ")
        if filename in fileList:
            filesize = fileList[filename]["size"]
            peerList = fileList[filename]["peers"]
            if addr in peerList:
                conn.send("ERROR YOU_ALREADY_GOT_IT".encode())
            else:
                peerNum = len(peerList)
                slideSize = 720
                slideNum = math.ceil(filesize/slideSize)
                peerSize = math.ceil(slideNum/peerNum)
                getList = {}
                curInd = 0
                for ind in range(0, peerNum):
                    getList[peerList[ind]] = (curInd, curInd+peerSize)
                    if curInd+peerSize >= slideNum:
                        getList[peerList[ind]] = (curInd, slideNum)
                    curInd += peerSize
                conn.send(("SUCCESS " + str(filesize) +
                        " " + str(getList)).encode())
        else:
            conn.send("ERROR FILE_NOT_FOUND".encode())

    # 添加文件
    elif request.startswith("ADD"):
        request = request.lstrip("ADD ")
        filename = request.split()[0]
        filesize = int(request.split()[1])
        lock.acquire()
        try:
            add_file(filename, filesize, addr)
        finally:
            lock.release()
        conn.send("ADDACK".encode())

    # 下线
    elif request.startswith("QUIT"):
        lock.acquire()
        try:
            delete_peer(addr)
        finally:
            lock.release()        
        conn.send("QUITACK".encode())
        print("-----fileList---------: \n"+str(fileList)+"\n--------------------")

    # 未定义请求
    else:
        conn.send(("ERROR "+"UNKNOWN_REQUEST "+request).encode())
    conn.close()

def main():
    # 开启ip和端口
    ip_port = ('127.0.0.1', 16337)
    # 生成一个socket对象
    sk = socket.socket()
    # 绑定ip端口
    sk.bind(ip_port)
    # 最多连接数
    sk.listen(5)
    # 开启死循环等待客户端连接
    print('中央服务器启动...')
    while 1:
        # 接受连接
        conn, addr = sk.accept()
        t = threading.Thread(target=echo, args=(conn, addr))
        t.daemon = True
        t.start()


if __name__ == "__main__":
    main()
