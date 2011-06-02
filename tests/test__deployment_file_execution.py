import os
import sys
import unittest
import urllib2
from cStringIO import StringIO
from tempfile import gettempdir
from test_cases import ForgeTest
from forge import Is
from pydeploy import virtualenv_api
from pydeploy import os_api
from pydeploy.environment import Environment
from pydeploy.environment import clear_active_environment

def _no_op(*args, **kwargs):
    pass

class DeploymentFrontendTest(ForgeTest):
    def setUp(self):
        super(DeploymentFrontendTest, self).setUp()
        self.forge.replace_with(os_api, "makedirs", _no_op)
        self.forge.replace_with(virtualenv_api, "create_environment", _no_op)
        self.forge.replace_with(virtualenv_api, "activate_environment", _no_op)
        self.env = self.forge.create_hybrid_mock(Environment)
    def test__execute_deployment_frontend_path(self):
        path = "/tmp/filename"
        self.env.execute_deployment_file_path(path)
        self.forge.replay()
        self.env.execute_deployment_file(path)
    def test__execute_deployment_frontend_url(self):
        url = "http://www.site.com/pydeploy"
        self.env.execute_deployment_file_url(url)
        self.forge.replay()
        self.env.execute_deployment_file(url)
    def test__execute_deployment_frontend_stdin(self):
        self.env.execute_deployment_file_object(Is(sys.stdin), filename="<stdin>")
        self.forge.replay()
        self.env.execute_deployment_stdin()

class DeploymentScriptTest(ForgeTest):
    _DEPLOYMENT_SCRIPT = """
env.__test__.success = True"""
    def setUp(self):
        super(DeploymentScriptTest, self).setUp()
        self.success = False
        self.env = Environment("/some/path")
        self.env.__test__ = self
    def test__execute_deployment_path(self):
        deployment_filename = os.path.join(gettempdir(), "_deployment_file")
        with open(deployment_filename, "wb") as f:
            f.write(self._DEPLOYMENT_SCRIPT)
        self.env.execute_deployment_file_path(deployment_filename)
        self.assertTrue(self.success)
    def test__urlopen_is_urllib2_urlopen(self):
        # we rely on it throwing exceptions if errors occur...
        self.assertIs(os_api.urlopen, urllib2.urlopen)
    def test__execute_deployment_url(self):
        url = "some_url"
        self.forge.replace(os_api, "urlopen")
        os_api.urlopen(url).and_return(StringIO(self._DEPLOYMENT_SCRIPT))

        with self.forge.verified_replay_context():
            self.env.execute_deployment_file_url(url)
        self.assertTrue(self.success)
