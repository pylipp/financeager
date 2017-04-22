import Pyro4
from financeager.server import PyroServer

Pyro4.config.COMMTIMEOUT = 1.0

if __name__ == "__main__":
    with Pyro4.Daemon() as daemon:
        server = PyroServer()
        ns = Pyro4.locateNS()
        uri = daemon.register(server)
        ns.register(PyroServer.NAME, uri)

        print("Starting {}...".format(PyroServer.NAME))
        daemon.requestLoop(loopCondition=lambda: server.running)

        # no printing bc this clutters/blocks the command line
        # print("Stopping {}...".format(server_name))
        ns.remove(PyroServer.NAME)
