"""Suite for running all unittests."""
import unittest
import sys

modules = [
    'test_entries',
    'test_model',
    'test_period',
    'test_server',
    'test_webservice',
    'test_config',
    'test_offline',
    'test_communication',
]

test_runner = unittest.TextTestRunner(verbosity=2)

# import modules, find suite via suite() method and run it
successful = True
for module in modules:
    exec('from . import {}'.format(module))
    try:
        suite = eval('{}.suite()'.format(module))
        result = test_runner.run(suite)
        successful = successful and result.wasSuccessful()
    except (AttributeError) as e:
        print("{}: {}".format(module, e))

# return error code
sys.exit(0 if successful else 1)
