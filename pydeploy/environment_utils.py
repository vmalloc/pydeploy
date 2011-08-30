from .python3_compat import basestring
from .command import execute_assert_success

class EnvironmentUtils(object):
    def __init__(self, env):
        super(EnvironmentUtils, self).__init__()
        self._env = env
    def execute_python_script(self, cmd, cwd=None):
        if isinstance(cmd, basestring):
            cmd = "{0} {1}".format(self._env.get_python_executable(), cmd)
        else:
            cmd = list(cmd)
            cmd.insert(0, self._env.get_python_executable())
        return execute_assert_success(cmd, cwd=cwd, shell=False)
