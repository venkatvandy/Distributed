#Venkataramana

from hash_util import *
from network_ctrl import *
from socket import *
import time
from threading import *
import signal
import sys
import uuid
import copy
from optparse import OptionParser
import random
import logging
import zmq

class Node():
    ID = 0
    #IPAddr = "localhost"
    IPAddr = "10.0.0.1"
    ctrlPort = 7228
    relayPort = 7229
    logFilename = ""

    def __eq__(self, other):
        if (self.ID == other.ID and self.IPAddr == other.IPAddr and self.ctrlPort
            == other.ctrlPort and self.relayPort == other.relayPort):

            return True
        return False

context = zmq.Context()

#Node
thisNode = Node()
#thisNode.ID = hash_str(str(uuid.uuid4()) + str(uuid.uuid4()))
#thisNode.IPAddr = "localhost"
#thisNode.IPAddr = "10.0.0.1"
thisNode.ctrlPort = 7228
thisNode.relayPort = 7229

prevNode = thisNode

#Finger table
fingerTable = []
fingerTableLock = Lock()
prevNodeLock = Lock()
numFingerErrors = 0

successorList = []
sucListLock = Lock()
successorOfflineAttempts = 0

#Network connections
servCtrl = None
servRelay = None
IPInfo_from_pubandsub = context.socket(zmq.REP)
port = "5556"
IPInfo_from_pubandsub.bind("tcp://*:%s" % port)


def exit_signal_handler(signal, frame):
    print "\nClosing Connections."
    logging.info("Closing Connections.")
    graceful_exit(0)
    exit(0)
    
signal.signal(signal.SIGINT, exit_signal_handler)

def graceful_exit(exitCode):
    global servCtrl
    global servRelay
    try:
        servCtrl.shutdown(1)
        servCtrl.close()
    except:
        print "Could not close control port."
        logging.info("Could not close control port.")
    try:
        servRelay.shutdown(1)
        servRelay.close()
    except:
        print "Could not close relay port."
        logging.info("Could not close relay port.")
    exit(exitCode)


def handle_ctrl_connection(conn, addr):
    global thisNode
    data = conn.recv(MAX_REC_SIZE)
    conn.settimeout(DEFAULT_TIMEOUT)

    if data:
        message = unserialize_message(data)
        #print "Recieved - " + str(message.messageType)
        
        if message.messageType == ControlMessageTypes.GET_NEXT_NODE:
            retCode = 0
            tmpNode = find_closest_finger(message.data)
            if tmpNode == thisNode:
                tmpNode = get_immediate_successor_node()
                retCode = 1
            retMsg = CtrlMessage(MessageTypes.MSG_ACK, tmpNode, retCode)
            conn.send(serialize_message(retMsg))
            
        elif message.messageType == ControlMessageTypes.GET_ROOT_NODE_REQUEST:
            print "Got root node request"
            logging.info("Got root node request")
            tmpNode = get_root_node(message.data)
            retMsg = CtrlMessage(MessageTypes.MSG_ACK, tmpNode, 0)
            conn.send(serialize_message(retMsg))
            
        elif message.messageType == ControlMessageTypes.GET_PREDECESSOR:
            retMsg = CtrlMessage(MessageTypes.MSG_ACK, get_predecessor(), 0)
            conn.send(serialize_message(retMsg))
            
        elif message.messageType == ControlMessageTypes.IS_PREDECESSOR:
            print "New pred set"
            logging.info("New pred set")
            farm_successor_list_bg()
            if hash_between(message.data.ID, get_predecessor().ID, thisNode.ID):
                set_predecessor(copy.deepcopy(message.data))
            retMsg = CtrlMessage(MessageTypes.MSG_ACK, 0, 0)
            conn.send(serialize_message(retMsg))
            
        elif message.messageType == ControlMessageTypes.IS_SUCCESSOR:
            farm_successor_list_bg()
            if hash_between(message.data.ID, thisNode.ID, get_immediate_successor_node().ID):
                set_immediate_successor(copy.deepcopy(message.data))
            retMsg = CtrlMessage(MessageTypes.MSG_ACK, 0, 0)
            conn.send(serialize_message(retMsg))
            
        elif message.messageType == ControlMessageTypes.GET_NEXT_NODE_PREDECESSOR:
            retCode = 0
            tmpNode = find_closest_finger(message.data)
            if tmpNode == thisNode:
                retCode = 1
            retMsg = CtrlMessage(MessageTypes.MSG_ACK, tmpNode, retCode)
            conn.send(serialize_message(retMsg))
            
        elif message.messageType == ControlMessageTypes.UPDATE_FINGER_TABLE:
            update_finger_table(message.data, message.extra)
            conn.send(serialize_message(CtrlMessage(MessageTypes.MSG_ACK, 0, 0)))
        elif message.messageType == MessageTypes.PING:
            conn.send(serialize_message(CtrlMessage(MessageTypes.MSG_ACK, 0, 0)))       
        else:
            print "random msg"

    #print "Closing connection."
    conn.shutdown(1)
    conn.close()
    return

