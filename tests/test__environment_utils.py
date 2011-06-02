from test_cases import ForgeTest
from pydeploy.environment import Environment
from pydeploy import environment_utils

class EnvironmentUtilsTest(ForgeTest):
    def setUp(self):
        super(EnvironmentUtilsTest, self).setUp()
        self.env = self.forge.create_mock(Environment)
        self.forge.replace(environment_utils, "execute_assert_success")
        self.envutils = self.env.utils = environment_utils.EnvironmentUtils(self.env)
        self.python_exe = "some_python_exe"
    def test__execute_python_script_list(self):
        self._test__execute_python_script(["some", "cmd"], [self.python_exe, "some", "cmd"])
    def test__execute_python_script_string(self):
        self._test__execute_python_script("some cmd", "{0} some cmd".format(self.python_exe))
    def _test__execute_python_script(self, cmd, expected_cmd):
        orig_cmd = cmd[:]
        self.env.get_python_executable().and_return(self.python_exe)
        expected_result = self.forge.create_sentinel()
        cwd = "some_cwd"
        environment_utils.execute_assert_success(expected_cmd, shell=False, cwd=cwd).and_return(expected_result)
        with self.forge.verified_replay_context():
            result = self.envutils.execute_python_script(cmd, cwd=cwd)
        self.assertEquals(result, expected_result)
        self.assertEquals(cmd, orig_cmd)
