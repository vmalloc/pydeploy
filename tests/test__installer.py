import os
from pkg_resources import Requirement
from .test_cases import ForgeTest
from tempfile import mkdtemp
from pydeploy.environment import PythonEnvironment
from pydeploy.environment_utils import EnvironmentUtils
from pydeploy.installer import Installer
from pydeploy.sources import Source

class InstallerFrontendTest(ForgeTest):
    def setUp(self):
        super(InstallerFrontendTest, self).setUp()
        self.env = self.forge.create_mock(PythonEnvironment)
        self.env.utils = self.forge.create_mock(EnvironmentUtils)
        self.installer = Installer(self.env)
        self.forge.replace(self.installer, "_get_install_requirements")
        self.path = mkdtemp()

    def test__install_with_pydeploy_setup(self):
        self._test__install(with_pydeploy_setup=True)
    def test__install_without_pydeploy_setup(self):
        self._test__install(with_pydeploy_setup=False)

    def _test__install(self, with_pydeploy_setup):
        name = "some_name"
        if with_pydeploy_setup:
            pydeploy_setup_file = os.path.join(self.path, "pydeploy_setup.py")
            with open(pydeploy_setup_file, "w"):
                pass
            self.env.execute_deployment_file(pydeploy_setup_file)
        deps = [Requirement.parse("dep{}>=2.0.0".format(i)) for i in range(10)]
        aliased = [deps[2], deps[4]]
        self.installer._get_install_requirements(self.path, name).and_return(deps)
        for dep in deps:
            self.env.has_alias(dep).and_return(dep in aliased)
            if dep in aliased:
                self.env.install(dep)
        self._expect_installation()
        self.forge.replay()
        self.installer.install_unpacked_package(self.path, name)
    def _expect_installation(self):
        return self.env.utils.execute_python_script(
            ["setup.py", "install"],
            cwd=self.path
            )

class InstallerRequirementsTest(ForgeTest):
    def setUp(self):
        super(InstallerRequirementsTest, self).setUp()
        self.env = self.forge.create_mock(PythonEnvironment)
        self.installer = Installer(self.env)
    def test__get_install_requirements(self):
        name = "some_name"
        package_container = mkdtemp()
        reqs = ["dep{}>=2.0.0".format(i) for i in range(10)]
        with open(os.path.join(package_container, "setup.py"), "w") as setup_file:
            setup_file.write(_SETUP_FILE_SKELETON.format(reqs=reqs))
        self.forge.replay()
        parsed_reqs = self.installer._get_install_requirements(package_container, name=name)
        for parsed_requirement, dep in zip(parsed_reqs, reqs):
            self.assertIsInstance(parsed_requirement, Requirement)
            self.assertEquals(parsed_requirement.project_name, dep.split(">=")[0])


_SETUP_FILE_SKELETON = """\
from setuptools import setup, find_packages

setup(name="somepkg",
      version="0.0.1",
      packages=find_packages(),
      install_requires={reqs},
      )
"""
