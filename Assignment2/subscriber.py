import sys
import socket
import zmq
import os
from socket import *
from optparse import OptionParser
from network_ctrl import *


#myIPaddress = sys.argv[1]
context = zmq.Context()
#socket = context.socket(zmq.REQ)
# socket.connect ("tcp://localhost:%s" % port)
#port="5555"
#socket.connect("tcp://10.0.0.1:%s" % port)

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

        message = myIPaddress + "@" + str(topic)

        try:
            conn = socket(AF_INET, SOCK_STREAM)
            conn.connect(nodeAddr)
            conn.send(serialize_message(CtrlMessage(ControlMessageTypes.SUBSCRIBER_HERE_FIND_MY_SUCCESSOR, message, 0)))
            data = conn.recv(MAX_REC_SIZE)
            data=unserialize_message(data)
            print("*************My eventservice will be:", data.data)

        finally:
            conn.shutdown(1)
            conn.close()

        try:
            eSnodeIPAddr = (data.data, 5555)
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


            #socket.send("%s %s %i %i %s" % ("sub",myIPaddress, topic, -1,"blah"))
            #message = socket.recv()
            #print(message)

        #socket.close()

    sub_socket = context.socket(zmq.REP)
    #socket = context.socket(zmq.SUB)
    #event_serviceIP = "tcp://10.0.0.1:5557"
    #socket.connect(event_serviceIP)

    #IPfilter = ""
    #IPfilter = myIPaddress

    # Python 2 - ascii bytes to unicode str
    #if isinstance(IPfilter, bytes):
    #    IPfilter = IPfilter.decode('ascii')

    # any subscriber must use the SUBSCRIBE to set a subscription, i.e., tell the
    # system what it is interested in
    #socket.setsockopt_string(zmq.SUBSCRIBE, IPfilter)

    IPInfo_from_pub = context.socket(zmq.REP)
    port = "5555"
    IPInfo_from_pub.bind("tcp://*:%s" % port)

    while True:
        print("Receiving....");
        data = IPInfo_from_pub.recv()
        print("****** Century no:",data)
        IPInfo_from_pub.send("received")

if __name__ == "__main__":
    main()