import subprocess
import logging
from .exceptions import CommandFailed

_logger = logging.getLogger("pydeploy.execute")
def execute_assert_success(cmd, **kwargs):
    result, output = _execute(cmd, **kwargs)
    if 0 != result:
        raise CommandFailed(cmd, result, output)
    return result

def execute(*args, **kwargs):
    result, output = _execute(*args, **kwargs)[0]
    return result

def _execute(cmd, cwd=None, shell=True):
    _logger.debug("Running %r", cmd if isinstance(cmd, basestring) else " ".join(cmd))
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=shell, close_fds=True)
    p.stdin.close()
    _logger.debug("pid: %r", p.pid)
    output = p.stdout.read()
    _logger.debug("Got Output:\n%s", output)
    result = p.wait()
    _logger.debug("Process returned %r", result)
    return result, output
