import collections
import threading
#import zmq
import sys

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

def send_to_subsciber(IPaddress,topic):
    table ={}
    table = ownership_strength_table[topic]
    print("Table is:",table)

    '''max_own_strength =0;
    for own_strengths in table:
        if(own_strengths>max_own_strength):
            max_own_strength = own_strengths;'''

    max_own_strength = max(table.keys(), key=int)
    print("Max ownership strength is:",max_own_strength)
    print("Publisher IP address who wants to send is :", IPaddress)
    print("Publisher who can publish this topic is :", table[max_own_strength])

    if table[max_own_strength] == IPaddress:
        print(IPaddress+" sending message to subscriber")
        #print(sub_dict[topic])
        #subscribers_list = sub_dict[topic]
        #for subscribers in subscribers_list:
        #    print("Subcriber:",subscribers)
        for subscribers in sub_dict[topic]:
            print("Subcriber:", subscribers)
    else:
        print("Publisher "+ IPaddress + " tu aukaat badha")

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
                        #break

    pub_lock.acquire()
    for ip, table in ownership_strength_table.items():
        for topic, own_str in table.items():
            if topic not in pub_dict.keys():
                pub_dict[topic]=ip
    pub_lock.release()

    '''pub_lock.acquire()
    for topic in pub_dict:
        if(pub_dict[topic]==None):
            for ip, table in ownership_strength_table.items():
                for topic_o in table:
                    if(topic_o==topic):
                        pub_dict[topic]=ip;

    pub_lock.release()'''

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


'''add_to_ownership_stength_table(1,10,"10.0.0.1")
add_to_ownership_stength_table(2,9,"10.0.0.1")
add_to_ownership_stength_table(3,8,"10.0.0.1")
add_to_ownership_stength_table(4,7,"10.0.0.1")

add_to_ownership_stength_table(3,9,"10.0.0.2")
add_to_ownership_stength_table(4,6,"10.0.0.2")
add_to_ownership_stength_table(5,11,"10.0.0.2")
add_to_ownership_stength_table(6,12,"10.0.0.2")

add_to_ownership_stength_table(1,14,"10.0.0.3")
add_to_ownership_stength_table(3,10,"10.0.0.3")
add_to_ownership_stength_table(5,9,"10.0.0.3")
add_to_ownership_stength_table(6,3,"10.0.0.3")'''

add_to_ownership_stength_table(1,5,"10.0.0.2")
add_to_ownership_stength_table(2,6,"10.0.0.2")

add_to_ownership_stength_table(1,10,"10.0.0.3")
add_to_ownership_stength_table(2,3,"10.0.0.3")

register_subscriber(1,"10.0.0.4")
register_subscriber(2,"10.0.0.5")

print(ownership_strength_table)
print(sub_dict)

send_to_subsciber("10.0.0.2",1)
send_to_subsciber("10.0.0.3",1)

#pub_died("10.0.0.1")
#print(ownership_strength_table)
#refresh_pub_dict()
#print_pub_table()