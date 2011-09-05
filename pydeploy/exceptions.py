from .python3_compat import make_str

class DeploymentException(Exception):
    pass

class RequiredVersionNotFound(Exception):
    pass

class CommandFailed(DeploymentException):
    def __init__(self, cmd, returncode, output):
        super(CommandFailed, self).__init__()
        self.cmd = cmd
        self.returncode = returncode
        self.output = output
    def __repr__(self):
        return "CommandFailed:\n  command: {!r}\n  returncode: {}\n  output: {!r})".format(self.cmd, self.returncode, make_str(self.output))
    def __str__(self):
        return repr(self)
