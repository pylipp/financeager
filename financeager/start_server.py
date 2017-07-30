import Pyro4
from financeager.server import PyroServer
from financeager.config import CONFIG

Pyro4.config.COMMTIMEOUT = 1.0


if __name__ == "__main__":
    pyro_config = CONFIG["SERVICE:PYRO"]

    with Pyro4.Daemon(
            host=pyro_config["host"],
            port=pyro_config.getint("port")
            ) as daemon:
        server = PyroServer()
        ns = Pyro4.locateNS(hmac_key=pyro_config.get("hmac_key"))

        # see https://stackoverflow.com/questions/34013578/pyro-how-to-use-hmac-key-with-name-server-communicationerror-hmac-key-config
        daemon._pyroHmacKey = pyro_config.get("hmac_key")

        uri = daemon.register(server)
        ns.register(PyroServer.NAME, uri)

        print("Starting {}...".format(PyroServer.NAME))
        daemon.requestLoop(loopCondition=lambda: server.running)

        # no printing bc this clutters/blocks the command line
        # print("Stopping {}...".format(server_name))
        ns.remove(PyroServer.NAME)
