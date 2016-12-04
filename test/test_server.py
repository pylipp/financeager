# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager.server import Server, CONFIG_DIR
import os.path
import subprocess
import signal
import socket
import sys


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_config_dir_exists'
            ]
    suite.addTest(unittest.TestSuite(map(StartServerTestCase, tests)))
    tests = [
            'test_entry_exists',
            'test_period_name'
            ]
    suite.addTest(unittest.TestSuite(map(AddEntryToServerTestCase, tests)))
    tests = [
            'test_period_file_exists'
            ]
    suite.addTest(unittest.TestSuite(map(ServerDumpTestCase, tests)))
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
        self.server = Server(0)
        self.dump_filepath = os.path.join(CONFIG_DIR, "0.xml")
        self.server.run("add", name="Hiking boots", value="-111.11",
                category="outdoors")

    def test_entry_exists(self):
        self.assertIsNotNone(self.server._period._expenses_model.find_name_item(
            name="hiking boots", category="outdoors"))

    def test_period_name(self):
        self.assertEqual("0", self.server._period.name)

    def tearDown(self):
        os.remove(self.dump_filepath)

class ServerDumpTestCase(unittest.TestCase):
    def setUp(self):
        server = Server(42)
        self.dump_filepath = os.path.join(CONFIG_DIR, "42.xml")
        server.run("add", name="Hiking boots", value="-111.11", category="outdoors")

    def test_period_file_exists(self):
        self.assertTrue(os.path.isfile(self.dump_filepath))

    def tearDown(self):
        os.remove(self.dump_filepath)

class RunServerScriptTestCase(unittest.TestCase):
    """This runs yet no output is written to file by Server.__exit__().
    Manually starting a nameserver and running
    `python start_server.py <name>` in the financeager virtualenv starts the
    process. Terminating it via CTRL-C causes the period file to be written.
    """
    def setUp(self):
        # silence error messages if name server has already been launched
        DEVNULL = open(os.devnull, 'w')
        self.nameserver_process = subprocess.Popen(
                [sys.executable, "-m", "Pyro4.naming"], shell=False,
                stderr=subprocess.STDOUT, close_fds=True,
                stdout=DEVNULL)
        test_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(
                test_dir, "..", "financeager", "start_server.py")
        period_name = "1337"
        self.server_process = subprocess.Popen(
                [sys.executable, script_path, period_name], shell=False)

    def test_server_process_running(self):
        # sleep a bit to see output from server launches
        import time; time.sleep(1)
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
