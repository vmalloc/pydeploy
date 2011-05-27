from __future__ import absolute_import
import traceback
import argparse
import sys
import logging
from pydeploy.environment import Environment

parser = argparse.ArgumentParser()
parser.add_argument('-v', action='append_const', const=1, dest='verbose', default=[])
parser.add_argument("--pdb", action="store_true", default=False)
parser.add_argument("deployment_file")
parser.add_argument("dir")

_logger = logging.getLogger("pydeploy.main")

def main():
    args, remainder_argv = parser.parse_known_args()
    _configure_logging(args)
    env = Environment(args.dir, remainder_argv)
    env.create_and_activate()
    try:
        if args.deployment_file == '-':
            env.execute_deployment_stdin()
        else:
            env.execute_deployment_file(args.deployment_file)
    except Exception, e:
        _display_error(e, sys.exc_info()[-1])
        if args.pdb:
            import pdb
            pdb.post_mortem(sys.exc_info()[-1])
        return -1
    return 0

def _display_error(e, tb):
    _logger.error("Error occurred while running deployment file:\n %r", e)
    _logger.debug("Call stack:\n%s", "".join(traceback.format_tb(tb)))

def _configure_logging(args):
    level = logging.ERROR
    verbosity_level = sum(args.verbose)
    if verbosity_level > 0:
        if verbosity_level == 1:
            level = logging.INFO
        else:
            level = logging.DEBUG
    logging.basicConfig(
        stream=sys.stderr,
        level=level,
        format="--> %(message)s"
        )
