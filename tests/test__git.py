import tempfile
from .test_cases import ForgeTest
from pydeploy.scm import git
from pydeploy import command

class GitTest(ForgeTest):
    def setUp(self):
        super(GitTest, self).setUp()
        self.forge.replace(command, "execute_assert_success")
        self.url = "some/url"
        self.path = "/some/path/"
        self.branch = "some_branch"

class CloneOrUpdateTest(GitTest):
    def setUp(self):
        super(CloneOrUpdateTest, self).setUp()
        self.forge.replace(git, "update")
        self.forge.replace(git, "clone_to")
    def test__clone_or_update_path_exists(self):
        path = tempfile.gettempdir()
        git.update(self.url, self.branch, path)
        with self.forge.verified_replay_context():
            git.clone_to_or_update(self.url, self.branch, path)
    def test__clone_or_update_path_does_not_exist(self):
        git.clone_to(self.url, self.branch, self.path)
        with self.forge.verified_replay_context():
            git.clone_to_or_update(self.url, self.branch, self.path)

class UpdateTest(GitTest):
    def test__update(self):
        command.execute_assert_success("git fetch {0} {1}".format(self.url, self.branch), cwd=self.path, shell=True)
        command.execute_assert_success("git reset --hard FETCH_HEAD && git clean -fdx", cwd=self.path, shell=True)
        with self.forge.verified_replay_context():
            git.update(self.url, self.branch, self.path)
class CloneToTest(GitTest):
    def test__clone_to(self):
        command.execute_assert_success("git clone -b {0} {1} {2}".format(self.branch, self.url, self.path), shell=True)
        with self.forge.verified_replay_context():
            git.clone_to(self.url, self.branch, self.path)

class RemoteReferencesTest(GitTest):
    def test__remote_references(self):
        command.execute_assert_success("git ls-remote {0}".format(self.url), shell=True).and_return((0, """\
ccd9dc4f0775c442ede15db26c26c02a766cf1a	HEAD
4ccd9dc4f0775c442ede15db26c26c02a766cf1a	refs/heads/master
bee1140b66c0ca1cb788e52697b7fb66ecb650bd        some_symlink -> blap
bee1140b66c0ca1cb788e52697b7fb66ecb650bd	refs/tags/v0.0.1
"""))
        self.forge.replay()
        result = git.get_remote_references_dict(self.url)
        self.assertIsInstance(result, dict)
        refs = sorted(result)
        self.assertEquals(len(refs), 2)
        self.assertIsInstance(refs[0], git.Branch)
        self.assertEquals(refs[0], 'master')
        self.assertEquals(result['master'], "4ccd9dc4f0775c442ede15db26c26c02a766cf1a")
        self.assertEquals(refs[0].to_ref_name(), 'master')
        self.assertIsInstance(refs[1], git.Tag)
        self.assertEquals(refs[1], 'v0.0.1')
        self.assertEquals(refs[1].to_ref_name(), 'tags/v0.0.1')
        self.assertEquals(result['v0.0.1'], "bee1140b66c0ca1cb788e52697b7fb66ecb650bd")
