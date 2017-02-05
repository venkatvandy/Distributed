import sys
import socket
import zmq

context = zmq.Context()
'''EventService.register_subscriber(1, 1)
EventService.register_subscriber(1, 2)
EventService.register_subscriber(2, 2)
EventService.register_subscriber(2, 3)
EventService.register_subscriber(3, 3)
EventService.register_subscriber(3, 4)
EventService.register_subscriber(4, 4)
EventService.register_subscriber(4, 1)

EventService.print_sub_table()'''

socket = context.socket(zmq.REQ)
# socket.connect ("tcp://localhost:%s" % port)
port="5556"
socket.connect("tcp://10.0.0.4:%s" % port)

sys.stdout.write("Enter IP address: ")
sys.stdout.flush()
IPaddress = sys.stdin.readline()

n = input("Enter number of topics you want to subscribe to:");

for i in range(0,n):
    topic = input("Enter topic id:")
    socket.send("%s %s %i %i" % ("sub",IPaddress, topic, -1))
    message = socket.recv()
    print(message)
