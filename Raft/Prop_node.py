from network_ctrl import *
from socket import *
import time
from threading import *
import signal
import sys
import copy
from optparse import OptionParser
import random


class Node():
    ID = 0
    IPAddr = "localhost"
    ctrlPort = 7228
    relayPort = 7229

    def __eq__(self, other):
        if (self.ID == other.ID and self.IPAddr == other.IPAddr and self.ctrlPort
            == other.ctrlPort and self.relayPort == other.relayPort):
            return True
        return False

thisNode = Node()
thisNode.ID = 0
thisNode.IPAddr = "localhost"
thisNode.ctrlPort = 7228
thisNode.relayPort = 7229

currentleaderNode = Node()
log = []
current_index=0
acc_Table = []
drop_table = []
state= ServerStates.FOLLOWER
cluster_count=0
term_number = 0
last_term_i_voted_for = 0
voting_lock = Lock()

def handle_ctrl_connection(conn, addr):
    global thisNode
    global acc_Table
    global drop_table
    global currentleaderNode
    global last_term_i_voted_for
    global term_number
    global current_index
    global state

    data = conn.recv(MAX_REC_SIZE)
    conn.settimeout(DEFAULT_TIMEOUT)

    if data:
        message = unserialize_message(data)


        if message.messageType == ControlMessageTypes.JOIN_NETWORK:
            retCode = 0
            inNode = copy.deepcopy(message.data)
            acc_Table.append(inNode)
            retMsg = CtrlMessage(MessageTypes.MSG_ACK, thisNode, retCode)
            conn.send(serialize_message(retMsg))

        elif message.messageType == ControlMessageTypes.STARTING_ELECTION_PHASE:
            retCode = 0
            if(state == ServerStates.CANDIDATE):
                retMsg = CtrlMessage(MessageTypes.ELECTION_ALREADY_RUNNING, thisNode, retCode)
            else:
                state = ServerStates.FOLLOWER
                term_number = term_number + 1
                retMsg = CtrlMessage(MessageTypes.NOTED, thisNode, retCode)
            conn.send(serialize_message(retMsg))

        elif message.messageType == ControlMessageTypes.ASK_FOR_VOTE:
            retCode = 0
            incoming_term_number  = int(message.extra)
            if incoming_term_number < term_number:
                    retMsg = CtrlMessage(MessageTypes.I_DO_NOT_VOTE_FOR_YOU, thisNode, retCode)
            else:
                print("Voting for term ",message.extra)
                retMsg = CtrlMessage(MessageTypes.I_VOTE_FOR_YOU, thisNode, retCode)
                last_term_i_voted_for = incoming_term_number
            conn.send(serialize_message(retMsg))

        elif message.messageType == ControlMessageTypes.I_AM_LEADER:
            currentleaderNode = message.data
            #term_number = int(message.extra)
            state =  ServerStates.FOLLOWER
            print("---------------------The leader for term ",term_number," is:",message.data.IPAddr,"------------------------")

        elif message.messageType == ControlMessageTypes.REPLICATE_LOG:
            retCode = 0
            log_index = int(message.extra)
            log_value = message.data
            if(current_index == log_index):
                #log[current_index] = message.data
                log.append(log_value)
                print("Log replicated: ", log[current_index])
                current_index = current_index +1
                retMsg = CtrlMessage(MessageTypes.LOG_RECORDED, thisNode, retCode)
            elif (current_index < log_index):
                retMsg = CtrlMessage(MessageTypes.I_AM_BEHIND, current_index, retCode)
            conn.send(serialize_message(retMsg))

        elif message.messageType == ControlMessageTypes.UPDATE_YOUR_TERM_NUMBER_FROM_CURRENT_LEADER:
            retCode = 0
            term_number = message.data
            retMsg = CtrlMessage(MessageTypes.UPDATED_MY_TERM, current_index, retCode)
            conn.send(serialize_message(retMsg))


        elif message.messageType == ControlMessageTypes.ACCEPT_REQUEST_FROM_CLIENTS:
            if (state == ServerStates.LEADER):
                #log[current_index]= term_number
                log.append(term_number)
                print("Log recorded: ",log[current_index])
                for servers in acc_Table:
                    msg = send_ctrl_message_with_ACK(term_number, ControlMessageTypes.REPLICATE_LOG,current_index,servers,DEFAULT_TIMEOUT * 4)
                    if(msg.messageType == MessageTypes.I_AM_BEHIND ):
                        starting_index_of_log_of_lagging_server = msg.data
                        for i in range(starting_index_of_log_of_lagging_server,current_index+1):
                            send_ctrl_message_with_ACK(log[i], ControlMessageTypes.REPLICATE_LOG, i,
                                                       servers, DEFAULT_TIMEOUT * 4)
                        send_ctrl_message_with_ACK(term_number, ControlMessageTypes.UPDATE_YOUR_TERM_NUMBER_FROM_CURRENT_LEADER, i,
                                                   servers, DEFAULT_TIMEOUT * 4)
                current_index = current_index + 1

            else:
                send_ctrl_message_with_ACK(message.data, ControlMessageTypes.ACCEPT_REQUEST_FROM_CLIENTS,0 , currentleaderNode,
                                                     DEFAULT_TIMEOUT * 4)


        elif message.messageType == ControlMessageTypes.SYNC_NETWORK:
            retCode = 0
            a = set()
            b = set()
            for i in acc_Table:
                a.add(i.IPAddr)
            for i in drop_table:
                b.add(i.IPAddr)
            for i in message.data:
                if (i.IPAddr not in a) and (i.IPAddr != thisNode.IPAddr) and (i.IPAddr not in b):
                    acc_Table.append(i)

            retMsg = CtrlMessage(MessageTypes.MSG_ACK, thisNode, retCode)
            conn.send(serialize_message(retMsg))

