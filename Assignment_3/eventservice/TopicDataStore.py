import time, threading


class TopicInfo:

    def __init__(self):
        self.publishers = {}
        self.sub_list = []
        self.history = []
        self.owner = {}
        self.TOPIC_HISTORY = 5
        self.pub_status = {}

    def set_pub_status(self, ip, status):
        self.pub_status[ip] = status

    def get_pub_status_ip(self, ip):
        return self.pub_status[ip]

    def get_all_pub_status(self):
        return self.pub_status

    def delete_pub_status(self,ip):
        if bool(self.pub_status):
            self.pub_status.pop(ip)

    def addPublisher(self,ip,ownership):
        self.publishers[ip] = ownership

    def deletePublisher(self,ip):
        if bool(self.publishers):
            self.publishers.pop(ip)

    def getPublishers(self):
        for i in self.publishers.keys():
            print("------------------------")
            print("Pub IP: ", i)
            print("Pub Strength: ", self.publishers[i])
            print("------------------------")
        #return self.publishers
        #return ""
        return

    def addSubscriber(self,ip):
        self.sub_list.append(ip)

    def deleteSubscriber(self,ip):
        if self.sub_list:
            self.sub_list.remove(ip)

    def getSubscribers(self):
        return self.sub_list

    def archiveData(self,data):
        if len(self.history) < self.TOPIC_HISTORY:
            self.history.append(data)
        else:
            self.history.pop(0)

    def getHistory(self,requestValue):
        print "Total request value:" + str(requestValue)
        print "bool result: " + str(requestValue <= self.TOPIC_HISTORY)
        if requestValue <= self.TOPIC_HISTORY:
            hist = []
            for index in range(requestValue):
                print "Getting value:" + str(index)
                item = self.history[index]
                hist.append(item)
            return hist

        else:
            return self.history

    def printHistory(self):
        return self.history

    def setOwner(self,ip,ownership):
        if not(ip == "null" and ownership == -1):
            self.owner["ip"] = ip
            self.owner["ownership"] = ownership

        else:
            self.owner = {}

    def getOwner(self):
        return self.owner

    def checkOwnership(self,ip):
        if self.owner["ip"] == ip:
            return True
        else:
            return False


class TopicDb:

    def __init__(self):
        self.topics = {}


    def printTopics(self):
        for topic,topicInfo in self.topics.iteritems():
            print "Topic: " + topic
            #print "Publishers: " + str(topicInfo.getPublishers())
            topicInfo.getPublishers()
            #print "Ownership Strength: " + str(topicInfo.getOwner())
            print "Subscribers: " + str(topicInfo.getSubscribers())
            print "Sliding window: " + str(topicInfo.printHistory())

            #print "Publisher status: " + str(topicInfo.get_all_pub_status())


    def clean_up_expired_publishers(self):
        expired_publishers = self.get_expired_publishers()
        for pub_ip in expired_publishers.keys():
            topic = expired_publishers[pub_ip]
            self.unregisterPublisher(topic, pub_ip)
            print "Removed dead publisher."

        self.printTopics()

        threading.Timer(10, self.clean_up_expired_publishers).start()


    def get_expired_publishers(self):
        expired_publishers = {}
        for topic, topicInfo in self.topics.iteritems():
            pub_status = topicInfo.get_all_pub_status()
            curr_time = time.time()

            for pub_ip in pub_status.keys():
                status = pub_status[pub_ip]
                time_elapsed = curr_time - status
                if time_elapsed >= 12:
                    expired_publishers[pub_ip] = topic

        return expired_publishers



    def registerPublisher(self,topic, ownership_value, ip):
        # if bool(self.topics):
        ownerChanged = False
        ownerIP = "null"
        if topic in self.topics.keys():
            topicInfo = self.topics[topic]
        else:
            topicInfo = TopicInfo()

        topicInfo.addPublisher(ip, ownership_value)
        topicInfo.set_pub_status(ip, time.time())
        owner = topicInfo.getOwner()
        if not bool(owner) or ownership_value > owner.get("ownership"):
            topicInfo.setOwner(ip,ownership_value)
            ownerChanged = True
            ownerIP = ip

        self.topics[topic] = topicInfo
        return ownerChanged,ownerIP



    def unregisterPublisher(self,topic,ip):
        ownerChanged = False
        ownerIP = "null"
        topicInfo = self.topics[topic]
        topicInfo.deletePublisher(ip)
        topicInfo.delete_pub_status(ip)

        if topicInfo.checkOwnership(ip):
            # determine the new owner (i.e. pub with highest ownership value)
            highest_ownership = -1
            new_owner = "null"
            for ip, ownership in topicInfo.getPublishers().iteritems():
                if ownership > highest_ownership:
                    highest_ownership = ownership
                    new_owner = ip

            # set the new owner
            topicInfo.setOwner(new_owner, highest_ownership)
            ownerChanged = True
            ownerIP = new_owner

        self.topics[topic] = topicInfo
        return ownerChanged,ownerIP


    def registerSubscriber(self,topic,ip):
        publisherIP = "null"
        if bool(self.topics):
            if topic in self.topics.keys():
                topicInfo = self.topics[topic]
                owner = topicInfo.getOwner()

                if bool(owner):
                    publisherIP = owner.get("ip")
                else:
                    publisherIP = "null"

            else:
                topicInfo = TopicInfo()
                publisherIP = "null"

            topicInfo.addSubscriber(ip)
            self.topics[topic] = topicInfo

        return publisherIP



    def unregisterSubscriber(self, topic, ip):
        if bool(self.topics):
            topicInfo = self.topics[topic]
            topicInfo.deleteSubscriber(ip)
            self.topics[topic] = topicInfo


    def storePublisherData(self,topic,ip,data):
        # store publisher data in self.topics
        topicInfo = self.topics[topic]
        owner = topicInfo.getOwner()
        topicInfo.set_pub_status(ip, time.time())
        if bool(owner) and (ip == owner.get("ip")):
            topicInfo.archiveData(data)
            self.topics[topic] = topicInfo
            return "Success"
        else:
            return "Failure"

    def getHistoryData(self, topic, requestValue):
        historyData = ""
        topicInfo = self.topics[topic]
        for data in topicInfo.getHistory(requestValue):
            historyData =  historyData + data + " "

        print "Sending history data: " + str(historyData)

        return historyData