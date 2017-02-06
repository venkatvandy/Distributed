import collections
import threading
import zmq
import sys

context = zmq.Context()

sub_dict = {}
ownership_strength_table = {}
sub_lock = threading.Lock()
own_lock = threading.Lock()


def register_subscriber(interestedTopicID, IPaddress):
    sub_lock.acquire()
    sub_dict.setdefault(interestedTopicID, []).append(IPaddress)
    sub_lock.release()


def add_to_ownership_stength_table(topic, ownershipStrength, IPaddress):
    own_lock.acquire()
    ownership_strength_table.setdefault(topic, {})[ownershipStrength]=IPaddress
    own_lock.release()

def pub_died(IPaddress):
    own_lock.acquire()
    for topics, table in ownership_strength_table.items():
        for own_str, IP in table.items():
            if IPaddress==IP:
                del table[own_str]
                break
    own_lock.release()

def send_to_subsciber(IPaddress,topic,message):

    table ={}

    own_lock.acquire()

    table = ownership_strength_table[topic]
    max_own_strength =0;
    for own_strengths in table:
        if(own_strengths>max_own_strength):
            max_own_strength = own_strengths;

    if table[max_own_strength] == IPaddress:
        print(IPaddress+" is sending message to subscriber")
        pub_socket = context.socket(zmq.PUB)
        pub_socket.bind("tcp://*:5557")
        for subscribers in sub_dict[topic]:
            pub_socket.send(subscribers,"Kohli hits " + message + " th ODI century.");

    else:
        print("Publisher "+ IPaddress + " tu aukaat badha apni")

    own_lock.release()


IPInfo_from_pubandsub = context.socket(zmq.REP)
port="5556"
IPInfo_from_pubandsub.bind("tcp://*:%s" % port)

while True:
    print("Receiving....");
    string = IPInfo_from_pubandsub.recv()
    entity,IPaddress,topic, own_strength = string.split()
    print("Received.... "+ entity,IPaddress,topic, own_strength)
    if(entity=="pub"):
        add_to_ownership_stength_table(topic, own_strength,IPaddress)
        print(ownership_strength_table)
    elif(entity=="sub"):
        register_subscriber(topic,IPaddress)
        print(sub_dict)
    elif (entity == "message"):
        message=own_strength
        send_to_subsciber(IPaddress,topic,message)
    IPInfo_from_pubandsub.send("You have been registred with us")