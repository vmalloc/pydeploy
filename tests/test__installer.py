import os
from pkg_resources import Requirement
from infi.unittest import parameters
from .test_cases import ForgeTest
from tempfile import mkdtemp
from pydeploy.environment import PythonEnvironment
from pydeploy.environment_utils import EnvironmentUtils
from pydeploy.installer import Installer
from pydeploy.sources import Source
from .test_utils import create_installable_package

class InstallerFrontendTest(ForgeTest):
    def setUp(self):
        super(InstallerFrontendTest, self).setUp()
        self.env = self.forge.create_mock(PythonEnvironment)
        self.env.utils = self.forge.create_mock(EnvironmentUtils)
        self.installer = Installer(self.env)
        self.forge.replace(self.installer, "_get_install_requirements")
        self.path = mkdtemp()

    def test__get_installation_context(self):
        self.assertIsNone(self.installer._context)
        with self.installer.get_installation_context():
            self.assertIsNotNone(self.installer._context)
            self.assertEquals(self.installer._context.installed, set())
            orig_context = self.installer._context
            with self.installer.get_installation_context():
                self.assertIs(self.installer._context, orig_context)
            self.assertIs(self.installer._context, orig_context)
        self.assertIsNone(self.installer._context)
    @parameters.toggle('with_pydeploy_setup', 'reinstall')
    def test__install(self, with_pydeploy_setup, reinstall):
        name = "some_name"
        self.forge.replace(self.installer, "_can_install_requirement")
        if with_pydeploy_setup:
            pydeploy_setup_file = os.path.join(self.path, "pydeploy_setup.py")
            with open(pydeploy_setup_file, "w"):
                pass
            self.env.execute_deployment_file(pydeploy_setup_file)
        deps = [Requirement.parse("dep{}>=2.0.0".format(i)) for i in range(10)]
        can_install = [deps[2], deps[4]]
        self.installer._get_install_requirements(self.path, name).and_return(deps)
        for dep in deps:
            self.installer._can_install_requirement(dep).and_return(dep in can_install)
            if dep in can_install:
                self.env.install(dep, reinstall=reinstall).and_call_with_args(self._assert_marked_as_installed)
        self._expect_installation()
        self.forge.replay()
        with self.installer.get_installation_context():
            self.installer.install_unpacked_package(self.path, name, reinstall=reinstall)
    @parameters.toggle('aliased', 'already_installed')
    def test__can_install_requirement(self, aliased, already_installed):
        req = Requirement.parse('x>=2.0.0')
        self.env.has_alias(req).and_return(aliased)
        self.forge.replay()
        with self.installer.get_installation_context():
            if aliased and already_installed:
                self.installer._context.installed.add(req.unsafe_name)
            self.assertEquals(aliased and not already_installed,
                              self.installer._can_install_requirement(req))

    def _assert_marked_as_installed(self, dep, *_, **__):
        self.assertIn(dep.unsafe_name, self.installer._context.installed)
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
        create_installable_package(package_container, reqs=reqs)
        self.forge.replay()
        parsed_reqs = self.installer._get_install_requirements(package_container, name=name)
        for parsed_requirement, dep in zip(parsed_reqs, reqs):
            self.assertIsInstance(parsed_requirement, Requirement)
            self.assertEquals(parsed_requirement.project_name, dep.split(">=")[0])


