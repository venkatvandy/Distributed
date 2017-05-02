from SubInterface import SubInterface
import sys,time


class SubCallback:
    @staticmethod
    def pub_data_callback(pub_data):
        print("Received data: " + pub_data)

    @staticmethod
    def hist_data_callback(hist):
        #print("History for topic received: ")

        for data in hist:
            print("\t" + data)

# expected terminal args format:
#   <ip:port> <topic_string>

# Initialize data

# error if insufficient number of args
if len(sys.argv) != 4:
    print("Please enter arguments as follows:")
    print("\tYOUR IP, KNOWN EVENT SERVICE IP, TOPIC ")
    sys.exit()

ip_and_port = sys.argv[1]
es_node_ip = "tcp://" + sys.argv[2] + ":5556"
topic = sys.argv[3]

print("\t YOUR IP: " + ip_and_port)
print("\t KNOWN EVENT SERVICE IP: " + es_node_ip)
print("\t TOPIC: " + topic)

print("*************************8")

sub_int = SubInterface()

print("Registering.")

sub_int.register(es_node_ip, topic, ip_and_port)

time.sleep(1)

print("Registration successful")
print()
print("Receiving data...")

sub_int.enter_message_loop(topic, SubCallback)


