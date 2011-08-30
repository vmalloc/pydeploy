from __future__ import print_function
import os
import tempfile
from pydeploy import virtualenv_api
import unittest

class VirtualenvAPITest(unittest.TestCase):
    def test__activate_environment(self):
        global _success
        _success = False
        path = tempfile.gettempdir()
        bin_dir = os.path.join(path, "bin")
        if not os.path.exists(bin_dir):
            os.mkdir(bin_dir)
        activate_this_file = os.path.join(bin_dir, "activate_this.py")
        with open(activate_this_file, "w") as activate_file:
            print("""import {0}
if __file__ != {1!r}:
    raise Exception('Wrong path')
{0}._success = True
""".format(__name__, activate_this_file), file=activate_file)

        virtualenv_api.activate_environment(path)
        self.assertTrue(_success)

