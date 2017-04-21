import Pyro4
import sys
from financeager.server import TinyDbServer

Pyro4.config.COMMTIMEOUT = 1.0

if __name__ == "__main__":
    period_name = sys.argv[1]

    with Pyro4.Daemon() as daemon:
        server = TinyDbServer(period_name)
        ns = Pyro4.locateNS()
        uri = daemon.register(server)
        ns.register(TinyDbServer.NAME, uri)

        print("Starting {}...".format(TinyDbServer.NAME))
        daemon.requestLoop(loopCondition=lambda: server.running)

        # no printing bc this clutters/blocks the command line
        # print("Stopping {}...".format(server_name))
        ns.remove(TinyDbServer.NAME)
