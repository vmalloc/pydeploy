import tempfile
from test_cases import ForgeTest
from pydeploy.scm import git
from pydeploy import command

class GitTest(ForgeTest):
    def setUp(self):
        super(GitTest, self).setUp()
        self.forge.replace(command, "execute_assert_success")
        self.url = "some/url"
        self.path = "/some/path/"

class CloneOrUpdateTest(GitTest):
    def setUp(self):
        super(CloneOrUpdateTest, self).setUp()
        self.forge.replace(git, "update")
        self.forge.replace(git, "clone_to")
    def test__clone_or_update_path_exists(self):
        path = tempfile.gettempdir()
        git.update(self.url, path)
        with self.forge.verified_replay_context():
            git.clone_to_or_update(self.url, path)
    def test__clone_or_update_path_does_not_exist(self):
        git.clone_to(self.url, self.path)
        with self.forge.verified_replay_context():
            git.clone_to_or_update(self.url, self.path)

class UpdateTest(GitTest):
    def test__update(self):
        command.execute_assert_success("git fetch {0}".format(self.url), cwd=self.path, shell=True)
        command.execute_assert_success("git reset --hard FETCH_HEAD && git clean -fdx", cwd=self.path, shell=True)
        with self.forge.verified_replay_context():
            git.update(self.url, self.path)
class CloneToTest(GitTest):
    def test__clone_to(self):
        command.execute_assert_success("git clone {0} {1}".format(self.url, self.path), shell=True)
        with self.forge.verified_replay_context():
            git.clone_to(self.url, self.path)
