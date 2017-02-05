import socket
import sys
import zmq

context = zmq.Context()

# The difference here is that this is a publisher and its aim in life is
# to just publish some value. The binding is as before.
#socket = context.socket(zmq.REQ)
#tcp://*:5555
#tcp://10.0.0.1:5555
#socket.connect("tcp://10.0.0.1:5555")

# keep publishing
while True:
    sys.stdout.write("Enter IP address: ")
    sys.stdout.flush()
    IPaddress = sys.stdin.readline()
    topic = input("Enter topic id:")
    own_strength = input("Enter ownership strength corresponding to that topic id:")

    print("Sending...")
    '''socket.send("%s %i %i" % (IPaddress, topic, own_strength))
    print("Sent...")'''

    #print("Connecting to server...")
    socket = context.socket(zmq.REQ)
    # socket.connect ("tcp://localhost:%s" % port)
    port="5556"
    socket.connect("tcp://10.0.0.4:%s" % port)

    # if len(sys.argv) > 2:
    #    socket.connect ("tcp://localhost:%s" % port1)

    # You have to send a request and then wait for reply.


    #  Do 10 requests, waiting each time for a response
    #for request in range(1, 10):
    #    print("Sending request ", request, "...")
    #    socket.send("10.0.0.2")
        #  Get the reply.
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


'''from EventService import add_to_ownership_stength_table
from EventService import refresh_pub_dict
from EventService import print_pub_table
from EventService import publish_data'''

#ip = socket.gethostbyname(socket.gethostname())

#EventService.register_publisher(ip)


#    add_to_ownership_stength_table(topic, own_strength, IPaddress)

#refresh_pub_dict()
#print_pub_table()

'''EventService.add_to_ownership_stength_table("topic1",10,"10.0.0.1")
EventService.add_to_ownership_stength_table("topic2",5,"10.0.0.1")

EventService.refresh_pub_dict()


EventService.add_to_ownership_stength_table("topic2",6,"10.0.0.2")
EventService.add_to_ownership_stength_table("topic3",7,"10.0.0.2")

EventService.refresh_pub_dict()

EventService.add_to_ownership_stength_table("topic3",8,"10.0.0.3")
EventService.add_to_ownership_stength_table("topic4",3,"10.0.0.3")

EventService.refresh_pub_dict()


EventService.add_to_ownership_stength_table("topic4",2,"10.0.0.4")
EventService.add_to_ownership_stength_table("topic1",5,"10.0.0.4")

EventService.refresh_pub_dict()

EventService.print_pub_table()

#EventService.pub_died("10.0.0.1")

EventService.register_subscriber(1,"10.0.0.5")
EventService.register_subscriber(3,"10.0.0.5")
EventService.register_subscriber(2,"10.0.0.6")
EventService.register_subscriber(4,"10.0.0.6")

EventService.print_sub_table()


EventService.publish("10.0.0.1",)'''

#EventService.match_pub_sub()