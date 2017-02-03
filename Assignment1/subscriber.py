import sys
from EventService import register_subscriber
from EventService import print_sub_table

'''EventService.register_subscriber(1, 1)
EventService.register_subscriber(1, 2)
EventService.register_subscriber(2, 2)
EventService.register_subscriber(2, 3)
EventService.register_subscriber(3, 3)
EventService.register_subscriber(3, 4)
EventService.register_subscriber(4, 4)
EventService.register_subscriber(4, 1)

EventService.print_sub_table()'''

sys.stdout.write("Enter IP address: ")
sys.stdout.flush()
IPaddress = sys.stdin.readline()
n = input("Enter number of topics you want to subscribe to:");
for i in range(0,n):
    topic = input("Enter topic id:")
    register_subscriber(topic,IPaddress)

print_sub_table()