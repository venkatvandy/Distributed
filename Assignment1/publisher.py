import socket
import sys
import zmq

context = zmq.Context()
IPaddress = sys.argv[1]
count=1;

socket = context.socket(zmq.REQ)
port = "5556"

while True:
    #sys.stdout.write("Enter IP address: ")
    #sys.stdout.flush()
    #IPaddress = sys.stdin.readline()

    socket.connect("tcp://10.0.0.1:%s" % port)
    #break

    topic = input("Enter topic id:")
    own_strength = input("Enter ownership strength corresponding to that topic id:")


    print("Sending...")
    #socket.connect("tcp://10.0.0.1:%s" % port)
    socket.send("%s %s %i %i" % ("pub",IPaddress, topic, own_strength))

    message = socket.recv()
    print("Received reply:", message)

    #sys.stdout.write("Want to enter more topics ? yes/no ")
    #sys.stdout.flush()
    #choice = sys.stdin.readline()
    choice = raw_input("Want to enter more topics ? y/n: ")

    if(choice == "n"):
        break

while True:
    choice = raw_input("Do you want to publish ? y/n:")
    if (choice == 'n'):
        break
    count=count+1;
    topic = input("Enter topic id:")
    #message = input("Enter message:")
    #message = "Kohli hits "+ count +" th ODI century"
    socket.send("%s %s %i %i" % ("message", IPaddress, topic,count))