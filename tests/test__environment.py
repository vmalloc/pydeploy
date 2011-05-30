import unittest
import forge
from pydeploy import environment
from pydeploy import get_active_envrionment

class EnvironmentTest(unittest.TestCase):
    def setUp(self):
        super(EnvironmentTest, self).setUp()
        self.forge = forge.Forge()
    def tearDown(self):
        environment.clear_active_environment()
        self.assertIsNone(get_active_envrionment())
        self.forge.verify()
        self.forge.restore_all_replacements()
        super(EnvironmentTest, self).tearDown()

class ActiveEnvironmentTest(EnvironmentTest):
    def test__create_and_activate_frontend(self):
        create_environment_stub = self.forge.replace(environment, "create_environment")
        e = self.forge.create_hybrid_mock(environment.Environment)
        e._path = path = "some/path"
        create_environment_stub(e._path)
        def _assert_no_active_environment():
            self.assertIsNone(get_active_envrionment())
        e._try_load_installed_signatures()
        e._activate().and_call(_assert_no_active_environment)
        with self.forge.verified_replay_context():
            e.create_and_activate()
            self.assertIs(get_active_envrionment(), e)
