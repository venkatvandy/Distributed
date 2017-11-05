import sys
import zmq
from socket import *
from optparse import OptionParser
from network_ctrl import *
from node import Node
from collections import deque

count=0
msg_sliding_window = {}
currentESnodeIPAddrdict = {}
his_dict= {}

#pub_socket = context.socket(zmq.PUB)
#pub_socket.bind("tcp://*:5555")

#conn_a = socket(AF_INET, SOCK_STREAM)
#conn_2 = socket(AF_INET, SOCK_STREAM)
#conn_3 = socket(AF_INET, SOCK_STREAM)
#conn_4 = socket(AF_INET, SOCK_STREAM)

def store_msg_history(topic,message,history):
    que = deque()

    if topic in msg_sliding_window.keys():
        que.clear()
        for elements in msg_sliding_window[topic]:
            # print(elements)
            que.append(elements)
            # que=required_table[topic]
            # print("Queueeueue:",que)
        del (msg_sliding_window[topic])

    que.appendleft(message)
    if len(que) == int(history) +1 :
        que.pop()

    temp_list = []
    temp_list[:] = []

    for ele in que:
        temp_list.append(ele)

    msg_sliding_window[topic] = temp_list

    print(msg_sliding_window)

def send_message_to_sub(sub,msg_sliding_window,topic):
    temp_list = msg_sliding_window[topic]
    print("Length of sliding window is:", len(temp_list))
    # for messages in msg_sliding_window[IPaddress][topic]:
    for messages in temp_list:
        # print("**Century number is:",messages)
        context = zmq.Context()
        pub_socket = context.socket(zmq.REQ)
        port = "5555"
        sub_ip = "tcp://"+str(sub)+":5555"
        pub_socket.connect(sub_ip)

        pub_socket.send_string("%s" % (str(messages)));
        print(pub_socket.recv())

        # IPInfo_from_pubandsub.send_string("%s %s" % (subscribers,message));
        # print("Sent to:", subscribers)


def get_my_successor(topic):
    try:
        message="blah@"+str(topic)
        staticIP=("10.0.0.1",5555)
        conn = socket(AF_INET, SOCK_STREAM)
        conn.connect(staticIP)
        conn.send(serialize_message(CtrlMessage(ControlMessageTypes.PUBLISHER_HERE_FIND_MY_SUCCESSOR, message, 0)))
        data = conn.recv(MAX_REC_SIZE)
        data = unserialize_message(data)
        print("*************My eventservice will be:", data.data)

    finally:
        conn.shutdown(1)
        conn.close()
        print("********Finding successor done*******")
        return(data.data)

def register_with_successor(myIPaddress,topic,own_strength):
    try:
        message = myIPaddress + "@" + str(topic) + "@" + str(own_strength)
        currentESnodeIPAddr = (currentESnodeIPAddrdict[topic],5555)
        print("***********currentESnodeIPAddr",currentESnodeIPAddr)
        #conn_a = socket(AF_INET, SOCK_STREAM)
        conn = socket(AF_INET, SOCK_STREAM)
        print("***********1")
        conn.connect(currentESnodeIPAddr)
        print("***********2")
        conn.send(serialize_message(CtrlMessage(ControlMessageTypes.PUBLISHERHERE_STOREOWN_STRENGTH, message, 0)))
        print("***********3")
        data = conn.recv(MAX_REC_SIZE)
        print("***********4")
        data = unserialize_message(data)
            print("*************Response to topic addition:", data.data)

    finally:
        conn.shutdown(1)
        conn.close()
        print("********Registered to correct successor*******")


######################### Main #########################
def main():
    global thisNode,count

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
        print "Please specify the IP address of the EventService you know with -e option."
        exit(0)

    eventServiceNodeIP = options.existingnode

    if options.myIP is None:
        print "Please specify your IP address with -m option"
        exit(0)

    myIPaddress = options.myIP


#    topic = input("Enter topic id:")
#    own_strength = input("Enter ownership strength corresponding to that topic id:")
#    history = input("Enter history for that topic id:")

