import zmq,time
import threading

class ES_Interface:

    def __init__(self, ip):
        self.pubReplyUrl = "tcp://*:5555"
        self.subReplyUrl = "tcp://*:5556"
        self.pubUrl = "tcp://*:5557"

        self.ip = "tcp://" + ip
        self.sub_address = self.ip + ":5557"

        self.poller = zmq.Poller()
        self.pubReplySocket = self.createReplySocket(self.pubReplyUrl)
        self.subReplySocket = self.createReplySocket(self.subReplyUrl)
        self.pubSocket = self.createPubSocket(self.pubUrl)

        self.isLeader = False


    def getIpAddress(self):
        return self.ip


    def createReplySocket(self,clientUrl):
        #print("Creating Reply socket: " + clientUrl)
        socket = zmq.Context().socket(zmq.REP)
        socket.bind(clientUrl)
        self.poller.register(socket, zmq.POLLIN)
        return socket


    def createPubSocket(self,pubUrl):
        socket = zmq.Context().socket(zmq.PUB)
        socket.bind(pubUrl)
        return socket


     # Begins to broker incoming messages
    def enter_message_loop(self, es_callback, leader_running):
        print "\n\n Leader status: " + str(leader_running) + ".\n"

        self.isLeader = leader_running

        while self.isLeader == leader_running:
            # print("debug: mess loop for leadership status - " + str(leader_running))

            events = dict(self.poller.poll(1000))

            if self.isLeader == leader_running:

                # check if publishers have sent a message
                if self.pubReplySocket in events:
                    print("\n\nIncoming Publisher request")
                    messageString = self.pubReplySocket.recv_string()
                    print("Incoming Data: " + messageString)
                    messages = messageString.split()
                    self.handlePublisherMessages(messages,es_callback, leader_running)


                # check if subscribers have sent a message
                if self.subReplySocket in events:
                    print("\n\nIncoming Subscriber request")
                    messageString = self.subReplySocket.recv_string()
                    print("Incoming Data: " + messageString)
                    messages = messageString.split()
                    self.handleSubscriberMessages(messages,es_callback, leader_running)



    def find_leader_address(self, es_callback):
        leader_ip = es_callback.get_leader()
        leader_address = "tcp://" + leader_ip
        return leader_address



    ######## EventService  ############
    def handlePublisherMessages(self,messages,es_callback, leader_running):

        requestType = messages[0]
        topic = messages[1]
        ip = messages[2]

        print(leader_running)

        if leader_running:


            if requestType == "find_es_ip":
                print("Publisher looking for leader ES" + "--" + topic + "--" + ip)
                leader_address = self.find_leader_address(es_callback)
                self.pubReplySocket.send_string(leader_address + ":5555")

            elif requestType == "register":

                # print ("debug: request type = register")

                ownership = int(messages[3])
                print("Incoming Publisher with: " + "--" + topic + "--" + ip + "--" + str(ownership))
                es_callback.registerPublisher(topic, ip, ownership)
                self.pubReplySocket.send_string("Publisher has been registered successfully")

            elif requestType == "unregister":
                print("Leaving Publisher: " + "--" + topic + "--" + ip)
                es_callback.unregisterPublisher(topic, ip)
                self.pubReplySocket.send_string("Publisher has been removed successfully")

            elif requestType == "publish":
                data = messages[3]
                print("Publisher publishing: " + "--" + topic + "--" + ip )
                print("Message: " + data)
                status = es_callback.storePublisherData(topic, ip, data)
                self.pubReplySocket.send_string(status)

                if (status is "Success"):
                    messageString = topic + " " + data
                    print("\n\nAcknowledging : " + messageString)
                    self.pubSocket.send_string(messageString)

        else:
            if requestType == "find_es_ip":
                print("Publisher looking for ES leader " +  "--" + topic + "--" + ip)
                leader_address = self.find_leader_address(es_callback)
                self.pubReplySocket.send_string(leader_address + ":5555")



    def handleSubscriberMessages(self,messages,es_callback, leader_running):
        requestType = messages[0]

        if leader_running:

            if requestType == "find_es_ip":
                topic = messages[1]
                ip = messages[2]

                print("Subscriber looking for ES leader" + "--" + topic + "--" + ip)
                leader_address = self.find_leader_address(es_callback)
                self.subReplySocket.send_string(leader_address + ":5556")

            if requestType == "register":
                topic = messages[1]
                ip = messages[2]
                print("Subscriber" + "--" + topic + "--" + ip)
                es_callback.registerSubscriber(topic, ip)
                self.subReplySocket.send_string(self.sub_address)


            elif requestType == "unregister":
                topic = messages[1]
                ip = messages[2]
                print("Leaving Subscriber" + "--" + topic + "," + ip)
                es_callback.unregisterSubscriber(topic, ip)
                self.subReplySocket.send_string("Subscriber removed successfully")


            elif requestType == "hist_request":
                topic = messages[1]
                numOfValues = int(messages[2])
                print("Subscriber looking for " + "--" + topic + "--" + "with history " + str(numOfValues))
                historyData = es_callback.getHistoryData(topic, numOfValues)
                self.subReplySocket.send_string(historyData)

        else:
            if requestType == "find_es_ip":
                topic = messages[1]
                ip = messages[2]

                print("Subscriber looking for EventService IP" + "--" + topic + "--" + ip)
                leader_address = self.find_leader_address(es_callback)
                self.subReplySocket.send_string(leader_address + ":5556")