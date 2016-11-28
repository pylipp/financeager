# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager.server import Server, CONFIG_DIR
import os.path
import subprocess
import signal


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_config_dir_exists'
            ]
    suite.addTest(unittest.TestSuite(map(StartServerTestCase, tests)))
    tests = [
            'test_entry_exists'
            ]
    suite.addTest(unittest.TestSuite(map(AddEntryToServerTestCase, tests)))
    tests = [
            'test_period_file_exists'
            ]
    suite.addTest(unittest.TestSuite(map(ServerContextTestCase, tests)))
    tests = [
            'test_server_process_running'
            ]
    suite.addTest(unittest.TestSuite(map(RunServerScriptTestCase, tests)))
    return suite

class StartServerTestCase(unittest.TestCase):
    def test_config_dir_exists(self):
        server = Server()
        self.assertTrue(os.path.isdir(CONFIG_DIR))

class AddEntryToServerTestCase(unittest.TestCase):
    def setUp(self):
        self.server = Server()
        self.server.add(name="Hiking boots", value="-111.11",
                category="outdoors")

    def test_entry_exists(self):
        self.assertIsNotNone(self.server._period._expenses_model.find_name_item(
            name="hiking boots", category="outdoors"))

class ServerContextTestCase(unittest.TestCase):
    def setUp(self):
        with Server() as server:
            server.add(name="Hiking boots", value="-111.11", category="outdoors")

    def test_period_file_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(CONFIG_DIR, "2016.xml")))

class RunServerScriptTestCase(unittest.TestCase):
    """This runs yet no output is written to file by Server.__exit__().
    Manually starting a nameserver and running
    `python start_server.py <name>` in the financeager virtualenv starts the
    process. Terminating it via CTRL-C causes the period file to be written.
    """
    def setUp(self):
        python_exec = os.path.join(
                os.environ["WORKON_HOME"], "financeager", "bin", "python")
        self.nameserver_process = subprocess.Popen(
                [python_exec, "-m", "Pyro4.naming"], shell=False)
        test_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(
                test_dir, "..", "financeager", "start_server.py")
        period_name = "1337"
        self.server_process = subprocess.Popen(
                [python_exec, script_path, period_name], shell=False)

    def test_server_process_running(self):
        # sleep a bit to see output from server launches
        import time; time.sleep(3)
        running = True
        try:
            os.kill(self.server_process.pid, 0)
        except (OSError) as e:
            running = False
        self.assertTrue(running)

    def tearDown(self):
        os.kill(self.server_process.pid, signal.SIGTERM)
        os.kill(self.nameserver_process.pid, signal.SIGTERM)

if __name__ == '__main__':
    unittest.main()