def handle_connection(conn, addr):
    data = conn.recv(MAX_REC_SIZE)
    conn.settimeout(DEFAULT_TIMEOUT)
    if data: 
        conn.send(data)
    print "Closing connection."
    logging.info("Closing connection.")
    conn.shutdown(1)
    conn.close()
    return

def get_next_node(node, key):
    message = send_ctrl_message_with_ACK(key, ControlMessageTypes.GET_NEXT_NODE, 0, node, DEFAULT_TIMEOUT)
    if message is None:
        #TODO: handle this - should return successor on failure
        pass
    return (message.extra, message.data)

def get_next_node_predecessor(node, key):
    message = send_ctrl_message_with_ACK(key, ControlMessageTypes.GET_NEXT_NODE_PREDECESSOR, 0, node, DEFAULT_TIMEOUT)
    if message is None:
        #TODO: handle this
        pass
    return (message.extra, message.data)

def get_root_node(key):
    global thisNode
    closestNode = find_closest_finger(key)
    
    if closestNode == thisNode:
        #this is the closest node - return the successor
        return get_immediate_successor_node()

    while 1:
        #get next node on the path
        (retCode, tmpNode) = get_next_node(closestNode, key)

        if retCode == 1:
            return tmpNode

        closestNode = tmpNode
        
    return None

def get_closest_preceding_node(key):
    global thisNode

    closestNode = find_closest_finger(key)
    
    if closestNode == thisNode:
        return thisNode

    while 1:
        #get next node on the path
        (retCode, tmpNode) = get_next_node_predecessor(closestNode, key)

        if retCode == 1:
            return tmpNode

        closestNode = tmpNode
        
    return None
    
def update_finger_table_request(requestNode, updateNode, i):
    data = send_ctrl_message_with_ACK(updateNode, ControlMessageTypes.UPDATE_FINGER_TABLE, i, requestNode, DEFAULT_TIMEOUT * 4)
    if data is None:
        #TODO: handle this
        pass
    return

def update_finger_table(node, i):
    global thisNode
    global fingerTable

    fingerTableLock.acquire()
    fingerEntry = fingerTable[i]
    fingerTableLock.release()
    
    if hash_between(node.ID, thisNode.ID, fingerEntry.ID):
        fingerTableLock.acquire()
        fingerTable[i] = copy.deepcopy(node)
        fingerTableLock.release()
        update_finger_table_request(get_predecessor(), node, i)
    return

def get_root_node_request(requestNode, key):
    message = send_ctrl_message_with_ACK(key, ControlMessageTypes.GET_ROOT_NODE_REQUEST, 0, requestNode, DEFAULT_TIMEOUT * 4)
    if message is None:
        #TODO: handle this
        pass
    return message.data

def get_immediate_successor_node():
    global fingerTable
    fingerTableLock.acquire()
    ret = copy.deepcopy(fingerTable[0])
    fingerTableLock.release()
    return ret

def get_node_predecessor(requestNode):
    message = send_ctrl_message_with_ACK(0, ControlMessageTypes.GET_PREDECESSOR, 0, requestNode, DEFAULT_TIMEOUT)
    if message is None:
        #TODO: handle this
        return None
    return message.data

def inform_new_predecessor(node):
    global thisNode
    data = send_ctrl_message_with_ACK(thisNode, ControlMessageTypes.IS_PREDECESSOR, 0, node, DEFAULT_TIMEOUT)
    if data is None:
        #TODO: handle this
        pass
    return

def inform_new_successor(node):
    global thisNode
    data = send_ctrl_message_with_ACK(thisNode, ControlMessageTypes.IS_SUCCESSOR, 0, node, DEFAULT_TIMEOUT)
    if data is None:
        #TODO: handle this
        pass
    return

def update_others():
    global thisNode
    for i in range(0, KEY_SIZE):
        searchKey = generate_reverse_lookup_key_with_index(thisNode.ID, i)
        tmpNode = get_closest_preceding_node(searchKey)
        update_finger_table_request(tmpNode, thisNode, i)
    return
        

