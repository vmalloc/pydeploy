import itertools
import os
import sys
import urllib2
from cStringIO import StringIO
from tempfile import mkdtemp
from tempfile import gettempdir
from test_cases import ForgeTest
from pydeploy import os_api
from pydeploy.environment import Environment

class DeploymentFileExecutionTest(ForgeTest):
    _DEPLOYMENT_SCRIPT = """\
env.__test__.__success__ = True"""
    def setUp(self):
        super(DeploymentFileExecutionTest, self).setUp()
        self.env = Environment(gettempdir())
        self.env.__test__ = self
        self.assertFalse(hasattr(self, "__success__"))
        # we rely on it throwing exceptions if errors occur...
        self.assertIs(os_api.urlopen, urllib2.urlopen)
        self.forge.replace(os_api, "urlopen")
        self._orig_stdin = sys.stdin
    def tearDown(self):
        sys.stdin = self._orig_stdin
        super(DeploymentFileExecutionTest, self).tearDown()
    def assertSuccess(self):
        self.assertTrue(self.__success__)
    def test__execute_path_direct(self):
        self._test__execute_path(direct=True)
    def test__execute_path_indirect(self):
        self._test__execute_path(direct=False)
    def _test__execute_path(self, direct):
        filename = os.path.join(mkdtemp(), "deployment")
        with open(filename, "w") as deployment_file:
            deployment_file.write(self._DEPLOYMENT_SCRIPT)
        if direct:
            self.env.execute_deployment_file_path(filename)
        else:
            self.env.execute_deployment_file(filename)
        self.assertSuccess()
    def test__execute_url_direct(self):
        self._test__execute_url(direct=True)
    def test__execute_url_indirect(self):
        self._test__execute_url(direct=False)
    def _test__execute_url(self, direct):
        url = "http://some.url.com/bla"
        os_api.urlopen(url).and_return(StringIO(self._DEPLOYMENT_SCRIPT))
        self.forge.replay()
        if direct:
            self.env.execute_deployment_file_url(url)
        else:
            self.env.execute_deployment_file(url)
        self.assertSuccess()
    def test__execute_stdin(self):
        sys.stdin = StringIO(self._DEPLOYMENT_SCRIPT)
        self.env.execute_deployment_stdin()
        self.assertSuccess()
    def _test__execute_once(self, is_url, same_arg, same_content):
        if is_url:
            arg = "http://a"
            os_api.urlopen(arg).and_return(StringIO(self._DEPLOYMENT_SCRIPT))
            if not same_arg:
                os_api.urlopen(arg + 'x').and_return(StringIO(self._DEPLOYMENT_SCRIPT if same_content else self._DEPLOYMENT_SCRIPT + ' '))
        else:
            arg = os.path.join(mkdtemp(), "file.py")
            with open(arg, "w") as outfile:
                outfile.write(self._DEPLOYMENT_SCRIPT)
            if not same_arg:
                with open(arg + 'x', "w") as outfile:
                    outfile.write(self._DEPLOYMENT_SCRIPT if same_content else self._DEPLOYMENT_SCRIPT + ' ')
        self.forge.replay()
        self.env.execute_deployment_file_once(arg)
        self.assertSuccess()
        self.__success__ = False
        self.env.execute_deployment_file_once(arg if same_arg else arg + 'x')
        if same_content or same_arg:
            self.assertFalse(self.__success__)
        else:
            self.assertTrue(self.__success__)

_BOOL = (True, False)

for combination in itertools.product(_BOOL, _BOOL, _BOOL):
    setattr(DeploymentFileExecutionTest, 'test__execute_once_{}_{}_{}'.format(*combination), lambda self, c=combination : self._test__execute_once(*c))
