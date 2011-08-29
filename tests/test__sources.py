import os
import tempfile
import unittest
from test_cases import ForgeTest
from pydeploy.environment import Environment
from pydeploy.environment_utils import EnvironmentUtils
from pydeploy.checkout_cache import CheckoutCache
from pydeploy.installer import Installer
from pydeploy import sources
from pydeploy.scm import git
from pydeploy import command

class SourceTest(ForgeTest):
    def setUp(self):
        super(SourceTest, self).setUp()
        self.env = self.forge.create_mock(Environment)
        self.env.installer = self.forge.create_mock(Installer)
        self.env.utils = self.forge.create_mock(EnvironmentUtils)

class SourceFromStringTest(ForgeTest):
    def setUp(self):
        super(SourceFromStringTest, self).setUp()
        self.S = sources.Source.from_anything
    def test__git(self):
        self.assertIsInstance(self.S("git://bla"), sources.Git)
    def test__path(self):
        filename = tempfile.mkdtemp()
        self.assertIsInstance(self.S(filename), sources.Path)
    def test__easy_install(self):
        self.assertIsInstance(self.S("blablabla"), sources.EasyInstall)
    def test__invalid_source(self):
        for invalid_value in [2, 2.5, True]:
            with self.assertRaises(ValueError):
                self.S(invalid_value)

class PathSourceTest(SourceTest):
    def setUp(self):
        super(PathSourceTest, self).setUp()
        self.path = tempfile.mkdtemp()
        self.source = sources.Path(self.path)
    def test__get_name(self):
        self.assertEquals(self.source.get_name(), self.path)
    def test__uses_expanduser(self):
        source = sources.Path("~/a/b/c")
        self.assertEquals(source._param, os.path.expanduser("~/a/b/c"))
    def test__get_signature(self):
        self.assertEquals(self.source.get_signature(), "Path({0})".format(self.path))
    def test__checkout(self):
        self.assertEquals(self.source.checkout(self.env), self.path)
        with self.assertRaises(NotImplementedError):
            self.source.checkout(self.env, '/another/path')
    def test__install(self):
        self.env.installer.install_unpacked_package(self.path)
        self.forge.replay()
        self.source.install(self.env)

class DelegateToPathInstallTest(SourceTest):
    def setUp(self):
        super(DelegateToPathInstallTest, self).setUp()
        self.path_class = self.forge.create_class_mock(sources.Path)
        self.orig_path_class = sources.Path
        self.forge.replace_with(sources, "Path", self.path_class)
    def expect_delegation_to_path_install(self, path):
        path_mock = self.forge.create_mock(self.orig_path_class)
        self.path_class(path).and_return(path_mock)
        return path_mock.install(self.env)

class GitSourceTest(DelegateToPathInstallTest):
    def setUp(self):
        super(GitSourceTest, self).setUp()
        self.repo_url = "some/repo/url"
        self.branch = 'some_branch'
        self.source = sources.Git(self.repo_url, self.branch)
        self.forge.replace(git, "clone_to_or_update")
    def test__master_is_default_branch(self):
        self.assertEquals(sources.Git('bla')._branch, 'master')
    def test__get_name(self):
        self.assertEquals(self.source.get_name(), self.repo_url + "@" + self.branch)
    def test__repr(self):
        self.assertEquals(repr(self.source), 'Git({})'.format(self.source.get_name()))
    def test__get_signature(self):
        self.assertEquals(self.source.get_signature(), repr(self.source))
    def test__git_source_install(self):
        self.forge.replace(self.source, "checkout")
        checkout_path = "some/checkout/path"
        self.source.checkout(self.env).and_return(checkout_path)
        self.expect_delegation_to_path_install(checkout_path)
        with self.forge.verified_replay_context():
            self.source.install(self.env)
    def test__git_source_checkout_with_path_argument(self):
        checkout_path = "/some/path/to/checkout"
        git.clone_to_or_update(url=self.repo_url, path=checkout_path, branch=self.branch)

        with self.forge.verified_replay_context():
            result = self.source.checkout(self.env, checkout_path)
        self.assertIs(result, checkout_path)
    def test__git_source_checkout_no_path_argument(self):
        checkout_path = "/some/path/to/checkout"
        checkout_cache = self.forge.create_mock(CheckoutCache)
        self.env.get_checkout_cache().and_return(checkout_cache)
        checkout_cache.get_checkout_path(self.repo_url).and_return(checkout_path)
        git.clone_to_or_update(url=self.repo_url, branch=self.branch, path=checkout_path)

        with self.forge.verified_replay_context():
            result = self.source.checkout(self.env)
        self.assertIs(result, checkout_path)
    def test__git_identifies_git_prefix(self):
        url = "git://bla"
        source = sources.Source.from_anything(url)
        self.assertIsInstance(source, sources.Git)

class ExternalToolSourceTest(SourceTest):
    def setUp(self):
        super(ExternalToolSourceTest, self).setUp()
        self.package_name = "some_package==1.0.0"
        self.forge.replace(command, "execute_assert_success")
class PIPSourceTest(ExternalToolSourceTest):
    def test__install(self):
        source = sources.PIP(self.package_name)
        self.env.execute_pip_install(self.package_name)
        with self.forge.verified_replay_context():
            source.install(self.env)
    def test__checkout_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            sources.PIP(self.package_name).checkout(self.env, '/some/path')
        with self.assertRaises(NotImplementedError):
            sources.PIP(self.package_name).checkout(self.env)
class EasyInstallSourceTest(ExternalToolSourceTest):
    def test__install(self):
        self.env.execute_easy_install(self.package_name)
        source = sources.EasyInstall(self.package_name)
        with self.forge.verified_replay_context():
            source.install(self.env)
    def test__checkout_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            sources.EasyInstall(self.package_name).checkout(self.env, '/some/path')
        with self.assertRaises(NotImplementedError):
            sources.EasyInstall(self.package_name).checkout(self.env)

class SCMTest(SourceTest):
    def test__git(self):
        repo = "git://some_repo"
        result = sources.SCM(repo)
        self.assertIsInstance(result, sources.Git)
        self.assertEquals(result._url, repo)
    def test__git_with_branch(self):
        result = sources.SCM("git://some_repo@branch_name")
        self.assertIsInstance(result, sources.Git)
        self.assertEquals(result._url, "git://some_repo")
        self.assertEquals(result._branch, "branch_name")
    def test__other(self):
        with self.assertRaises(ValueError):
            sources.SCM("bla")
