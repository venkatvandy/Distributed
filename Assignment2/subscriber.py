import sys
import socket
import zmq
import os
from socket import *
from optparse import OptionParser
from network_ctrl import *


succ_dict = {}
#myIPaddress = sys.argv[1]

#socket = context.socket(zmq.REQ)
# socket.connect ("tcp://localhost:%s" % port)
#port="5555"
#socket.connect("tcp://10.0.0.1:%s" % port)

def find_my_successor(myIPaddress,topic,nodeAddr):
    message = myIPaddress + "@" + str(topic)

    try:
        conn = socket(AF_INET, SOCK_STREAM)
        conn.connect(nodeAddr)
        conn.send(serialize_message(CtrlMessage(ControlMessageTypes.SUBSCRIBER_HERE_FIND_MY_SUCCESSOR, message, 0)))
        data = conn.recv(MAX_REC_SIZE)
        data = unserialize_message(data)
        print("*************My eventservice will be:", data.data)
        #succ_dict[topic] = data.data
        return  data.data

    finally:
        conn.shutdown(1)
        conn.close()

def register_to_successor(myIPaddress,topic,succ):
    try:
        message = myIPaddress + "@" + str(topic)
        eSnodeIPAddr = (succ, 5555)
        print("***********eSnodeIPAddr", eSnodeIPAddr)
        # conn_a = socket(AF_INET, SOCK_STREAM)
        conn = socket(AF_INET, SOCK_STREAM)
        conn.connect(eSnodeIPAddr)
        conn.send(serialize_message(CtrlMessage(ControlMessageTypes.SUBSCRIBER_HERE_STORE_ME, message, 0)))
        data = conn.recv(MAX_REC_SIZE)
        data = unserialize_message(data)
        print("*************Response to topic subscription:", data.data)

    finally:
        conn.shutdown(1)
        conn.close()

def receive_msg_from_pub():
    context = zmq.Context()
    IPInfo_from_pub = context.socket(zmq.REP)
    port = "5555"
    IPInfo_from_pub.bind("tcp://*:%s" % port)

    while True:
        print("Receiving....");
        data = IPInfo_from_pub.recv()
        print("****** Century no:", data)
        IPInfo_from_pub.send("received")

def refresh(myIPaddress,myDict):
    while True:
        time.sleep(60)
        for topic in myDict.keys():
            currentIP = myDict[topic]
            returned_succ = find_my_successor(myIPaddress,topic,("10.0.0.1",5555))
            if(returned_succ!=currentIP):
                myDict[topic]=returned_succ
                register_to_successor(myIPaddress,topic,myDict[topic])

def main():
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
    parser.add_option("-e", "--existingnode",
                      action="store",
                      type="string",
                      dest="existingnode",
                      help="Use an existing node to join an existing network.")
    parser.add_option("-m", "--myIP",
                      action="store",
                      type="string",
                      dest="myIP",
                      help="IP address of the current node.")

    (options, args) = parser.parse_args()

    if options.existingnode is None:
        print "Please specify the IP address of the EventService you know with -e option."
        exit(0)

    eventServiceNodeIP = options.existingnode

    if options.myIP is None:
        print "Please specify your IP address with -m option"
        exit(0)

    myIPaddress = options.myIP


    n = input("Enter number of topics you want to subscribe to:");

    for i in range(0,n):
        topic = input("Enter topic id:")

        nodeAddr = (eventServiceNodeIP, 5555)
        print("***********nodeAddr", nodeAddr)

        succ_dict[topic] = find_my_successor(myIPaddress,topic,nodeAddr)
        register_to_successor(myIPaddress,topic,succ_dict[topic])

    t = Thread(target=receive_msg_from_pub, args=())
    t.daemon = True
    t.start()

    t = Thread(target=refresh, args=(myIPaddress,succ_dict))
    t.daemon = True
    t.start()

    while True:
        choice = raw_input("\nPress n to exit\n")
        if (choice == 'n'):
            message = myIPaddress

            try:
                conn = socket(AF_INET, SOCK_STREAM)
                conn.connect(eSnodeIPAddr)
                conn.send(serialize_message(CtrlMessage(ControlMessageTypes.SUBSCRIBERDEAD, message, 0)))
                data = conn.recv(MAX_REC_SIZE)
                data = unserialize_message(data)
                print("******",data.data)

            finally:
                conn.shutdown(1)
                conn.close()
                break


if __name__ == "__main__":
    main()