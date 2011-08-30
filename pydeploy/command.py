import errno
import logging
import subprocess
from .exceptions import CommandFailed
from .python3_compat import basestring

_logger = logging.getLogger("pydeploy.command")

def execute_assert_success(cmd, shell, cwd=None):
    _logger.debug("Running %r", cmd if isinstance(cmd, basestring) else " ".join(cmd))
    try:
        p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=shell, close_fds=True)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
        raise CommandFailed(cmd, errno.ENOENT, '')
    p.stdin.close()
    _logger.debug("pid: %r", p.pid)
    output = p.stdout.read()
    _logger.debug("Got Output:\n%s", output)
    result = p.wait()
    _logger.debug("Process returned %r", result)
    if result != 0:
        raise CommandFailed(cmd, result, output)
    return result, output

