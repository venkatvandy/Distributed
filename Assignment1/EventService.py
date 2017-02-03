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
    '''for ip in ownership_strength_table:
        for topic in ip:
            cur_own_strength = ip[topic]
            for ip2 in ownership_strength_table:
                if topic in ip2 :
                    if ip2[topic] >= cur_own_strength:
                        pub_dict[topic] = ip2'''

    own_lock.acquire()

    if len(ownership_strength_table.keys()) != 1:
        for ip, table in ownership_strength_table.items():
            for topic, own_str in table.items():
                for ip2, table2 in ownership_strength_table.items():
                    for topic2, own_str2 in table2.items():
                        print(topic, own_str, topic2, own_str2)
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
    else:
        for ip, table in ownership_strength_table.items():
            for topic, own_str in table.items():
                pub_lock.acquire()
                pub_dict[topic] = ip
                pub_lock.release()

    own_lock.release()



def publish_data(topic, IPaddress):
    if pub_dict.get(topic, "nomatch") == "nomatch":
        print("Wrong topic id")
    else:
        if pub_dict.get(topic) == IPaddress:
            print("Publishing data.......")


def print_pub_table():
    print(pub_dict)


def print_sub_table():
    print(sub_dict)


# Since we are the subscriber, we use the SUB type of the socket
socket = context.socket(zmq.SUB)

# Here we assume publisher runs locally unless we
# send a command line arg like 10.0.0.1
srv_addr = sys.argv[1] if len(sys.argv) > 1 else "localhost"
connect_str = "tcp://" + srv_addr + ":5556"
socket.connect(connect_str)

while True:
    string = socket.recv()
    print("Receiving....");
    IPaddress,topic, own_strength = string.split()
    add_to_ownership_stength_table(topic, own_strength,IPaddress)
