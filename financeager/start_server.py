import Pyro4
from financeager.server import TinyDbServer

Pyro4.config.COMMTIMEOUT = 1.0

if __name__ == "__main__":
    with Pyro4.Daemon() as daemon:
        server = TinyDbServer()
        ns = Pyro4.locateNS()
        uri = daemon.register(server)
        ns.register(TinyDbServer.NAME, uri)

        print("Starting {}...".format(TinyDbServer.NAME))
        daemon.requestLoop(loopCondition=lambda: server.running)

        # no printing bc this clutters/blocks the command line
        # print("Stopping {}...".format(server_name))
        ns.remove(TinyDbServer.NAME)
