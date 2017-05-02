import zmq, time
from kazoo.client import KazooClient



LEADER_PATH = "/ass3/leader"
HOST_IP = '10.0.0.1:2181'


class PubInterface:

    def __init__(self):
        self.context = zmq.Context()
        self.broker_socket = self.context.socket(zmq.REQ)

        # self.zk = KazooClient(hosts=HOST_IP)
        # self.zk.start()
        # self.zk.ensure_path("/ass3")

        self.zk = KazooClient(hosts=HOST_IP)
        self.zk.start()

        self.zk.ensure_path("/ass3")

        self.topic = None
        self.my_ip_and_port = None
        self.ownership = None

        self.data = None
        self.update_int = None

        self.current_broker_ip = None

        # Or if you want the event object
        @self.zk.DataWatch(LEADER_PATH)
        def new_es(data, stat):
            if self.topic is not None:

                self.current_broker_ip = "tcp://" + data + ":5555"

                self.broker_socket = self.context.socket(zmq.REQ)
                self.broker_socket.connect(self.current_broker_ip)
                print("Contacting new leader: " + data)

                message = "register" + " " + self.topic + " " + self.my_ip_and_port + " " + self.ownership
                self.broker_socket.send_string(message)
                status = self.broker_socket.recv_string()
                print(status)

                self.publish_loop(self.data, self.update_int)




    def register(self, es_node_ip, topic, my_ip_and_port, ownership):

        # set interface state
        self.topic = topic
        self.my_ip_and_port = my_ip_and_port
        self.ownership = ownership

        broker_addr = es_node_ip  # well known address to middleware
        self.broker_socket.connect(broker_addr)

        # print("debug: es_node_ip" + str(broker_addr))

        message = "find_es_ip" + " " + topic + " " + my_ip_and_port
        self.broker_socket.send_string(message)
        ip_of_event_service = self.broker_socket.recv_string()
        #print(ip_of_event_service)

        if ip_of_event_service is not es_node_ip:
            # print("debug: changing ip of broker to " + str(ip_of_event_service))
            self.broker_socket = self.context.socket(zmq.REQ)
            self.broker_socket.connect(ip_of_event_service)

        message = "register" + " " + topic + " " + my_ip_and_port + " " + ownership
        self.broker_socket.send_string(message)
        status = self.broker_socket.recv_string()
        print(status)
        # self.broker_socket = self.context.socket(zmq.REQ)
        # self.broker_socket.connect(ip_of_event_service)



    def un_register(self, topic, ip):
        message = "unregister" + " " + topic + " " + ip
        self.broker_socket.send_string(message)
        conf_message = self.broker_socket.recv_string()
        print(conf_message)

    def publish(self, topic, ip_and_port, data):
        # First send the data to the event service for history purposes
        es_message = "publish" + " " + topic + " " + ip_and_port + " " + data

        self.broker_socket.send_string(es_message)
        conf_message = self.broker_socket.recv_string()
        #print("EventService Configuration: " + conf_message)

    def publish_loop(self, data, update_int):

        start_broker_ip = self.current_broker_ip
        self.data = data
        self.update_int = update_int

        while start_broker_ip == self.current_broker_ip:

            #print("\ttime: {} | data: ".format(time.time()) + data)
            self.publish(self.topic, self.my_ip_and_port, data)
            time.sleep(update_int)