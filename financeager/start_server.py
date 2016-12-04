import Pyro4
import sys
from financeager.server import Server

Pyro4.config.COMMTIMEOUT = 1.0

if __name__ == "__main__":
    name = sys.argv[1]

    with Pyro4.Daemon() as daemon:
        server = Server(name)
        ns = Pyro4.locateNS()
        uri = daemon.register(server)
        server_name = Server.NAME_STUB.format(name)
        ns.register(server_name, uri)

        print("Starting {}...".format(server_name))
        daemon.requestLoop(loopCondition=lambda: server.running)

        # no printing bc this clutters/blocks the command line
        # print("Stopping {}...".format(server_name))
        ns.remove(server_name)