def join_network(someNode):
    global thisNode
    global acc_Table
    message = send_ctrl_message_with_ACK(thisNode, ControlMessageTypes.JOIN_NETWORK, 0, someNode,
                                         DEFAULT_TIMEOUT * 4)
    if message is None:
        print("Timeout or Error")
        return 0
        # TODO: handle this
        #pass
    print ("return IP", message.data.IPAddr)
    acc_Table.append(message.data)
    return message.data

def stabilization_routine():
    global thisNode
    global acc_Table
    global drop_table

    #time.sleep(random.randint(1,10))
    while 1:
        for i in acc_Table:
            message = send_ctrl_message_with_ACK(acc_Table, ControlMessageTypes.SYNC_NETWORK, 1,i,
                                       DEFAULT_TIMEOUT * 4)
            if message.messageType == ControlMessageTypes.NODE_DROP:
                print("Bu hu")
                drop_table.append(message.data)
                print("Length of drop table: ",len(drop_table))
                acc_Table.remove(i)
                time.sleep(40)
                drop_table.remove(message.data)
                print("Length of drop table: ", len(drop_table))
                print("Removed: ", i.IPAddr)
            #else:
            #    print(message.data)
            time.sleep(random.randint(1,2))

def start_leader_election():
    global thisNode
    global term_number
    global currentleaderNode
    global state
    global voting_lock

    voting_lock.acquire()

    state = ServerStates.CANDIDATE
    cluster_count = len(acc_Table)+1
    print("--------Total servers in cluster:",cluster_count,"-------")
    print("My state is: Candidate")
    count=1

    for server in acc_Table:
        message = send_ctrl_message_with_ACK(thisNode, ControlMessageTypes.STARTING_ELECTION_PHASE, term_number, server,
                                         DEFAULT_TIMEOUT * 4)
        if (message.messageType == MessageTypes.ELECTION_ALREADY_RUNNING):
            state = ServerStates.FOLLOWER
            print("Election already running")
            return

    term_number = term_number + 1

    for server in acc_Table:
        message = send_ctrl_message_with_ACK(thisNode, ControlMessageTypes.ASK_FOR_VOTE, term_number, server,
                                         DEFAULT_TIMEOUT * 4)

        if(message.messageType == MessageTypes.I_VOTE_FOR_YOU):
            count=count+1
            if(count>cluster_count/2):
                state = ServerStates.LEADER
                currentleaderNode=thisNode
                print("------I am the leader for term ",term_number,"------")
                break

    if(state == ServerStates.LEADER):
        for i in acc_Table:
            message = send_ctrl_message_with_ACK(thisNode, ControlMessageTypes.I_AM_LEADER, term_number, i,
                                             DEFAULT_TIMEOUT * 4)
    else:
        print("You cannot become leader")
        state = ServerStates.FOLLOWER

    voting_lock.release()

def display_state_of_server():
    global state

    while 1:
        if(state == ServerStates.FOLLOWER):
            print("My state is : Follower")
        elif(state == ServerStates.LEADER):
            print("My state is : Leader")
        else:
            print("My state is : Candidate")
        time.sleep(5)


def main():
    global thisNode
    global acc_Table
    global drop_table
    global log
    global state


    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
    parser.add_option("-e", "--existingnode",
                      action="store",
                      type="string",
                      dest="existingnode",
                      help="Use an existing node to join an existing network.")
    parser.add_option("-p", "--myIP",
                      action="store",
                      type="string",
                      dest="myIP",
                      help="IP of service.")

    (options, args) = parser.parse_args()

    if options.myIP is None:
        print "Please specify the IP with the -p option."
        exit(0)

    thisNode.IPAddr = options.myIP

    if options.existingnode is not None:
        tmpNode = Node()
        tmpNode.IPAddr = options.existingnode
        join_network(tmpNode)


    print("MY IP ADDRESS IS ", thisNode.IPAddr)

    listenCtrlThread = Thread(target=wait_for_ctrl_connections, args=(thisNode, handle_ctrl_connection))
    listenCtrlThread.daemon = True
    listenCtrlThread.start()
    print "Sleeping for 1 seconds while listening threads are created."
    time.sleep(1)

    stabilizer = Thread(target=stabilization_routine)
    stabilizer.daemon = True
    stabilizer.start()

    display_State_Routine = Thread(target=display_state_of_server)
    display_State_Routine.daemon = True
    display_State_Routine.start()

    # Wait forever
    while 1:
        # The threads should never die
        listenCtrlThread.join(1)
        print("\nOptions:\n")
        print("Press 1 to start leader election\n")
        print("Press 2 to print log status\n")

        j = raw_input("")

        if (j == "1"):
            start_leader_election()

        elif j=="2" :
            for i in log:
                print(i)

        else:
            print("Incorrect Input")

    return 0

if __name__ == "__main__":
    main()
