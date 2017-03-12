import socket
import sys
import zmq
from socket import *
from optparse import OptionParser
from network_ctrl import *
from node import Node

count=0

######################### Main #########################
def main():
    global thisNode,count

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

    #context = zmq.Context()

    #socket = context.socket(zmq.REQ)
    #port = "5556"
    #socket.connect(eventServiceNodeIP % port)

    conn = socket(AF_INET, SOCK_STREAM)
    #conn.settimeout(timeout)
    nodeAddr = (eventServiceNodeIP,5555)

    topic = input("Enter topic id:")
    own_strength = input("Enter ownership strength corresponding to that topic id:")
    history = input("Enter history for that topic id:")
    message = myIPaddress+"@"+str(topic) + "@" +str(own_strength)

    print("Sending to ...", eventServiceNodeIP)
        # socket.connect("tcp://10.0.0.1:%s" % port)
        #socket.send("%s %s %i %i %i" % ("pub", myIPaddress, topic, own_strength, history))
    conn.connect(nodeAddr)
    conn.send(serialize_message(CtrlMessage(ControlMessageTypes.PUBLISHER_HERE, message, 0)))
    data = conn.recv(MAX_REC_SIZE)
    conn.close()
    data=unserialize_message(data)
    print("*************My eventservice will be:", data.data)

    esIP = data.data
    eSnodeIPAddr = (esIP, 5555)
    conna = socket(AF_INET, SOCK_STREAM)
    conna.connect(eSnodeIPAddr)
    conna.send(serialize_message(CtrlMessage(ControlMessageTypes.PUBLISHERHERE_STOREOWN_STRENGTH, message, 0)))
    data = conna.recv(MAX_REC_SIZE)
    conna.close()

    data = unserialize_message(data)
    print("*************Response to topic addition:", data.data)

    #message = socket.recv()
        #print("Received reply:", message)

        # sys.stdout.write("Want to enter more topics ? yes/no ")
        # sys.stdout.flush()
        # choice = sys.stdin.readline()

    #choice = raw_input("Want to enter more topics ? y/n: ")
    #if (choice == "n"):
    #    break

    while True:
        choice = raw_input("To Publish -> Press 1\n To add more topics -> Press 2\nPress n to exit\n")
        if (choice == 'n'):
            conn.connect(eSnodeIPAddr)
            conn.send(serialize_message(CtrlMessage(ControlMessageTypes.PUBLISHERDEAD, message, 0)))
            #socket.send("%s %s %s %i %i" % ("died", myIPaddress, "pub", own_strength, history))
            #message = socket.recv()
            conn.send(serialize_message(CtrlMessage(ControlMessageTypes.PUBLISHER_HERE, message, 0)))
            print("Received reply:", message)
            break
        elif choice == '1':
            count = count + 1;
            topic = input("Enter topic id:")
            message = myIPaddress + "@" + str(topic)
            conn2 = socket(AF_INET, SOCK_STREAM)
            conn2.connect(eSnodeIPAddr)
            conn2.send(serialize_message(CtrlMessage(ControlMessageTypes.PUBLISH, message, 0)))
            data = conn2.recv(MAX_REC_SIZE)
            conn2.close()
            data = unserialize_message(data)
            print("*************Can I publish ?:", data.data)

            # message = input("Enter message:")
            # message = "Kohli hits "+ count +" th ODI century"
            #socket.send("%s %s %i %i %i" % ("message", myIPaddress, topic, count, 0))
            #message = socket.recv()
            #print("Received reply:", message)
        elif choice == '2':
            topic = input("Enter topic id:")
            own_strength = input("Enter ownership strength corresponding to that topic id:")
            history = input("Enter history for that topic id:")

            print("Sending...")
            conn3 = socket(AF_INET, SOCK_STREAM)
            conn3.connect(nodeAddr)
            conn3.send(serialize_message(CtrlMessage(ControlMessageTypes.PUBLISHER_HERE, message, 0)))
            data = conn3.recv(MAX_REC_SIZE)
            conn3.close()
            data = unserialize_message(data)
            print("*************My eventservice will be:", data.data)

            eSnodeIPAddr = (data.data, 5555)
            message = myIPaddress + "@" + str(topic) + "@" + str(own_strength)
            conn4 = socket(AF_INET, SOCK_STREAM)
            conn4.connect(eSnodeIPAddr)
            conn4.send(serialize_message(CtrlMessage(ControlMessageTypes.PUBLISHERHERE_STOREOWN_STRENGTH, message, 0)))
            data = conn4.recv(MAX_REC_SIZE)
            conn4.close()
            data = unserialize_message(data)
            print("*************Response to topic addition:", data.data)

            # socket.connect("tcp://10.0.0.1:%s" % port)
            #socket.send("%s %s %i %i %i" % ("pub", myIPaddress, topic, own_strength, history))
            #message = socket.recv()

            #print("Received reply:", message)


if __name__ == "__main__":
    main()