def join_network(existingNode):
    global fingerTable
    global thisNode
    
    k = generate_lookup_key_with_index(thisNode.ID, 0)

    tmpNode = get_root_node_request(existingNode, k)
    if tmpNode is None:
        return -1

    set_immediate_successor(tmpNode)

    nextNodesPred = get_node_predecessor(tmpNode)
    set_predecessor(nextNodesPred)
    set_finger_table_to_successor()
    inform_new_successor(nextNodesPred)
    inform_new_predecessor(tmpNode)

    for i in range(1, KEY_SIZE):
        searchKey = generate_lookup_key_with_index(thisNode.ID, i)
        
        fingerTableLock.acquire()
        prevFingerNode = copy.deepcopy(fingerTable[i-1])
        fingerTableLock.release()
        
        if hash_between(searchKey, thisNode.ID, prevFingerNode.ID):
            fingerTableLock.acquire()
            fingerTable[i] = copy.deepcopy(fingerTable[i-1])
            fingerTableLock.release()
        else:
            print "Making request for fingertable construction"
            logging.info("Making request for fingertable construction")
            retNode = get_root_node_request(existingNode, searchKey)
            fingerTableLock.acquire()
            fingerTable[i] = copy.deepcopy(retNode)
            fingerTableLock.release()

    #fingerTableLock.release()
    print "Updating Others"
    logging.info("Updating Others")
    update_others()
    return 0

def check_node_alive():
    return True

def initialise_finger_table():
    global fingerTable
    fingerTableLock.acquire()
    for i in range(0, KEY_SIZE):
        tmpNode = copy.deepcopy(thisNode)
        fingerTable.append(tmpNode)
    fingerTableLock.release()
    return

def set_finger_table_to_successor():
    fingerTableLock.acquire()
    for i in range(1, KEY_SIZE):
        fingerTable[i] = copy.deepcopy(fingerTable[0])
    fingerTableLock.release()
    return
    

def print_finger_table():
    global thisNode
    fingerTableLock.acquire()
    for i in range(0, KEY_SIZE):
        #print str(fingerTable[i].ID.key) + " " + str(fingerTable[i].IPAddr) + ":" + str(fingerTable[i].ctrlPort) + " " + str(generate_lookup_key_with_index(thisNode.ID, i).key)
        logging.info(str(fingerTable[i].ID.key) + " " + str(fingerTable[i].IPAddr) + ":" + str(fingerTable[i].ctrlPort) + " " + str(generate_lookup_key_with_index(thisNode.ID, i).key))
    fingerTableLock.release()
    print "Pred: " + get_predecessor().ID.key
    logging.info("Pred: "+ get_predecessor().ID.key)
    return

def find_closest_finger(key):
    global fingerTable
    global thisNode
    fingerTableLock.acquire()
    for i in range((KEY_SIZE - 1), -1, -1):
        if hash_between(fingerTable[i].ID, thisNode.ID, key):
            tmpNode = copy.deepcopy(fingerTable[i])
            fingerTableLock.release()

            if send_ping_message(tmpNode) == False:
                return get_immediate_successor_node()
            return tmpNode

    fingerTableLock.release()
    return copy.deepcopy(thisNode)

def set_immediate_successor(node):
    global fingerTable
    fingerTableLock.acquire()
    fingerTable[0] = copy.deepcopy(node)
    fingerTableLock.release()
    return

def set_predecessor(node):
    global prevNode
    prevNodeLock.acquire()
    prevNode = copy.deepcopy(node)
    prevNodeLock.release()
    return

def get_predecessor():
    global prevNode
    prevNodeLock.acquire()
    ret = copy.deepcopy(prevNode)
    prevNodeLock.release()
    return ret


def update_entire_finger_table():
    set_finger_table_to_successor()
    for i in range(1, KEY_SIZE):
        searchKey = generate_lookup_key_with_index(thisNode.ID, i)

        fingerTableLock.acquire()
        prevFingerNode = copy.deepcopy(fingerTable[i-1])
        fingerTableLock.release()
        
        if hash_between(searchKey, thisNode.ID, prevFingerNode.ID):
            fingerTableLock.acquire()
            fingerTable[i] = copy.deepcopy(fingerTable[i-1])
            fingerTableLock.release()
        else:
            print "Making request for fingertable construction"
            logging.info("Making request for fingertable construction")
            retNode = get_root_node_request(get_immediate_successor_node(), searchKey)
            fingerTableLock.acquire()
            fingerTable[i] = copy.deepcopy(retNode)
            fingerTableLock.release()
    return

