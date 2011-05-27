import subprocess
import logging
from .exceptions import CommandFailed

_logger = logging.getLogger("pydeploy.execute")
def execute(cmd, **kwargs):
    if 'stdout' not in kwargs and 'stderr' not in kwargs:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.STDOUT
    _logger.debug("Running %r", cmd if isinstance(cmd, basestring) else " ".join(cmd))
    p = subprocess.Popen(cmd, **kwargs)
    if p.stdout is not None:
        stdout = p.stdout.read()
        _logger.debug("Got Output:\n%s", stdout)
    result = p.wait()
    _logger.debug("Process returned %r", result)
    return p

def execute_assert_success(cmd, **kwargs):
    p = execute(cmd, **kwargs)
    if 0 != p.returncode:
        raise CommandFailed("Command {0!r} failed!".format(cmd))
