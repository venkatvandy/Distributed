from kazoo.client import KazooClient
import logging, threading, json


LEADER_PATH = "/ass3/leader"
HOST_IP = '10.0.0.1:2181'


class ES_zk_interface:

    def __init__(self, my_ip, es_interface, es_callback):
        self.ip = my_ip
        self.es_callback = es_callback
        self.es_interface = es_interface
        self.zk = KazooClient(hosts=HOST_IP)
        self.zk.start()

        self.zk.ensure_path("/ass3")

    def start_election_process(self):
        print "Starting Election process"
        #print("Previous Leader: %s" % (self.es_callback.get_leader()))
        election = self.zk.Election("/electionpath", self.ip)
        election.run(self.leader_function)



    def leader_function(self):
        print "Won the election: " + str(self.ip)
        if self.zk.exists(LEADER_PATH):
            self.zk.set(LEADER_PATH, self.ip)
        else:
            self.zk.create(LEADER_PATH, self.ip)

        #print "\nStarting Leader thread.... \n"
        self.es_interface.enter_message_loop(self.es_callback, True)


    def get_zookeeper_client(self):
        return self.zk

    def get_leader_path(self):
        return LEADER_PATH


