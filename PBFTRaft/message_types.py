#Message Types

class ControlMessageTypes():
    JOIN_NETWORK = 0
    SYNC_NETWORK = 1
    NODE_DROP = 2
    LEADER_PROPOSE = 3
    LEADER_NO = 4
    LEADER_GO = 5
    SEND_VAL = 6
    VAL_ACCEPTED = 7
    ASK_FOR_VOTE = 8
    I_AM_LEADER = 9
    ACCEPT_REQUEST_FROM_CLIENTS = 14
    REPLICATE_LOG = 15
    STARTING_ELECTION_PHASE= 18
    UPDATE_YOUR_TERM_NUMBER_FROM_CURRENT_LEADER = 23
    HEARTBEAT = 25
    CLIENT_INTERVENTION = 30
    CLIENT_INTERVENTION_RECEIVED = 31

class MessageTypes():
    MSG_ACK = 10
    PING = 11
    I_VOTE_FOR_YOU = 12
    I_DO_NOT_VOTE_FOR_YOU = 13
    ELECTION_ALREADY_RUNNING = 19
    NOTED = 20
    LOG_RECORDED = 21
    I_AM_BEHIND = 22
    UPDATED_MY_TERM = 24
    REJECT_NEW_LEADER = 26
    ACCEPT_NEW_LEADER = 27
    NOT_ENOUGH_NODES_IN_THE_SYSTEM = 28
    REPLY_TO_CLIENT = 29
    NEW_LEADER_ELECTED = 32

class ServerStates():
    CANDIDATE = 15
    LEADER = 16
    FOLLOWER = 17