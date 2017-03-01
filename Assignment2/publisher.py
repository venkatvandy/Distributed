import socket
import sys
import zmq
from optparse import OptionParser


######################### Main #########################
def main():
    global thisNode

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
        print "Please specify the IP address of the EventService you want to register with -e option."
        exit(0)

    eventServiceNodeIP = "tcp://" +options.existingnode + ":"

    if options.myIP is None:
        print "Please specify your IP address with -m option"
        exit(0)

    myIPaddress = options.myIP

    context = zmq.Context()

    count = 1;

    socket = context.socket(zmq.REQ)
    port = "5556"
    socket.connect(eventServiceNodeIP % port)

    while True:
        # sys.stdout.write("Enter IP address: ")
        # sys.stdout.flush()
        # IPaddress = sys.stdin.readline()


        # break

        topic = input("Enter topic id:")
        own_strength = input("Enter ownership strength corresponding to that topic id:")
        history = input("Enter history for that topic id:")

        print("Sending to ...", eventServiceNodeIP)
        # socket.connect("tcp://10.0.0.1:%s" % port)
        socket.send("%s %s %i %i %i" % ("pub", myIPaddress, topic, own_strength, history))

        message = socket.recv()
        print("Received reply:", message)

        # sys.stdout.write("Want to enter more topics ? yes/no ")
        # sys.stdout.flush()
        # choice = sys.stdin.readline()
        choice = raw_input("Want to enter more topics ? y/n: ")

        if (choice == "n"):
            break

    while True:
        choice = raw_input("To Publish -> Press 1\n To add more topics -> Press 2\nPress n to exit\n")
        if (choice == 'n'):
            socket.send("%s %s %s %i %i" % ("died", myIPaddress, "pub", own_strength, history))
            message = socket.recv()
            print("Received reply:", message)
            break
        elif choice == '1':
            count = count + 1;
            topic = input("Enter topic id:")
            # message = input("Enter message:")
            # message = "Kohli hits "+ count +" th ODI century"
            socket.send("%s %s %i %i %i" % ("message", myIPaddress, topic, count, 0))
            message = socket.recv()
            print("Received reply:", message)
        elif choice == '2':
            topic = input("Enter topic id:")
            own_strength = input("Enter ownership strength corresponding to that topic id:")
            history = input("Enter history for that topic id:")

            print("Sending...")
            # socket.connect("tcp://10.0.0.1:%s" % port)
            socket.send("%s %s %i %i %i" % ("pub", myIPaddress, topic, own_strength, history))

            message = socket.recv()
            print("Received reply:", message)

    return 0


if __name__ == "__main__":
    main()