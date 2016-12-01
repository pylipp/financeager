import Pyro4
import sys
from financeager.server import Server

Pyro4.config.COMMTIMEOUT = 1.0

if __name__ == "__main__":
    name = sys.argv[1]

    with Server(name) as server:
        with Pyro4.Daemon() as daemon:
            ns = Pyro4.locateNS()
            uri = daemon.register(server)
            server_name = Server.NAME_STUB.format(name)
            ns.register(server_name, uri)

            print("Starting {}...".format(server_name))
            daemon.requestLoop(loopCondition=lambda: server.running)
            print("Stopping {}...".format(server_name))
