import subprocess
from .exceptions import CommandFailed

def execute_assert_success(cmd, **kwargs):
    p = subprocess.Popen(cmd, **kwargs)
    if 0 != p.wait():
        raise CommandFailed("Command {0!r} failed!".format(cmd))
