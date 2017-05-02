import zmq, time
from kazoo.client import KazooClient

LEADER_PATH = "/ass3/leader"
HOST_IP = '10.0.0.1:2181'

class SubInterface:
    def __init__(self):
        self.context = zmq.Context()

        # connect to the broker server
        # self.broker_socket_client = self.context.socket(zmq.REQ)
        # broker_addr = "tcp://10.0.0.1:5556"  # Well known address to middleware
        # self.broker_socket_client.connect(broker_addr)

        # create broker sub socket
        self.broker_socket_sub = self.context.socket(zmq.SUB)

        # self.broker_ip_pub = "tcp://10.0.0.1:5557"
        self.broker_ip_pub = None

        # self.zk = KazooClient(hosts=HOST_IP)
        # self.zk.start()
        # self.zk.ensure_path("/ass3")

        self.zk = KazooClient(hosts=HOST_IP)
        self.zk.start()

        self.zk.ensure_path("/ass3")

        self.topic = None
        self.my_ip_and_port = None

        # Or if you want the event object
        @self.zk.DataWatch(LEADER_PATH)
        def new_es(data, stat):
            if self.topic is not None:
                leader_ip = "tcp://" + data + ":5556"

                self.broker_socket_client = self.context.socket(zmq.REQ)
                self.broker_socket_client.connect(leader_ip)

                reg_string = "register" + " " + self.topic + " " + self.my_ip_and_port
                self.broker_socket_client.send_string(reg_string)
                self.broker_ip_pub = self.broker_socket_client.recv_string()
                print("Contacting new leader: " + data)

                self.connect_and_subscribe(self.broker_socket_sub, self.broker_ip_pub, self.topic)

    def register(self, es_node_ip, topic, ip):
        print("________________________________________")
        print("Registering with EventService.")

        self.topic = topic
        self.my_ip_and_port = ip

        self.broker_socket_client = self.context.socket(zmq.REQ)
        broker_addr = es_node_ip  # Well known address to middleware
        self.broker_socket_client.connect(broker_addr)

        reg_string = "find_es_ip" + " " + topic + " " + ip
        self.broker_socket_client.send_string(reg_string)
        leader_address = self.broker_socket_client.recv_string()

        self.broker_socket_client = self.context.socket(zmq.REQ)
        self.broker_socket_client.connect(leader_address)


        reg_string = "register" + " " + topic + " " + ip
        self.broker_socket_client.send_string(reg_string)
        self.broker_ip_pub = self.broker_socket_client.recv_string()

        print "Connecting to publisher: " + self.broker_ip_pub

        # todo connect message format:
        # pub_ip_and_port

        # register with the broker's publisher
        self.connect_and_subscribe(self.broker_socket_sub,
                                   self.broker_ip_pub,
                                   topic)

        print("Subscribed to topic")
        #print("________________________________________")

    def un_register(self, topic, ip):
        unreg_string = "Unregister" + " " + topic + " " + ip

        self.broker_socket_client.send_string(unreg_string)

        conf_message = self.broker_socket_client.recv_string()

        print(conf_message)

    def enter_message_loop(self, topic, sub):
        print("***Receiving: ***")

        while True:
            pub_message = self.broker_socket_sub.recv_string()
            # pub_message_split = pub_message.split()
            #
            # if topic is pub_message_split[0]:
            #     sub.pub_data_callback(pub_message_split[1])
            sub.pub_data_callback(pub_message)


    def request_history(self, topic, number_of_val, sub):

        # todo history request format:
        # "hist_request topic number_of_values"
        hist_request = "hist_request" + " " + topic + " " + number_of_val

        self.broker_socket_client.send_string(hist_request)

        # todo history reply format:
        # "val_1 val_2 ....val_n"
        hist_reply = self.broker_socket_client.recv_string()
        hist_reply_split = hist_reply.split()

        # return to the caller
        sub.hist_data_callback(hist_reply_split)

    @staticmethod
    def connect_and_subscribe(socket, ip_and_port, topic):
        socket.connect(ip_and_port)

        # Python 2 - ascii bytes to unicode str
        # (shouldn't be necessary)
        if isinstance(topic, bytes):
            topic = topic.decode('ascii')

        socket.setsockopt_string(zmq.SUBSCRIBE, topic) 