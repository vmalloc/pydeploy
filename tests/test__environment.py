import random
import time
import os
import tempfile
import unittest
import forge
from test_cases import ForgeTest
from pydeploy import environment
from pydeploy import os_api
from pydeploy import virtualenv_api
from pydeploy.environment_utils import EnvironmentUtils
from pydeploy import get_active_envrionment
from pydeploy.sources import (
    Source,
    Path,
    EasyInstall
    )

class EnvironmentTest(ForgeTest):
    def tearDown(self):
        environment.clear_active_environment()
        self.assertIsNone(get_active_envrionment())
        super(EnvironmentTest, self).tearDown()

class EnvironmentConstructionTest(EnvironmentTest):
    def setUp(self):
        super(EnvironmentConstructionTest, self).setUp()
        self.env_root = "/some/path"
        self.forge.replace_many(os_api, "makedirs")
        self.forge.replay() # make sure nothing happens during the test
        self.env = environment.Environment(self.env_root)
    def test__no_checkout_cache_by_default(self):
        self.assertIsNone(self.env.get_checkout_cache())
    def test__utils(self):
        self.assertIsInstance(self.env.utils, EnvironmentUtils)

class GetActiveEnvironmentTest(EnvironmentTest):
    def setUp(self):
        super(GetActiveEnvironmentTest, self).setUp()
        self.forge.replace_many(virtualenv_api,
            "create_environment", "activate_environment"
            )
    def test__create_and_activate_frontend(self):
        create_environment_stub = self.forge.replace(virtualenv_api, "create_environment")
        e = self.forge.create_hybrid_mock(environment.Environment)
        e.__forge__.enable_setattr_during_replay()
        e._path = path = "some/path"
        create_environment_stub(e._path)
        def _assert_no_active_environment():
            self.assertIsNone(get_active_envrionment())
        e._try_load_installed_signatures()
        virtualenv_api.activate_environment(path).and_call(_assert_no_active_environment)
        with self.forge.verified_replay_context():
            e.create_and_activate()
            self.assertIs(get_active_envrionment(), e)

class EnvironmentWithLocalPathTest(EnvironmentTest):
    def setUp(self):
        super(EnvironmentWithLocalPathTest, self).setUp()
        self.path = os.path.join(tempfile.gettempdir(), "envs", str(random.random()))
        self.argv = ["some", "argv", "here"]
        self.forge.replace_with(virtualenv_api, "create_environment", self._create)
        self.forge.replace_with(virtualenv_api, "activate_environment", self._activate)
        self.activated_count = 0
        self.env = environment.Environment(self.path, self.argv)
        self.assertEquals(self.activated_count, 0)
    def _create(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)
    def _activate(self, path):
        self.assertEquals(self.path, path)
        self.activated_count += 1

class EnvironmentAPITest(EnvironmentWithLocalPathTest):
    def test__get_argv(self):
        self.assertEquals(self.env.get_argv(), self.argv)
        self.assertIsNot(self.env.get_argv(), self.argv)
    def test__get_path(self):
        self.assertEquals(self.env.get_path(), self.path)
    def test__get_python_executable(self):
        self.assertEquals(self.env.get_python_executable(),
                          os.path.join(self.path, "bin", "python"))
    def test__get_easy_install_executable(self):
        self.assertEquals(self.env._get_easy_install_executable(),
                          os.path.join(self.path, "bin", "easy_install"))
    def test__get_pip_executable(self):
        self.assertEquals(self.env._get_pip_executable(),
                          os.path.join(self.path, "bin", "pip"))
    def test__make_source_object_path(self):
        path = os.path.join(tempfile.gettempdir(), "bla")
        open(path, "wb").close()
        result = self.env._make_source_object(path)
        self.assertIsInstance(result, Path)
        self.assertEquals(result._param, path)
    def test__make_source_object_easy_install(self):
        pkg_name = "some_pkg"
        result = self.env._make_source_object(pkg_name)
        self.assertIsInstance(result, EasyInstall)
        self.assertEquals(result._param, pkg_name)

class ActivatedEnvironmentTest(EnvironmentWithLocalPathTest):
    def setUp(self):
        super(ActivatedEnvironmentTest, self).setUp()
        self.env.create_and_activate()
        self.assertEquals(self.activated_count, 1)

class InstallCheckoutTest(ActivatedEnvironmentTest):
    def setUp(self):
        super(InstallCheckoutTest, self).setUp()
        self.source = self.forge.create_mock(Source)
        self.source_name = "some_name"
        self.source.get_name = lambda: self.source_name
        self.source_signature = "some_signature"
        self.source.get_signature = lambda: self.source_signature
    def test__main_installation_sequence(self):
        expected_result = self.forge.create_sentinel()
        self.source.install(self.env).and_return(expected_result)

        with self.forge.verified_replay_context():
            self.assertEquals(self.activated_count, 1)
            result = self.env.install(self.source)
            self.assertEquals(self.activated_count, 2)
        self.assertIs(result, expected_result)
    def test__main_checkout_sequence(self):
        expected_result = self.forge.create_sentinel()
        self.source.checkout(self.env).and_return(expected_result)
        with self.forge.verified_replay_context():
            result = self.env.checkout(self.source)
        self.assertIs(expected_result, result)
    def test__main_checkout_sequence_with_arg(self):
        expected_result = self.forge.create_sentinel()
        arg = self.forge.create_sentinel()
        self.source.checkout(self.env, arg).and_return(expected_result)
        with self.forge.verified_replay_context():
            result = self.env.checkout(self.source, arg)
        self.assertIs(expected_result, result)
    def test__installed_signatures(self):
        self.installed = False
        class MySource(Path):
            def install(self_, env):
                if self.installed:
                    raise Exception("Already installed")
                self.installed = True

        src = MySource("/bla/bla")
        self.assertFalse(self.env._is_already_installed(src))
        self.assertFalse(self.installed)
        for i in range(3): #only first time should matter
            self.env.install(src, reinstall=False)
            self.assertEquals(self.activated_count, 2)
            self.assertTrue(self.installed)
        # even if the environment is reinitialized, nothing should happen
        second_env = environment.Environment(self.path)
        second_env.create_and_activate()
        self.assertEquals(self.activated_count, 3)
        self.env.install(src, reinstall=False)
        self.assertEquals(self.activated_count, 3)

