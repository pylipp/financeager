# Script to conveniently run all test suites
#   cd financeager/ 
#   python -m src.test.suites
import unittest 

modules = [
        'test_items'
        ]

testRunner = unittest.TextTestRunner(verbosity=2)

# import modules, find suite via suite() method and run it
for module in modules:
    exec('import {}'.format(module))
    try:
        suite = eval('{}.suite()'.format(module))
        testRunner.run(suite)
    except (AttributeError) as e:
        print("{}: {}".format(module, e))
