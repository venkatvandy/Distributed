import TopicDataStore, sys
from ES_Interface import ES_Interface
from ES_zk_interface import ES_zk_interface
import threading

class EventService:

    def __init__(self, my_ip):
        self.ip = my_ip
        self.topicDb = TopicDataStore.TopicDb()
        self.es_interface = ES_Interface(my_ip)
        self.es_zk_interface = ES_zk_interface(my_ip, self.es_interface, self)

        #print "\nStarting Non-Leader thread.... \n"
        non_leader_thread = threading.Thread(target=self.es_interface.enter_message_loop,args=(self, False,))
        non_leader_thread.start()

        self.topicDb.clean_up_expired_publishers()

        self.es_zk_interface.start_election_process()


    def registerPublisher(self,topic,ip,ownership):
        ownerChanged, ownerIP = self.topicDb.registerPublisher(topic, ownership, ip)
        self.topicDb.printTopics()


    def unregisterPublisher(self,topic,ip):
        ownerChanged, ownerIP = self.topicDb.unregisterPublisher(topic, ip)
        self.topicDb.printTopics()


    def storePublisherData(self,topic,ip,data):
        status = self.topicDb.storePublisherData(topic, ip, data)
        self.topicDb.printTopics()
        return status

    def registerSubscriber(self,topic,ip):
        publisherIP = self.topicDb.registerSubscriber(topic, ip)
        self.topicDb.printTopics()

    def unregisterSubscriber(self,topic,ip):
        self.topicDb.unregisterSubscriber(topic, ip)
        self.topicDb.printTopics()

    def getHistoryData(self,topic,numOfValues):
        historyData = self.topicDb.getHistoryData(topic, numOfValues)
        return historyData


    def printEStable(self):
        self.topicDb.printTopics()


    def get_leader(self):
        zk = self.es_zk_interface.get_zookeeper_client()
        node_path = self.es_zk_interface.get_leader_path()
        if zk.exists(node_path):
            leader, stat = zk.get(node_path)
            return leader.decode("utf-8")
        else:
            return None





if len(sys.argv) == 1:
    print("error - must provide self ip")

elif len(sys.argv) == 2:
    EventService(sys.argv[1])

else:
    print("Format error")