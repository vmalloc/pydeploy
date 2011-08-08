from __future__ import absolute_import
import traceback
import argparse
import os
import sys
import logging
from pydeploy.environment import Environment, GlobalEnvironment

_logger = logging.getLogger("pydeploy.main")

def main():
    args, remainder_argv = parser.parse_known_args()
    _configure_logging(args)
    if args.virtualenv_path is None:
        env = GlobalEnvironment(remainder_argv)
    else:
        env = Environment(args.virtualenv_path, remainder_argv)
    env.create_and_activate()
    try:
        args.func(env, args)
    except Exception, e:
        _display_error(e, sys.exc_info()[-1])
        if args.pdb:
            import pdb
            pdb.post_mortem(sys.exc_info()[-1])
        return -1
    return 0

def _run_deployment_file(env, args):
    if args.deployment_file == '-':
        env.execute_deployment_stdin()
    else:
        env.execute_deployment_file(os.path.expanduser(args.deployment_file))

def _install_source(env, args):
    env.install(args.source)

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

parser = argparse.ArgumentParser()
parser.add_argument('-v', action='append_const', const=1, dest='verbose', default=[])
parser.add_argument("--pdb", action="store_true", default=False)

subparsers = parser.add_subparsers(help="sub-command help")

run_parser = subparsers.add_parser("run")
run_parser.set_defaults(func=_run_deployment_file)
run_parser.add_argument("deployment_file")
run_parser.add_argument("--env", dest="virtualenv_path", default=None)

install_parser = subparsers.add_parser("install")
install_parser.set_defaults(func=_install_source)
install_parser.add_argument("source")
install_parser.add_argument("--env", dest="virtualenv_path", default=None)
