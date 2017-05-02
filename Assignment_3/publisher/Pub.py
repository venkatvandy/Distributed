import sys
import time

from PubInterface import PubInterface

# expected terminal args format:
#   <ip:port> <topic_string> <ownership> <update_interval> <data_string>

# Initialize data

# error if insufficient number of args
if len(sys.argv) != 7:
    print("Please enter arguments as follows:")
    print("\tYOUR IP, KNOWN EVENT SERVICE IP, TOPIC, OWNERSHIP STRENGTH, DATA, UPDATE TIME INTERAVAL")
    sys.exit()

my_ip_and_port = sys.argv[1]
es_node_ip = "tcp://" + sys.argv[2] + ":5555"
topic = sys.argv[3]
ownership_value = sys.argv[4]
data = sys.argv[5]
update_int = int(sys.argv[6])

#print("Data initialized to following:")
#print("\t YOUR IP: " + my_ip_and_port)
#print("\t KNOWN EVENT SERVICE IP " + es_node_ip)
#print("\t TOPIC: " + topic)
#print("\t OWNERSHIP STRENGTH: " + ownership_value)
#print("\t DATA: " + data)
#print("\t UPDATE INTERAVAL: " + str(update_int))

pub_interface = PubInterface()

print("Registering...")

pub_interface.register(es_node_ip, topic, my_ip_and_port, ownership_value)

time.sleep(1)

print("Registration Successful")
#print()
print("Sending data...")

pub_interface.publish_loop(data, update_int)