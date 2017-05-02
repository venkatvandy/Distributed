import collections
import threading
import zmq
import sys
import copy
from collections import deque

context = zmq.Context()

sub_dict = {}
QoSTable = {}
ownership_strength_table = {}
history_table = {}
sub_lock = threading.Lock()
own_lock = threading.Lock()
his_lock = threading.Lock()
sliding_window_lock = threading.Lock()

msg_sliding_window = {}

pub_socket = context.socket(zmq.PUB)
pub_socket.bind("tcp://*:5557")


def store_msg_history(IPaddress,topic,message):
    que = deque()

    sliding_window_lock.acquire()
    #msg_sliding_window.setdefault(key, []).append(val)

    if IPaddress in msg_sliding_window.keys():
        required_table = msg_sliding_window[IPaddress]
        #print("Req table is:",required_table)
        if topic in required_table.keys():
            que.clear()
            for elements in required_table[topic]:
                #print(elements)
                que.append(elements)
            #que=required_table[topic]
            #print("Queueeueue:",que)
            del (msg_sliding_window[IPaddress][topic])
    else:
        que.clear()

    #print("Queue before append:",que)
    que.appendleft(message)
    #print("Queue after append:", que)
    if len(que) == int(history_table[IPaddress][topic]) +1 :
        que.pop()

    temp_table = {}

    if IPaddress in msg_sliding_window.keys():
        temp_table= msg_sliding_window[IPaddress]

    temp_list=[]
    temp_list[:] = []

    for ele in que:
        temp_list.append(ele)

    temp_table[topic] = temp_list
    msg_sliding_window[IPaddress] = temp_table

    print(msg_sliding_window)
    #print(que)
    sliding_window_lock.release()

def register_subscriber(interestedTopicID, IPaddress):
    sub_lock.acquire()
    sub_dict.setdefault(interestedTopicID, []).append(IPaddress)
    sub_lock.release()

def add_to_ownership_stength_table(topic, ownershipStrength, IPaddress):
    own_lock.acquire()
    ownership_strength_table.setdefault(topic, {})[ownershipStrength]=IPaddress
    own_lock.release()

def add_to_history_table(topic, history, IPaddress):
    his_lock.acquire()
    history_table.setdefault(IPaddress, {})[topic]=history
    his_lock.release()


def pub_died(IPaddress):
    own_lock.acquire()
    for topics, table in ownership_strength_table.items():
        for own_str, IP in table.items():
            if IPaddress==IP:
                del table[own_str]
                break
    own_lock.release()

    his_lock.acquire()
    if IPaddress in history_table.keys():
        del(history_table[IPaddress])
    his_lock.release()

    sliding_window_lock.acquire()
    if IPaddress in msg_sliding_window.keys():
        del(msg_sliding_window[IPaddress])
    sliding_window_lock.release()

def send_to_subsciber(IPaddress,topic):

    table ={}

    own_lock.acquire()

    table = ownership_strength_table[topic]
    #print("Table is:",table)

    max_own_strength = max(table.keys(), key=int)
    #print("Max ownership strength is:",max_own_strength)
    #print("Publisher IP address who wants to send is :",IPaddress)
    #print("Publisher who can publish this topic is :", table[max_own_strength])

    if table[max_own_strength] == IPaddress:
        if topic in sub_dict.keys():
            for subscribers in sub_dict[topic]:
                #print("Subcriber is:",subscribers)
                table = {}
                temp_list=[]
                table = msg_sliding_window[IPaddress]
                temp_list = table[topic]
                print("Length is:",len(temp_list))
                #for messages in msg_sliding_window[IPaddress][topic]:
                for messages in temp_list:
                    #print("**Century number is:",messages)
                    pub_socket.send_string("%s %s" % (subscribers, messages));
                    #IPInfo_from_pubandsub.send_string("%s %s" % (subscribers,message));
                    #print("Sent to:", subscribers)
            IPInfo_from_pubandsub.send("Your message has been sent")

        else:
            print("No subscibers for topic:",topic," yet.")

    else:
        IPInfo_from_pubandsub.send("We could not send your message as someone with higher ownership strength exists for this topic")
        print("Cannot let Publisher "+ IPaddress + " publish")

    own_lock.release()


IPInfo_from_pubandsub = context.socket(zmq.REP)
port="5556"
IPInfo_from_pubandsub.bind("tcp://*:%s" % port)

while True:
    print("Receiving....");
    string = IPInfo_from_pubandsub.recv()
    entity,IPaddress,topic, own_strength,history = string.split()
    #print("Received.... "+ entity,IPaddress,topic, own_strength)
    if(entity=="pub"):
        add_to_ownership_stength_table(topic, own_strength,IPaddress)
        add_to_history_table(topic,history,IPaddress)
        #print(ownership_strength_table)
        #print(history_table)
        IPInfo_from_pubandsub.send("You have been registred with us")
    elif(entity=="sub"):
        register_subscriber(topic,IPaddress)
        #print(sub_dict)
        IPInfo_from_pubandsub.send("You have been registred with us")
    elif (entity == "message"):
        message=own_strength
        store_msg_history(IPaddress,topic,message)
        send_to_subsciber(IPaddress,topic)
    elif (entity == "died"):
        entity = topic
        if(entity=="pub"):
            pub_died(IPaddress)
            IPInfo_from_pubandsub.send("bye bye...")