def initialise_successor_list():
    global successorList
    global thisNode
    sucListLock.acquire()
    for i in range(0, 30):
        successorList.append(copy.deepcopy(thisNode))
    sucListLock.release()
    return

def farm_successor_list():
    global thisNode
    global successorList
    global fingerTable
    tmpId = thisNode.ID
    print "Farming successor list"
    logging.info("Farming successor list")
    for i in range(0, 15):
        node = get_root_node(generate_lookup_key_with_index(tmpId, 0))
        sucListLock.acquire()
        successorList[i] = copy.deepcopy(node)
        sucListLock.release()
        tmpId = node.ID
    for i in range(15,30):
        sucListLock.acquire()
        fingerTableLock.acquire()
        successorList[i] = copy.deepcopy(fingerTable[130 + i])
        fingerTableLock.release()
        sucListLock.release()
    print "Finished farming successor list"
    logging.info("Finished farming successor list")
    return

def farm_successor_list_bg():
    farmThread = Thread(target=farm_successor_list)
    farmThread.daemon = True
    farmThread.start()

def get_next_successor():
    global successorList
    global successorOfflineAttempts
    sucListLock.acquire()
    for m in successorList:
        print m.ID.key
        logging.info(m.ID.key)
    successorOfflineAttempts += 1
    if successorOfflineAttempts > 30:
        farm_successor_list_bg()
        successorOfflineAttempts = 0
    tmp = successorList.pop(0)
    successorList.append(tmp)
    ret = copy.deepcopy(successorList[0])
    sucListLock.release()
    return ret

def stabilize_predecessor_routine():
    global thisNode
    while 1:
        time.sleep(2)
        if send_ping_message(get_predecessor()) == False:
            set_predecessor(thisNode)
            print "Predecessor is down."
            logging.info("Predecessor is down.")

def ping_and_update(node, successor):
    if send_ping_message(node) == False:
        if send_ping_message(node) == False:
            print "Node is officially offline... sending out update message"
            logging.info("Node is officially offline... sending out update message")
            for i in range(0, KEY_SIZE):
                searchKey = generate_reverse_lookup_key_with_index(node.ID, i)
                tmpNode = get_closest_preceding_node(searchKey)
                update_finger_table_request(tmpNode, node, i)
    return

def stabilization_routine():
    global thisNode
    global successorOfflineAttempts
    sucCount = 0

    farm_successor_list()

    predStabilizationThread = Thread(target=stabilize_predecessor_routine)
    predStabilizationThread.daemon = True
    predStabilizationThread.start()

    offlineList = []

    while 1:
        time.sleep(2)

        if sucCount > 150:
            farm_successor_list_bg()
            sucCount = 0
            successorOfflineAttempts = 0
    
        suc = get_immediate_successor_node()
        pre = get_node_predecessor(suc)
        if pre is None:
            print "Successor seems to be offline."
            logging.info("Successor seems to be offline.")
            suc = get_next_successor()
            set_immediate_successor(suc)
            print "New succ set to " + suc.ID.key
            logging.info("New succ set to " + suc.ID.key)
            continue
        
        if not thisNode == pre:
            if hash_between(thisNode.ID, pre.ID, suc.ID):
                print "Updating successors predecessor"
                logging.info("Updating successors predecessor")
                inform_new_predecessor(suc)
            else:
                print "Successor is wrong"
                logging.info("Successor is wrong")
                suc = get_next_successor()
                set_immediate_successor(suc)
                print "New succ set to " + suc.ID.key
                logging.info("New succ set to " + suc.ID.key)
        
            
def fix_fingers_stabilization_routine():
    global fingerTable
    global numFingerErrors

    count = 0
    numFingerErrors = 0
    
    while 1:
        time.sleep(random.randint(25, 50))
        i = random.randint(1, 159)
        print "Updating finger " + str(i)
        logging.info("Updating finger " + str(i))
        searchKey = generate_lookup_key_with_index(thisNode.ID, i)
        retNode = get_root_node(searchKey)
        
        fingerTableLock.acquire()
        tmpFinger = copy.deepcopy(fingerTable[i])
        fingerTableLock.release()
        if not tmpFinger == retNode:
            print "Finger is wrong - changing finger."
            logging.info("Finger is wrong - changing finger.")
            if numFingerErrors > 1:
                print "Detected two finger table errors in a row - refreshing finger table."
                logging.info("Detected two finger table errors in a row - refreshing finger table.")
                update_entire_finger_table()
                numFingerErrors = 0
            else:
                fingerTableLock.acquire()
                fingerTable[i] = copy.deepcopy(retNode)
                fingerTableLock.release()
                numFingerErrors+=1
        else:
            numFingerErrors = 0

        print "Finished updating finger"
        logging.info("Finished updating finger")

        if count > 60:
            print "Performing an entire refresh of the finger table"
            logging.info("Performing an entire refresh of the finger table")
            update_entire_finger_table()
            count = 0
        else:
            count+=1

