from kazoo.client import KazooClient
import logging, json


logging.basicConfig()

# Create a client and start it
zk = KazooClient(hosts='10.0.0.1:2181')
zk.start()

if zk.exists("/ass3/leader"):
    print "Present. Deleting... "
    zk.delete("/ass3/leader", recursive=True)
    print "Cleared.."


# In the end, stop it
zk.stop()