# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager.server import Server, CONFIG_DIR
from financeager.cli import Cli
import psutil
import os
import signal
import subprocess


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_server_process_running',
            'test_name_server_process_running'
            ]
    suite.addTest(unittest.TestSuite(map(StartCliTestCase, tests)))
    return suite

class StartCliTestCase(unittest.TestCase):
    def setUp(self):
        cl_kwargs = {"period_name": 1337}
        self.cli = Cli(cl_kwargs)
        ps_process = subprocess.Popen(["ps", "aux"], stdout=subprocess.PIPE)
        self.python_processes = subprocess.check_output(["grep", "python"],
                stdin=ps_process.stdout).splitlines()
        self.server_pid = self.find_pid_by_name("start_server.py")
        self.name_server_pid = self.find_pid_by_name("Pyro4.naming")

    def find_pid_by_name(self, name):
        for process in self.python_processes:
            if process.find(name) > -1:
                return int(process.split()[1])
        return None

    def test_server_process_running(self):
        # sleep a bit to see output from server launches
        import time; time.sleep(3)
        running = True
        if self.server_pid is None:
            running = False
        else:
            try:
                os.kill(self.server_pid, 0)
            except (OSError) as e:
                running = False
        self.assertTrue(running)

    def test_name_server_process_running(self):
        # sleep a bit to see output from server launches
        import time; time.sleep(3)
        running = True
        if self.name_server_pid is None:
            running = False
        else:
            try:
                os.kill(self.name_server_pid, 0)
            except (OSError) as e:
                running = False
        self.assertTrue(running)

    def tearDown(self):
        os.kill(self.server_pid, signal.SIGTERM)
        os.kill(self.name_server_pid, signal.SIGTERM)

if __name__ == '__main__':
    unittest.main()
