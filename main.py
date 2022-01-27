import os
import socket
import pickle
import sys
import threading
import _thread

from threading import Lock

import time

s_print_lock = Lock()

isLocal = False
isLocalDef = False
myConnections = []
newConnections = []
s = socket.socket()


def getMyConnectionsData(currentip):
    withoutcurrent = myConnections
    withoutcurrent.remove(currentip)
    data = pickle.dumps(withoutcurrent)
    return data


def startListening():
    ConnectionHandler = threading.Thread(target=handleConnections)
    ConnectionHandler.start()


def is_port_in_use(test):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', test)) == 0


def handleConnections():
    s = socket.socket()

    sys.stdout.flush()

    port = 12346

    if is_port_in_use(port):
        s.bind(('', ports[1]))
        print("socket binded to secndoary port")
        global isLocal
        isLocal = True

        # f(lock, "socket binded to %s" % ports[1])

    else:
        s.bind(('', port))
        global isLocalDef
        isLocalDef = True
        print("socket binded to default port")
        # f(lock, "socket binded to %s" % port)

    s.listen(5)
    print("Listening for connections")
    while True:

        c, addr = s.accept()
        # f(lock, 'Got connection from' + addr[0])

        if addr[0] not in myConnections:
            myConnections.append(addr[0])

        try:
            c.send("pong".encode())
            message = c.recv(1024).decode()

            if message == "get nodes":
                print("Sent all of my known ips to " + addr[0])
                connectionsinstring = "er"
                c.send(getMyConnectionsData(addr[0]))
            elif message.split()[0] == "m_":
                senderName = message.split()[1]
                almreadym = message.replace(senderName, '')
                almreadym = almreadym.replace("m_", '')
                almreadym = almreadym[2:]
                print(senderName + ": " + almreadym + "\n")

            c.close()

        except ConnectionAbortedError:

            print("it was just a ping from", addr[0])


def pingPort(ip, port):
    s.connect(('localhost', port))
    s.send("ping".encode())
    if s.recv(1024).decode() == "pong":

        return True
    else:
        s.close()
        return False


def islocalip(ip):
    if ip == 'localhost' or ip == '127.0.0.1':
        return True
    else:
        return False


def connect(ip):
    global s
    if isLocal and islocalip(ip):
        # print("Connecting on the default port because I am secondary")
        s.connect((ip, port))
        mess = s.recv(1024).decode()
        print("Successfully connected on the default port")

    elif isLocalDef and islocalip(ip):
        # print("Connecting to ip on the secondary port Because the I am default")
        s = socket.socket()
        s.connect((ip, ports[1]))
        mess = s.recv(1024).decode()

        print("Successfully connected on the secondary port")
    else:
        try:
            s.connect((ip, ports[0]))
            mess = s.recv(1024).decode()
            print("Successfully connected on the default port")

        except Exception as e:
            # print("Couldn't connect to ip on the default port")
            s.close()
            s = None
            # print("Connecting to ip on the secondary port...")
            try:
                s = socket.socket()
                s.connect((ip, ports[1]))
                mess = s.recv(1024).decode()
            except Exception as e:
                print(e)
                print("This ", ip, " is probably a wrong ip or it is offline")

        # except socket.gaierror:
        #   print("Couldn't connect to ",ip," it is probably not a node")


if __name__ == '__main__':

    s_print_lock = Lock()

    ports = [12346, 12348, 25525, 89786]

    # myConnections = ['127.0.0.1']

    #  127.0.0.1

    # lock = Lock()
    # Process(target=f, args=(lock, "something lol")).start()
    # f(lock, "hello")

    # firstip = input("What do you want your name to be?")

    myname = input("Enter a name >  ").split()[0]
    firstip = input("Enter the first ip to connect to")

    myConnections.append(firstip)

    startListening()
    time.sleep(4)
    # myConnections.append(firstip)
    sys.stdout.flush()

    while True:
        print(myConnections)
        text = input("What shall we tell the node?\n")

        port = 12346

        if text == "get nodes":

            for ip in myConnections:

                try:
                    connect(ip)
                    s.send("get nodes".encode())
                    response = s.recv(1024)
                    print("the response from " + ip + "  is:")
                    newConnections = pickle.loads(response)


                except:
                    print("Something went wrong")
                s.close()

        elif text == "send":

            message = input("Type your message >  ")
            for ip in myConnections:
                try:
                    connect(ip)
                    ready = "m_ " + myname + " " + message
                    messageinbytes = ready.encode()
                    s.send(messageinbytes)
                except Exception as e:
                    s.close()
                    continue

                s.close()
                print("sent message to ", ip)

        newconnectionnumber = 0
        for address in newConnections:
            if address not in myConnections:
                myConnections.append(address)
                newconnectionnumber = newconnectionnumber + 1
        print("Received ", newconnectionnumber)