def process_publishers():
    while True:
        print("Receiving publishers...");
        string = IPInfo_from_pubandsub.recv()
        entity, IPaddress, topic, own_strength, history = string.split()
        # print("Received.... "+ entity,IPaddress,topic, own_strength)
        if (entity == "pub"):
            add_to_ownership_stength_table(topic, own_strength, IPaddress)
            add_to_history_table(topic, history, IPaddress)
            # print(ownership_strength_table)
            # print(history_table)
            IPInfo_from_pubandsub.send("You have been registred with us")
        elif (entity == "sub"):
            register_subscriber(topic, IPaddress)
            # print(sub_dict)
            IPInfo_from_pubandsub.send("You have been registred with us")
        elif (entity == "message"):
            message = own_strength
            store_msg_history(IPaddress, topic, message)
            send_to_subsciber(IPaddress, topic)
        elif (entity == "died"):
            entity = topic
            if (entity == "pub"):
                pub_died(IPaddress)
                IPInfo_from_pubandsub.send("bye bye...")

def main():
    global thisNode


    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
    parser.add_option("-e", "--existingnode",
                      action="store",
                      type="string",
                      dest="existingnode",
                      help="Use an existing node to join an existing network.")
    parser.add_option("-p", "--controlport",
                      action="store",
                      type="int",
                      dest="controlport",
                      help="Port to listen on for network control.")
    parser.add_option("-m", "--myIP",
                      action="store",
                      type="string",
                      dest="myIP",
                      help="IP address of the current node.")

    (options, args) = parser.parse_args()

    if options.controlport is None:
        print "Please specify the port to listen on with the -p option."
        exit(0)

    thisNode.ctrlPort = options.controlport

    if options.myIP is None:
        print "Please specify your ip address using -m option."
        exit(0)

    thisNode.IPAddr = options.myIP
    thisNode.logFilename = "log_" + thisNode.IPAddr + ".log"
    thisNode.ID = hash_str(thisNode.IPAddr)
    logging.basicConfig(filename=thisNode.logFilename, filemode='w', level=logging.DEBUG)

    print "Set listening port to " + str(options.controlport)
    logging.info("Set listening port to " + str(options.controlport))

    print "Set my IP to " + options.myIP
    logging.info("Set my IP to " + options.myIP)

    print "This ID: " + thisNode.ID.key
    logging.info("This ID: " + thisNode.ID.key)

    initialise_finger_table()
    initialise_successor_list()
    set_predecessor(copy.deepcopy(thisNode))


    listenCtrlThread = Thread(target=wait_for_ctrl_connections, args=(thisNode,handle_ctrl_connection))
    listenCtrlThread.daemon = True
    listenCtrlThread.start()

    print "Sleeping for 1 seconds while listening threads are created."
    logging.info("Sleeping for 1 seconds while listening threads are created.")
    time.sleep(1)

    if options.existingnode is not None:
        tmpNode = Node()
        tmpNode.IPAddr = options.existingnode.split(":")[0]
        tmpNode.ctrlPort = int(options.existingnode.split(":")[1])
        print("Joining using existing node:"+tmpNode.IPAddr+":"+str(tmpNode.ctrlPort))
        logging.info("Joining using existing node:"+tmpNode.IPAddr+":"+str(tmpNode.ctrlPort))
        join_network(tmpNode)

    
    print "Joined the network"
    logging.info("Joined the network")

    print "This ID: " + thisNode.ID.key
    logging.info("This ID: " + thisNode.ID.key)

    print_finger_table()

    fingerUpdater = Thread(target=fix_fingers_stabilization_routine)
    fingerUpdater.daemon = True
    fingerUpdater.start()

    stabilizer = Thread(target=stabilization_routine)
    stabilizer.daemon = True
    stabilizer.start()


    joiningPublishers = Thread(target=process_publishers)
    joiningPublishers.daemon = True
    joiningPublishers.start()

    while 1:
        listenCtrlThread.join(1)
        raw_input("Press enter to print finger table...")
        print_finger_table()
        
    return 0

if __name__ == "__main__":
    main()