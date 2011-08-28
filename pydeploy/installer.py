import sys
import os
import tempfile
import zipfile
from .command import execute_assert_success

class Installer(object):
    def __init__(self, env):
        super(Installer, self).__init__()
        self._env = env
    def install_unpacked_package(self, path):
        self._run_pydeploy_setup(path)
        self._install_dependencies(path)
        self._env.utils.execute_python_script(["setup.py", "install"], cwd=path)
    def _run_pydeploy_setup(self, path):
        pydeploy_setup_file = os.path.join(path, "pydeploy_setup.py")
        if os.path.exists(pydeploy_setup_file):
            self._env.execute_deployment_file(pydeploy_setup_file)
    def _install_dependencies(self, path):
        for dep in self._get_install_dependencies(path):
            self._env.install(dep)
    def _get_install_dependencies(self, path):
        temp_dir = tempfile.mkdtemp()
        execute_assert_success("{0} setup.py bdist_egg --dist-dir={1}".format(sys.executable, temp_dir),
                               shell=True, cwd=path)
        [egg_file] = os.listdir(temp_dir)
        return zipfile.ZipFile(os.path.join(temp_dir, egg_file)).read("EGG-INFO/requires.txt").splitlines()


