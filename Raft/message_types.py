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

class MessageTypes():
    MSG_ACK = 10
    PING = 11
    I_VOTE_FOR_YOU = 12
    I_DO_NOT_VOTE_FOR_YOU = 13
    