#    print("Sending to ...", eventServiceNodeIP)

    while True:
        choice = raw_input("To Publish -> Press 1\n To add more topics -> Press 2\nPress n to exit\n")
        if (choice == 'n'):
            message = myIPaddress

            for keys in currentESnodeIPAddrdict.keys():
                try:
                    IP = (currentESnodeIPAddrdict[keys],5555)
                    conn = socket(AF_INET, SOCK_STREAM)
                    conn.connect(IP)
                    conn.send(serialize_message(CtrlMessage(ControlMessageTypes.PUBLISHERDEAD, message, 0)))
                    data = conn.recv(MAX_REC_SIZE)
                    data = unserialize_message(data)
                    print("******", data.data)

                finally:
                    conn.shutdown(1)
                    conn.close()


        elif choice == '1':
            count = count + 1;
            topic = input("Enter topic id:")
            message = myIPaddress + "@" + str(topic)
            #storing message history
            store_msg_history(topic,str(count),str(his_dict[topic]))

            returned_successor = get_my_successor(topic)
            if(returned_successor!=currentESnodeIPAddrdict[topic]):
                currentESnodeIPAddrdict[topic]=returned_successor
                register_with_successor(myIPaddress, topic, own_strength)

            try:
                #conn2 = socket(AF_INET, SOCK_STREAM)
                IP = (currentESnodeIPAddrdict[topic],5555)
                conn = socket(AF_INET, SOCK_STREAM)
                conn.connect(IP)
                conn.send(serialize_message(CtrlMessage(ControlMessageTypes.PUBLISH, message, 0)))
                data = conn.recv(MAX_REC_SIZE)
                data = unserialize_message(data)
                if(data.data=="no"):
                    print("*************Can I publish ?:", data.data)
                else:
                    list_of_subs = data.data
                    print("************list_of_subs",list_of_subs)
                    no_of_subs=0
                    if(list_of_subs):
                        no_of_subs = list_of_subs.count('@') +1
                    subscribers = list()
                    if(no_of_subs==1):
                        subscribers.append(list_of_subs)
                    else:
                        for i in range(no_of_subs):
                            subscribers.append(list_of_subs.split('@')[i])

                    print("*********Subscriber List:",subscribers);

                    for sub in subscribers:
                        t= Thread(target=send_message_to_sub,args=(sub,msg_sliding_window,topic))
                        t.daemon = True
                        t.start()

            finally:
                conn.shutdown(1)
                conn.close()
                print("******Connection Closed*********")

        elif choice == '2':
            topic = input("Enter topic id:")
            own_strength = input("Enter ownership strength corresponding to that topic id:")
            his_dict[topic] = input("Enter history for that topic id:")

            message = myIPaddress + "@" + str(topic) + "@" + str(own_strength)

            currentESnodeIPAddrdict[topic] = get_my_successor(topic)
            register_with_successor(myIPaddress, topic, own_strength)

            '''print("Sending...")
            try:
                conn = socket(AF_INET, SOCK_STREAM)
                conn.connect(nodeAddr)
                conn.send(serialize_message(CtrlMessage(ControlMessageTypes.PUBLISHER_HERE_FIND_MY_SUCCESSOR, message, 0)))
                data = conn.recv(MAX_REC_SIZE)
                data = unserialize_message(data)
                print("*************My eventservice will be2:", data.data)
            finally:
                conn.shutdown(1)
                conn.close()

            currentESnodeIPAddr = (data.data, 5555)
            message = myIPaddress + "@" + str(topic) + "@" + str(own_strength)

            try :
                #conn4 = socket(AF_INET, SOCK_STREAM)
                conn = socket(AF_INET, SOCK_STREAM)
                conn.connect(currentESnodeIPAddr)
                conn.send(serialize_message(CtrlMessage(ControlMessageTypes.PUBLISHERHERE_STOREOWN_STRENGTH, message, 0)))
                data = conn.recv(MAX_REC_SIZE)
                data = unserialize_message(data)
                print("*************Response to topic addition2:", data.data)
            finally:
                conn.shutdown(1)
                conn.close()

            # socket.connect("tcp://10.0.0.1:%s" % port)
            #socket.send("%s %s %i %i %i" % ("pub", myIPaddress, topic, own_strength, history))
            #message = socket.recv()

            #print("Received reply:", message)'''


if __name__ == "__main__":
    main()