import Pyro4
import sys
from financeager.server import Server

name = sys.argv[1]

with Server(name) as server:
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(server)
    server_name = Server.NAME_STUB.format(name)
    ns.register(server_name, uri)

    print("Starting {}...".format(server_name))
    daemon.requestLoop()
