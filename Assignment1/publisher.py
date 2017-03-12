import socket
import sys
import zmq
from collections import deque


context = zmq.Context()
IPaddress = sys.argv[1]
count=1;

socket = context.socket(zmq.REQ)
port = "5556"
socket.connect("tcp://10.0.0.1:%s" % port)

while True:
    #sys.stdout.write("Enter IP address: ")
    #sys.stdout.flush()
    #IPaddress = sys.stdin.readline()


    #break

    topic = input("Enter topic id:")
    own_strength = input("Enter ownership strength corresponding to that topic id:")
    history = input("Enter history for that topic id:")


    print("Sending...")
    #socket.connect("tcp://10.0.0.1:%s" % port)
    socket.send("%s %s %i %i %i" % ("pub",IPaddress, topic, own_strength,history))

    message = socket.recv()
    print("Received reply:", message)

    #sys.stdout.write("Want to enter more topics ? yes/no ")
    #sys.stdout.flush()
    #choice = sys.stdin.readline()
    choice = raw_input("Want to enter more topics ? y/n: ")

    if(choice == "n"):
        break

while True:
    choice = raw_input("To Publish -> Press 1\n To add more topics -> Press 2\nPress n to exit\n")
    if (choice == 'n'):
        socket.send("%s %s %s %i %i" % ("died", IPaddress, "pub", own_strength, history))
        message = socket.recv()
        print("Received reply:", message)
        break
    elif choice=='1':
        count=count+1;
        topic = input("Enter topic id:")
        #message = input("Enter message:")
        #message = "Kohli hits "+ count +" th ODI century"
        socket.send("%s %s %i %i %i" % ("message", IPaddress, topic,count,0))
        message = socket.recv()
        print("Received reply:", message)
    elif choice == '2':
        topic = input("Enter topic id:")
        own_strength = input("Enter ownership strength corresponding to that topic id:")
        history = input("Enter history for that topic id:")

        print("Sending...")
        # socket.connect("tcp://10.0.0.1:%s" % port)
        socket.send("%s %s %i %i %i" % ("pub", IPaddress, topic, own_strength, history))

        message = socket.recv()
        print("Received reply:", message)