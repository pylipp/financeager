# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager.config import CONFIG_DIR, CONFIG
from financeager.cli import main
from financeager.pyro import launch_server
import os
import signal
import subprocess
import time


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_servers_running'
            ]
    suite.addTest(unittest.TestSuite(map(StartCliTestCase, tests)))
    return suite

class StartCliTestCase(unittest.TestCase):
    def setUp(self):
        CONFIG["SERVICE"]["name"] = "pyro"
        CONFIG["SERVICE:PYRO"]["host"] = "127.0.0.1"

        self.launch_process = launch_server(testing=True)
        time.sleep(2)
        
        ps_process = subprocess.Popen(["ps", "aux"], stdout=subprocess.PIPE)
        self.python_processes = subprocess.check_output(["grep", "python"],
                stdin=ps_process.stdout).splitlines()

        # check_output returns byte strings, hence prefix strings being searched for
        self.name_server_pid = self.find_pid_by_name(b"pyro4-ns")

    def find_pid_by_name(self, name):
        for process in self.python_processes:
            if process.find(name) > -1:
                return int(process.split()[1])
        return None

    def test_servers_running(self):
        cl_kwargs = {"command": "add", "name": "foo", "value": 19, "period": "0"}
        main(cl_kwargs)

        running = True
        if self.launch_process.pid is None:
            running = False
        else:
            try:
                self.launch_process.kill()
            except (OSError) as e:
                running = False
        self.assertTrue(running)
        if self.name_server_pid is None:
            running = False
        else:
            try:
                os.kill(self.name_server_pid, signal.SIGKILL)
            except (OSError) as e:
                running = False
        self.assertTrue(running)

    def tearDown(self):
        # self.cli._cl_kwargs = dict(command="stop", period="0")
        self.launch_process.kill()
        os.remove(os.path.join(CONFIG_DIR, "0.json"))

if __name__ == '__main__':
    unittest.main()
