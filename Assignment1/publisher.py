import socket
import sys
import zmq

context = zmq.Context()

IPaddress = sys.argv[1]

while True:
    #sys.stdout.write("Enter IP address: ")
    #sys.stdout.flush()
    #IPaddress = sys.stdin.readline()
    topic = input("Enter topic id:")
    own_strength = input("Enter ownership strength corresponding to that topic id:")

    print("Sending...")

    socket = context.socket(zmq.REQ)
    port="5556"
    socket.connect("tcp://10.0.0.4:%s" % port)
    socket.send("%s %s %i %i" % ("pub",IPaddress, topic, own_strength))

    message = socket.recv()
    print("Received reply [", message, "]")

    sys.stdout.write("Want to enter more topics ? yes/no ")
    sys.stdout.flush()
    choice = sys.stdin.readline()

    if(choice == "no"):
        break

while True:
    choice = input("Do you want to publish ? y/n:")
    if (choice == 'n'):
        break
    topic = input("Enter topic id:")
    message = input("Enter message:")
    socket.send_string("%i %i %i" % ("pub",IPaddress, topic, message))