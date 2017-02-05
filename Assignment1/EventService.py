import collections
import threading
import zmq
import sys

context = zmq.Context()

pub_dict = {}
sub_dict = {}
ownership_strength_table = {}
sub_lock = threading.Lock()
own_lock = threading.Lock()
pub_lock = threading.Lock()


def register_subscriber(interestedTopicID, IPaddress):
    sub_lock.acquire()
    sub_dict.setdefault(interestedTopicID, []).append(IPaddress)
    sub_lock.release()


def add_to_ownership_stength_table(topic, ownershipStrength, IPaddress):
    own_lock.acquire()
    ownership_strength_table.setdefault(IPaddress, {})[topic] = ownershipStrength
    own_lock.release()
    refresh_pub_dict()

def pub_died(IPaddress):
    own_lock.acquire()
    del ownership_strength_table[IPaddress]
    own_lock.release()
    refresh_pub_dict()


def refresh_pub_dict():

    own_lock.acquire()

    for ip, table in ownership_strength_table.items():
        for topic, own_str in table.items():
            for ip2, table2 in ownership_strength_table.items():
                for topic2, own_str2 in table2.items():
                    # print(topic, own_str, topic2, own_str2)
                    if (topic2 == topic and own_str2 > own_str):
                        pub_lock.acquire()
                        pub_dict[topic2] = ip2
                        pub_lock.release()
                        break
                    elif (topic2 == topic and own_str2 < own_str):
                        pub_lock.acquire()
                        pub_dict[topic2] = ip
                        pub_lock.release()
                        break

    own_lock.release()

def publish_data(topic, IPaddress):
    if pub_dict.get(topic, "nomatch") == "nomatch":
        print("Wrong topic id")
    else:
        if pub_dict.get(topic) == IPaddress:
            print("Publishing data.......")


# Since we are the subscriber, we use the SUB type of the socket
IPInfo_from_pubandsub = context.socket(zmq.REP)
#tcp://10.0.0.2:5555
#tcp://*:5555
port="5556"
IPInfo_from_pubandsub.bind("tcp://*:%s" % port)


#msg_to_subscribers = context.socket(zmq.XPUB)
#msg_to_subscribers.bind("tcp://10.0.0.1:5556")

# Here we assume publisher runs locally unless we
# send a command line arg like 10.0.0.1

'''srv_addr = sys.argv[1] if len(sys.argv) > 1 else "localhost"
connect_str = "tcp://" + srv_addr + ":5556"
socket.connect(connect_str)'''

while True:
    print("Receiving....");
    string = IPInfo_from_pubandsub.recv()
    entity,IPaddress,topic, own_strength = string.split()
    print("Received.... "+ entity,IPaddress,topic, own_strength)
    if(entity=="pub"):
        add_to_ownership_stength_table(topic, own_strength,IPaddress)
        print(ownership_strength_table)
        print(pub_dict)
    elif(entity=="sub"):
        register_subscriber(topic,IPaddress)
        print(sub_dict)
    IPInfo_from_pubandsub.send("You have been registred with us %s")