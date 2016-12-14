import Pyro4
import sys

Pyro4.config.COMMTIMEOUT = 1.0

if __name__ == "__main__":
    name = sys.argv[1]
    server_cls_name = sys.argv[2]
    server_module = __import__("financeager.server", fromlist=[server_cls_name])
    server_cls = getattr(server_module, server_cls_name)

    with Pyro4.Daemon() as daemon:
        server = server_cls(name)
        ns = Pyro4.locateNS()
        uri = daemon.register(server)
        server_name = server_cls.name(name)
        ns.register(server_name, uri)

        print("Starting {}...".format(server_name))
        daemon.requestLoop(loopCondition=lambda: server.running)

        # no printing bc this clutters/blocks the command line
        # print("Stopping {}...".format(server_name))
        ns.remove(server_name)
