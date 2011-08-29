import sys
import os
import tempfile
import zipfile
from .command import execute_assert_success
from pkg_resources import parse_requirements

class Installer(object):
    def __init__(self, env):
        super(Installer, self).__init__()
        self._env = env
    def install_unpacked_package(self, path):
        self._run_pydeploy_setup(path)
        self._install_requirements(path)
        self._env.utils.execute_python_script(["setup.py", "install"], cwd=path)
    def _run_pydeploy_setup(self, path):
        pydeploy_setup_file = os.path.join(path, "pydeploy_setup.py")
        if os.path.exists(pydeploy_setup_file):
            self._env.execute_deployment_file(pydeploy_setup_file)
    def _install_requirements(self, path):
        for req in self._get_install_requirements(path):
            if self._env.has_alias(req):
                self._env.install(req)
    def _get_install_requirements(self, path):
        temp_dir = tempfile.mkdtemp()
        execute_assert_success("{0} setup.py bdist_egg --dist-dir={1}".format(sys.executable, temp_dir),
                               shell=True, cwd=path)
        [egg_file] = os.listdir(temp_dir)
        reqs = zipfile.ZipFile(os.path.join(temp_dir, egg_file)).read("EGG-INFO/requires.txt")
        return list(parse_requirements(reqs))


