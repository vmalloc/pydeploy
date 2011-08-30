from forge import Forge
from forge import Anything
import unittest
from pydeploy import command

class CommandTest(unittest.TestCase):
    def test__command_success(self):
        result, output = command.execute_assert_success("echo hello", shell=True)
        self.assertEquals(result, 0)
        self.assertEquals(output.rstrip().decode('utf-8'), "hello")
    def test__command_no_shell(self):
        with self.assertRaises(command.CommandFailed):
            command.execute_assert_success("echo hello", shell=False)
    def test__command_propagate_non_enoent(self):
        self.forge = Forge()
        self.forge.replace(command.subprocess, "Popen")
        self.addCleanup(self.forge.restore_all_replacements)
        expected_code = 23232
        command.subprocess.Popen(
            Anything(), cwd=Anything(), shell=True, close_fds=True,
            stdout=Anything(), stderr=command.subprocess.STDOUT, stdin=Anything()
            ).and_raise(OSError(expected_code, "message"))
        with self.forge.verified_replay_context():
            with self.assertRaises(OSError) as caught:
                command.execute_assert_success("bla", shell=True)
        self.assertIsInstance(caught.exception, OSError)
        self.assertEquals(caught.exception.errno, expected_code)
    def test__command_cwd(self):
        result, output = command.execute_assert_success("pwd", shell=True, cwd="/")
        self.assertEquals(output.rstrip(), "/".encode('utf-8'))
        self.assertEquals(result, 0)
    def test__command_failure(self):
        cmd = "echo bla > /dev/stderr; false"
        with self.assertRaises(command.CommandFailed) as caught:
            command.execute_assert_success(cmd, shell=True)
        self.assertEquals(caught.exception.output.rstrip(), "bla".encode('utf-8'))
        self.assertEquals(caught.exception.returncode, 1)
        exception_repr = repr(caught.exception)
        self.assertIn("returncode: 1", exception_repr)
        self.assertIn(repr(cmd), exception_repr)
        self.assertIn("output: 'bla", exception_repr)
